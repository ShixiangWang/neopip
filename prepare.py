import sys
import os
import logging
from os.path import expanduser

from classes import conda_envs

"""Prepare softwares and corresponding dependencies for neoantigen prediction"""
# Reference: https://github.com/griffithlab/docker-pvactools/blob/master/Dockerfile

__author__ = "Shixiang Wang"
__email__ = "w_shixiang@163.com"
__prediction_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"
__pvactools_version__ = __prediction_version__[:5]
__mhc_i_version__ = __prediction_version__[11:17]
__mhc_ii_version__ = __prediction_version__[-6:]

# Global setting
home = expanduser("~")
this_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

neopip_loc="%s/.neopip" %home
miniconda_loc="%s/.neopip/miniconda" %home
py27_env="py27"
logfile="/tmp/prepare.log"


def execute(s, sep = " "):
    os.system(sep.join(s))


def main(neopip_loc="%s/.neopip" %home, miniconda_loc="%s/.neopip/miniconda" %home,
            py27_env="py27", logfile="/tmp/prepare.log"):

    # Set logging level and format
    datefmt = '%Y/%m/%d %H:%M:%S'
    logfmt = '[%(asctime)s - %(levelname)s - %(filename)s]: %(message)s'
    logging.basicConfig(level=logging.INFO, 
                        filename=logfile,
                        datefmt=datefmt,
                        format=logfmt)
    logger = logging.getLogger(__name__)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level=logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(fmt=logfmt, datefmt=datefmt))
    logger.addHandler(stream_handler)

    # Create base directory
    logger.info("Create %s", neopip_loc)
    try:
        execute(["mkdir", "-p", neopip_loc])
    except Exception:
        logger.error("Failed to create directory %s", neopip_loc, exc_info=True)
        sys.exit()

    logger.info("Prepare process is starting, log info will output to %s", logfile)
    
    # Install miniconda
    logger.info("Download miniconda to /tmp")
    try:
        execute(["wget", "-c", "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh", "-O", "/tmp/miniconda.sh"])
    except Exception:
        logger.error("Failed to download miniconda, please check your network", exc_info=True)
        sys.exit()

    logger.info("Start Installing miniconda to %s", miniconda_loc)
    try:
        execute(["sh",  "/tmp/miniconda.sh", "-b", "-p", miniconda_loc])
    except Exception:
        logger.error("Error occured in installation process", exc_info=True)
        #sys.exit()
    
    envs_py27 = conda_envs(miniconda_loc, py27_env)
    envs_py3 = conda_envs(miniconda_loc, "base")

    # Create conda environments for python 2.7 and
    # install softwares based on python 2.7
    logger.info("Create python 2.7 environment %s", envs_py27.env_location)
    try:
        execute([envs_py27.conda, "create", "-p", envs_py27.env_location, "python=2.7", "biopython", "-y"])
    except Exception:
        logger.error("Fail to create the environment", exc_info=True)
        sys.exit()

    # Install vep and vcf2maf on python 3
    cmds = [envs_py3.activate_cmd,  "%s install -c bioconda ensembl-vep vcf2maf -y"%envs_py3.conda, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
   
   # Copy data ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz and iedb
   # See:
   #    https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97
   #    https://github.com/ShixiangWang/Variants2Neoantigen
   
    data_dir = "%s/data" % neopip_loc
    if not os.path.isdir(data_dir):
        logger.info("Data directory %s does not exist, create it" %data_dir)
        os.system("mkdir -p %s" % data_dir)
    
    logger.info("Copy data files from neopip to %s data subdirectory"%neopip_loc)
    os.system("cp -r %s/* %s" %(os.path.join(this_dir, "data"), data_dir))

    # IEDB softwares
    iedb_dir = "%s/iedb" % neopip_loc
    if not os.path.isdir(iedb_dir):
        logger.info("IEDB directory %s does not exist, create it" %iedb_dir)
        os.system("mkdir -p %s" % iedb_dir)
    # IEDB MHC I 
    logger.info("Download and install IEDB MHC I  %s" %__mhc_i_version__)
    cmds = [envs_py27.activate_cmd, "wget -c https://downloads.iedb.org/tools/mhci/{0}/IEDB_MHC_I-{0}.tar.gz -O /tmp/IEDB_MHC_I.tar.gz".format(__mhc_i_version__),
            "tar zxf /tmp/IEDB_MHC_I.tar.gz -C %s"%iedb_dir, "cd %s/mhc_i"%iedb_dir, "./configure", envs_py27.deactivate_cmd]
    execute(cmds, sep = " && ")

    # IEDB MHC II 
    logger.info("Download and install IEDB MHC II %s" %__mhc_ii_version__)
    cmds = [envs_py27.activate_cmd, "wget -c https://downloads.iedb.org/tools/mhcii/{0}/IEDB_MHC_II-{0}.tar.gz -O /tmp/IEDB_MHC_II.tar.gz".format(__mhc_ii_version__),
            "tar zxf /tmp/IEDB_MHC_II.tar.gz -C %s"%iedb_dir, "cd %s/mhc_ii"%iedb_dir, "python ./configure.py", envs_py27.deactivate_cmd]
    execute(cmds, sep = " && ")


    mhcflurry_dir = "%s/data/mhcflurry_data" % neopip_loc
    if not os.path.isdir(mhcflurry_dir):
        logger.info("mhcflurry data directory %s does not exist, create it" %mhcflurry_dir)
        os.system("mkdir -p %s" % mhcflurry_dir)
    
    # Install pvactools
    logger.info("Install pvactools %s"%__pvactools_version__)
    cmds = [envs_py3.activate_cmd, "%s install tensorflow=1.5.0 -y"%envs_py3.conda, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    cmds = [envs_py3.activate_cmd, "pip install pvactools==%s"%__pvactools_version__, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")

    # Set data of mhcflurry to custom directory (is this good for analysis?)
    cmds = [envs_py3.activate_cmd, "export MHCFLURRY_DOWNLOADS_CURRENT_RELEASE=1.2.0", 
            "export MHCFLURRY_DATA_DIR=%s"%mhcflurry_dir, "mhcflurry-downloads fetch", envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    logger.info("Neoantigen prediction prepare process finished!")


if __name__ == "__main__":
    main(neopip_loc=neopip_loc, miniconda_loc=miniconda_loc,
        py27_env=py27_env, logfile=logfile)
