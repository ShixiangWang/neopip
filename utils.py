from os.path import join, expanduser
from shutil import which
import os

def create_dir(*path):
    dir = expanduser(join(*path))
    if not os.path.isdir(dir):
        os.makedirs(dir)
    return(dir)

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None