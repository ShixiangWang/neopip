from prepare import conda_envs
import subprocess
import os


conda_base = conda_envs("~/.neopip/miniconda", "base")
print(conda_base.env_location)
print(conda_base.activate_cmd)
print(conda_base.deactivate_cmd)
print(conda_base.conda)

conda_py27 = conda_envs("~/.neopip/miniconda", "py27")
print(conda_py27.env_location)
print(conda_py27.activate_cmd)
print(conda_py27.deactivate_cmd)

os.system("echo Hello; echo world!")