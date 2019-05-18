#!/usr/bin/env python3
import sys
import os
import yaml
import argparse
import logging
from os.path import expanduser, join
from classes import conda_envs

"""Prepare softwares and corresponding dependencies for neoantigen prediction"""
# Reference: 
# https://github.com/ShixiangWang/Variants2Neoantigen
# https://github.com/griffithlab/docker-pvactools/blob/master/Dockerfile
# https://pvactools.readthedocs.io/en/latest/pvacseq/input_file_prep/vep.html
# https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97

__author__ = "Shixiang Wang"
__email__ = "wangshx@shanghaitech.edu.cn"
__prediction_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"
__pvactools_version__ = __prediction_version__[:5]
__mhc_i_version__ = __prediction_version__[11:17]
__mhc_ii_version__ = __prediction_version__[-6:]
#MHCFLURRY_DOWNLOADS_CURRENT_RELEASE=1.2.0
#tensorflow=1.5.0

# Global setting
# Read configuration from yaml file
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.BaseLoader)
home = expanduser(config['prepare']['home'])

if home is not None:
    neopip_loc = home
    miniconda_loc = join(home, config['prepare']['miniconda'])
    vep_loc = join(home, config['prepare']['vep'])
else:
    neopip_loc = expanduser(config['prepare']['neopip'])
    miniconda_loc = expanduser(config['prepare']['miniconda'])
    vep_loc = expanduser(config['prepare']['vep'])

py27_env=config['prepare']['py27_env']
logfile=config['prepare']['logfile']

this_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def execute(s, sep = " "):
    os.system('bash -c "' + sep.join(s) + '"')


