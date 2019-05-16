import os
import sys
import argparse
from classes import conda_envs
from prepare import miniconda_loc, py27_env

'''
A conda command wrapper for managing custom conda environments based on python2 or python3
'''

def main(command, use_py3):
    if use_py3:
        envs = conda_envs(miniconda_loc, "base")
    else:
        envs = conda_envs(miniconda_loc, py27_env)
 
    if command == "activate":
        os.system(envs.activate_cmd)
    elif command == "deactivate":
        os.system(envs.deactivate_cmd)
    else:
        print("Bad commad!")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="Conda command, use activate or deactivate")
    parser.add_argument("--python3", action="store_true", help="If specified, use python3 conda environment")
    args = parser.parse_args()
    main(args.command, args.python3)