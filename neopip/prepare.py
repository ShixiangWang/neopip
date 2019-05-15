import sys
import logging
import subprocess
from os.path import expanduser
from os import system


"""Prepare softwares and corresponding dependencies for neoantigen prediction"""

__author__ = "Shixiang Wang"
__email__ = "w_shixiang@163.com"
__pvactools_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"

home = expanduser("~")

def execute(s):
    system(" ".join(s))
    return(0)

class conda_envs():
    def __init__(self, path, env):
        '''
        path: path to installed miniconda
        env : name of conda environment

        Note, all environments (except base) must be installed in envs subdirectory
        '''
        self.path = path
        if env == "base":
            self.env_location = self.path
        else:
            self.env_location = "{0}/envs/{1}".format(path, env)
        self.activate_cmd = "source {0}/bin/activate {1}".format(path, self.env_location)
        self.deactivate_cmd = "source {0}/bin/deactivate".format(path)


def prepare(neopip_loc="%s/.neopip" %home, miniconda_loc="%s/.neopip/miniconda" %home,
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
        #subprocess.call(["mkdir", "-p", neopip_loc])
        execute(["mkdir", "-p", neopip_loc])
    except Exception:
        logger.error("Failed to create directory %s", neopip_loc, exc_info=True)
        sys.exit()

    logger.info("Prepare process is starting, log info will output to %s", logfile)
    
    # Install miniconda
    logger.info("Download miniconda to /tmp")
    try:
        #subprocess.call(["wget", "-c", "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh", "-O", "/tmp/miniconda.sh"])
        execute(["wget", "-c", "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh", "-O", "/tmp/miniconda.sh"])
    except Exception:
        logger.error("Failed to download miniconda, please check your network", exc_info=True)
        sys.exit()

    logger.info("Start Installing miniconda to %s", miniconda_loc)
    try:
        #subprocess.call(["sh",  "/tmp/miniconda.sh", "-b", "-p", miniconda_loc])
        execute(["sh",  "/tmp/miniconda.sh", "-b", "-p", miniconda_loc])
    except Exception:
        logger.error("Error occured in installation process", exc_info=True)
        #sys.exit()
    
    # Create conda environments for python 2.7 and python 3
    envs_py27 = conda_envs(miniconda_loc, py27_env)
    logger.info("Create python 2.7 environment %s", envs_py27.path)
    try:
        #subprocess.call(["%s/bin/conda" %miniconda_loc, "create", "-p", py27_loc, "python=2.7", "biopython", "-y"])
        execute(["%s/bin/conda" %miniconda_loc, "create", "-p", py27_loc, "python=2.7", "biopython", "-y"])
    except Exception:
        logger.error("Fail to create the environment", exc_info=True)
        sys.exit()

    py3_loc = miniconda_loc
    execute("source %s/bin/activate")
    
   

if __name__ == "__main__":
    prepare()
