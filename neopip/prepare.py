
#!/usr/bin/env python

import sys
import logging
import subprocess

"""Prepare softwares and corresponding dependencies for neoantigen prediction"""

__author__ = "Shixiang Wang"
__email__ = "w_shixiang@163.com"
__pvactools_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"


def prepare(neopip_loc="$HOME/.neopip", miniconda_loc="$HOME/.neopip/miniconda",
            py27_env="py27", py3_env= "py3", logfile="/tmp/prepare.log"):

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
        subprocess.call(["mkdir", "-p", neopip_loc])
    except Exception:
        logger.error("Failed to create directory %s", neopip_loc, exc_info=True)

    logger.info("Prepare process is starting, log info will output to %s", logfile)
    

    # Install miniconda
    logger.info("Download miniconda to /tmp")
    try:
        subprocess.call("wget -c https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh")
    except Exception:
        logger.error("Failed to download miniconda, please check your network")

    logger.info("Start Installing miniconda to %s", miniconda_loc)
    try:
        subprocess.call(["sh ~/miniconda.sh -b -p", miniconda_loc])
    except Exception:
        logger.error("Error occured in installation process")
    
    # Create conda environments for python 2.7 and python 3
    logger.info("Create python 2.7 environment %s", py27_env)
    try:
        subprocess.call("%s/bin/conda" %miniconda_loc, "-p", py27_env, "python=2.7")
    except Exception:
        logger.error("Fail to create the environment")
    
    logger.info("Create python 3 environment %s", py3_env)
    try:
        subprocess.call("%s/bin/conda" %miniconda_loc, "-p", py3_env, "python=3")
    except Exception:
        logger.error("Fail to create the environment")

if __name__ == "__main__":
    prepare()