def main(neopip_loc=".neopip", miniconda_loc=".neopip/miniconda", vep_loc = ".neopip/vep", py27_env="py27", logfile="/tmp/prepare.log"):

    # Set logging level and format
    datefmt = '%Y/%m/%d %H:%M:%S'
    logfmt = '[%(asctime)s - %(levelname)s - %(filename)s]: %(message)s'
    logging.basicConfig(level=logging.DEBUG, 
                        filename=logfile,
                        datefmt=datefmt,
                        format=logfmt)
    logger = logging.getLogger(__name__)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level=logging.INFO)
    #stream_handler.setFormatter(logging.Formatter(fmt=logfmt, datefmt=datefmt))
    logger.addHandler(stream_handler)

    # Preface
    logger.info("========================================================================")
    logger.info("Prepare conda environments, softwares and data for neoantigen prediction")
    logger.info("========================================================================")
    logger.info("Author  : %s"%__author__)
    logger.info("Email   : %s"%__email__)
    logger.info("Version : %s"%__prediction_version__)
    logger.info("========================================================================")
    logger.info("Except VEP data will be stored at %s,"%vep_loc)
    logger.info("    all others will put into %s"%neopip_loc)
    logger.info("Custom conda path is %s"%miniconda_loc)
    logger.info("")
    logger.info("Prepare process is starting, log info will output to %s", logfile)
    logger.info("")
    logger.info("Enjoy it!")
    logger.info("========================================================================")
    
    # Create base directory
    if not os.path.isdir(neopip_loc):
        os.system("mkdir -p %s"%neopip_loc)

    # Install miniconda
    logger.info("> Download miniconda to /tmp")
    try:
        execute(["wget", "-c", "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh", "-O", "/tmp/miniconda.sh"])
    except Exception:
        logger.error("Failed to download miniconda, please check your network", exc_info=True)
        sys.exit()

    logger.info("> Start Installing miniconda to %s", miniconda_loc)
    try:
        execute(["sh",  "/tmp/miniconda.sh", "-b", "-p", miniconda_loc])
    except Exception:
        logger.error("Error occured in installation process", exc_info=True)
        #sys.exit()
    
    envs_py27 = conda_envs(miniconda_loc, py27_env)
    envs_py3 = conda_envs(miniconda_loc, "base")

    # Create conda environments for python 2.7 and
    # install softwares based on python 2.7
    logger.info("> Create python 2.7 environment %s", envs_py27.env_location)
    try:
        execute([envs_py27.conda, "create", "-p", envs_py27.env_location, "python=2.7", "biopython", "-y"])
    except Exception:
        logger.error("Fail to create the environment", exc_info=True)
        sys.exit()
   
   # Copy data ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz and iedb
   # See:
   #    https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97
   #    https://github.com/ShixiangWang/Variants2Neoantigen
   
    data_dir = "%s/data" % neopip_loc
    if not os.path.isdir(data_dir):
        os.system("mkdir -p %s" % data_dir)
    
    logger.info("> Copy data files from neopip to %s data subdirectory"%neopip_loc)
    os.system("cp -r %s/* %s" %(os.path.join(this_dir, "data"), data_dir))

    # Install vep & vcf2maf on python 3 environment
    # https://bioconda.github.io/recipes/ensembl-vep/README.html
    logger.info("> Install ensembl-vep vcf2maf samtools bcftools ucsc-liftover blast")
    cmds = [envs_py3.activate_cmd,  "conda install -c bioconda ensembl-vep vcf2maf samtools bcftools ucsc-liftover blast -y", envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    logger.info(">>> Copy ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz* to %s"%vep_loc)
    if not os.path.isdir(vep_loc):
        os.system("mkdir -p %s"%vep_loc)
    os.system("cp {0}/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz* {1}".format(data_dir, vep_loc))

    # IEDB softwares
    iedb_dir = "%s/iedb" % neopip_loc
    if not os.path.isdir(iedb_dir):
        os.system("mkdir -p %s" % iedb_dir)
    # IEDB MHC I 
    logger.info("> Download and install IEDB MHC I  %s" %__mhc_i_version__)
    cmds = [envs_py27.activate_cmd, "wget -c https://downloads.iedb.org/tools/mhci/{0}/IEDB_MHC_I-{0}.tar.gz -O /tmp/IEDB_MHC_I.tar.gz".format(__mhc_i_version__),
            "tar zxf /tmp/IEDB_MHC_I.tar.gz -C %s"%iedb_dir, "cd %s/mhc_i"%iedb_dir, "./configure", envs_py27.deactivate_cmd]
    execute(cmds, sep = " && ")

    # IEDB MHC II 
    # QA: Perl script can't locate Env.pm in @INC - yum install perl-Env
    logger.info("> Download and install IEDB MHC II %s" %__mhc_ii_version__)
    cmds = [envs_py27.activate_cmd, "wget -c https://downloads.iedb.org/tools/mhcii/{0}/IEDB_MHC_II-{0}.tar.gz -O /tmp/IEDB_MHC_II.tar.gz".format(__mhc_ii_version__),
            "tar zxf /tmp/IEDB_MHC_II.tar.gz -C %s"%iedb_dir, "cd %s/mhc_ii"%iedb_dir, "%s/bin/python configure.py"%envs_py27.env_location, envs_py27.deactivate_cmd]
    execute(cmds, sep = " && ")

    
    # Install pvactools
    logger.info("> Install pvactools %s"%__pvactools_version__)
    cmds = [envs_py3.activate_cmd, "conda install tensorflow=1.5.0 -y", envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    cmds = [envs_py3.activate_cmd, "pip install pvactools==%s"%__pvactools_version__, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")

    
    mhcflurry_dir = "%s/data/mhcflurry_data" %neopip_loc
    logger.info(">>> Download mhcflurry data to %s" %mhcflurry_dir)
    if not os.path.isdir(mhcflurry_dir):
        os.system("mkdir -p %s" % mhcflurry_dir)

    # Set data of mhcflurry to custom directory (is this good for analysis?)
    cmds = [envs_py3.activate_cmd, "export MHCFLURRY_DOWNLOADS_CURRENT_RELEASE=1.2.0", 
            "export MHCFLURRY_DATA_DIR=%s"%mhcflurry_dir, "mhcflurry-downloads fetch", envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")

    logger.info(">>> Download pvacseq example data to %s" %data_dir)
    cmds = [envs_py3.activate_cmd, "pvacseq download_example_data %s"%data_dir , envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")

    logger.info(">>> Download and install VEP plugins to %s" %vep_loc)
    cmds = [envs_py3.activate_cmd, "cd %s"%vep_loc, "git clone https://github.com/Ensembl/VEP_plugins.git",
            "pvacseq install_vep_plugin %s/VEP_plugins"%vep_loc, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    
    logger.info("> Neoantigen prediction prepare process finished!")


if __name__ == "__main__":
    main(neopip_loc=neopip_loc, miniconda_loc=miniconda_loc, vep_loc=vep_loc,
        py27_env=py27_env, logfile=logfile)
