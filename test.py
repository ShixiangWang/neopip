from prepare import conda_envs
import subprocess
import os
import sys
from os.path import expanduser
import argparse


print(os.environ['ahh'])

sys.exit()


conda_base = conda_envs("~/.neopip/miniconda", "base")
print(conda_base.env_location)
print(conda_base.activate_cmd)
print(conda_base.deactivate_cmd)
print(conda_base.conda)

conda_py27 = conda_envs("~/.neopip/miniconda", "py27")
print(conda_py27.env_location)
print(conda_py27.activate_cmd)
print(conda_py27.deactivate_cmd)

ac_msg = os.system("echo Hello; echo world!")
print(ac_msg)
ac_msg = subprocess.check_output("echo Hello; echo world!", shell = True)
print(ac_msg.decode('utf8'))

__prediction_version__ = "1.3.7_mhci_2.19.1_mhcii_2.17.5"
__pvactools_version__ = __prediction_version__[:5]
__mhc_i_version__ = __prediction_version__[11:17]
__mhc_ii_version__ = __prediction_version__[-6:]

print(__pvactools_version__)
print(__mhc_i_version__)
print(__mhc_ii_version__)

#home = sys.argv[1]
#print(home)

# print(expanduser(home))

# neopip_loc="%s/.neopip" %home
# miniconda_loc="%s/.neopip/miniconda" %home
# vep_loc="%s/.neopip/vep" %home
# py27_env="py27"
# logfile="/tmp/prepare.log"


def main():
    print("Yes")

if __name__ == "__main__":
    main()