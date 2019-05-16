import sys
import os
import logging
from os.path import expanduser

"""Prepare softwares and corresponding dependencies for neoantigen prediction"""

__author__ = "Shixiang Wang"
__email__ = "w_shixiang@163.com"
__pvactools_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"

home = expanduser("~")
neopip_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def execute(s, sep = " "):
    os.system(sep.join(s))

class conda_envs():
    def __init__(self, path, env):
        '''
        path: path to installed miniconda
        env : name of conda environment

        Note, all environments (except base) must be installed in envs subdirectory
        '''
        self.conda_location = path
        if env == "base":
            self.env_location = self.conda_location
        else:
            self.env_location = "{0}/envs/{1}".format(path, env)
        self.conda = "{0}/bin/conda".format(self.conda_location)
        self.activate_cmd = "source {0}/bin/activate {1}".format(path, self.env_location)
        self.deactivate_cmd = "source {0}/bin/deactivate".format(path)


def predict_prepare(neopip_loc="%s/.neopip" %home, miniconda_loc="%s/.neopip/miniconda" %home,
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

    # Install pvactools
    cmds = [envs_py3.activate_cmd, "%s install tensorflow=1.5.0 -y"%envs_py3.conda, envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
    cmds = [envs_py3.activate_cmd,  "pip install pvactools", envs_py3.deactivate_cmd]
    execute(cmds, sep = " && ")
   
   # Copy data ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz and iedb
   # See:
   #    https://gist.github.com/ckandoth/5390e3ae4ecf182fa92f6318cfa9fa97
   #    https://github.com/ShixiangWang/Variants2Neoantigen
   
    data_dir = "%s/data" % neopip_loc
    os.system("mkdir -p %s" % data_dir)
    os.system("cp -r %s/* %s" %(os.path.join(neopip_dir, "data"), data_dir))
   
    logger.info("Neoantigen prediction prepare process finished!")


if __name__ == "__main__":
    predict_prepare()
