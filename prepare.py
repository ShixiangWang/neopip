#!/usr/bin/env python3
import sys
import os
import yaml
import logging
from os.path import expanduser, join
from subprocess import run, PIPE
from utils import create_dir, is_tool

"""Prepare softwares and corresponding dependencies for neoantigen prediction"""
# Reference: 
# https://github.com/ShixiangWang/Variants2Neoantigen
# https://github.com/griffithlab/docker-pvactools/blob/master/Dockerfile
# https://pvactools.readthedocs.io/en/latest/pvacseq/input_file_prep/vep.html
# https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97

__author__ = "Shixiang Wang"
__email__ = "wangshx@shanghaitech.edu.cn"
__prediction_version__ = "1.4.0_mhci_2.19.1_mhcii_2.17.5"
__pvactools_version__ = __prediction_version__[:5]
__mhc_i_version__ = __prediction_version__[11:17]
__mhc_ii_version__ = __prediction_version__[-6:]
#MHCFLURRY_DOWNLOADS_CURRENT_RELEASE=1.2.0
#tensorflow=1.5.0

# Global setting
# Read configuration from yaml file
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.BaseLoader)
home = expanduser(config['prepare']['home']) if config['prepare']['home'] != 'null' else None
 
if home is not None:
    neopip_loc = home
    conda_loc = join(home, config['prepare']['conda']['path'])
    vep_loc = join(home, config['prepare']['vep'])
else:
    neopip_loc = expanduser(config['prepare']['neopip'])
    conda_loc = expanduser(config['prepare']['conda']['path'])
    vep_loc = expanduser(config['prepare']['vep'])

env_name = config['prepare']['conda']['env_name']
logfile=config['prepare']['logfile']

this_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def main(neopip_loc=".neopip", conda_loc=".neopip/miniconda", vep_loc = ".neopip/vep", env_name="py27", logfile="/tmp/prepare.log"):

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
    logger.info("Author  : %s", __author__)
    logger.info("Email   : %s", __email__)
    logger.info("Version : %s", __prediction_version__)
    logger.info("========================================================================")
    logger.info("Except VEP data will be stored at %s,", vep_loc)
    logger.info("    all others will put into %s", neopip_loc)
    logger.info("Conda environment name is %s", env_name)
    logger.info("")
    logger.info("Prepare process is starting, log info will output to %s", logfile)
    logger.info("")
    logger.info("Enjoy it!")
    logger.info("========================================================================")
    
    # Create base directory
    create_dir(neopip_loc)

    # Check conda and install environments
    if not is_tool("conda"):
        logger.info("> Conda does not exist")
        logger.info("> Download miniconda...")
        run("wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh", check=True, shell=True)

        logger.info("> Start Installing miniconda to %s", conda_loc)
        run("sh /tmp/miniconda.sh -b -p %s"%conda_loc, shell=True)
        logger.info("> Activate conda...")
        # use bash
        run("eval \"$({}/bin/conda shell.bash hook)\" && conda init bash".format(conda_loc), check=True, shell=True)
    else:
        logger.info("> Conda has already installed, skipping...")
        run("conda init bash", check=True, shell=True)
    # Create conda environments pvactools_py27
    logger.info("> Create pvactools_py27 environment")
    run("conda create -n pvactools_py27 python=2.7 biopython pyyaml -y", check=True, shell=True)
   
   # Copy data ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz and iedb
   # See:
   #    https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97
   #    https://github.com/ShixiangWang/Variants2Neoantigen
   
    data_dir = create_dir(neopip_loc, "data")
    
    logger.info("> Copy data files from neopip to %s data subdirectory"%neopip_loc)
    run("cp -r %s/* %s" %(join(this_dir, "data"), data_dir), check=True, shell=True)

    # Install vep & vcf2maf on python 3 environment
    # https://bioconda.github.io/recipes/ensembl-vep/README.html
    logger.info("> Create neopip environment and install ensembl-vep vcf2maf samtools bcftools ucsc-liftover blast")
    run(" -y".format(env_name), check=True, shell=True)
    run("conda create -n {} -c bioconda python=3 ensembl-vep vcf2maf samtools bcftools ucsc-liftover blast -y".format(env_name), check=True, shell=True)
    logger.info(">>> Copy ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz* to %s"%vep_loc)
    create_dir(vep_loc)
    run("cp {0}/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz* {1}".format(data_dir, vep_loc), check=True, shell=True)

    # IEDB softwares
    iedb_dir = create_dir(neopip_loc, "iedb")
    # IEDB MHC I 
    logger.info("> Download and install IEDB MHC I  %s" %__mhc_i_version__)
    run("conda activate pvactools_py27 && wget -c https://downloads.iedb.org/tools/mhci/{0}/IEDB_MHC_I-{0}.tar.gz -O /tmp/IEDB_MHC_I.tar.gz && tar zxf /tmp/IEDB_MHC_I.tar.gz -C {1} && cd {1}/mhc_i && ./configure".format(__mhc_i_version__, iedb_dir), check=True, shell=True)

    # IEDB MHC II 
    # QA: Perl script can't locate Env.pm in @INC - yum install perl-Env
    logger.info("> Download and install IEDB MHC II %s" %__mhc_ii_version__)
    run("conda activate pvactools_py27 && wget -c https://downloads.iedb.org/tools/mhcii/{0}/IEDB_MHC_II-{0}.tar.gz -O /tmp/IEDB_MHC_II.tar.gz && tar zxf /tmp/IEDB_MHC_II.tar.gz -C {1} && cd {1}/mhc_ii && python configure.py".format(__mhc_ii_version__, iedb_dir), check=True, shell=True)

    # Install pvactools
    logger.info("> Install pvactools {0} and download example data to {1}".format(__pvactools_version__, data_dir))
    run("conda activate {0} && pip install pvactools=={1} && pvacseq download_example_data {2}".format(env_name, __pvactools_version__, data_dir), check=True, shell=True)

    mhcflurry_dir = create_dir(neopip_loc, "data", "mhcflurry_data")
    logger.info(">>> Download mhcflurry data to %s" %mhcflurry_dir)

    # Set data of mhcflurry to custom directory (is this good for analysis?)
    run("conda activate {0} && export MHCFLURRY_DOWNLOADS_CURRENT_RELEASE=1.2.0 && export MHCFLURRY_DATA_DIR={1} && mhcflurry-downloads fetch".format(env_name, mhcflurry_dir), check=True, shell=True)

    logger.info(">>> Download and install VEP plugins to %s" %vep_loc)
    run("conda activate {0} && cd {1} && git clone https://github.com/Ensembl/VEP_plugins.git && pvacseq install_vep_plugin {1}/VEP_plugins".format(env_name, vep_loc), check=True, shell=True)
    
    logger.info("> Neoantigen prediction prepare process finished!")
    
if __name__ == "__main__":
    main(neopip_loc=neopip_loc, conda_loc=conda_loc, vep_loc=vep_loc,
        env_name=env_name, logfile=logfile)
