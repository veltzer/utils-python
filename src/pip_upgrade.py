#!/usr/bin/python

"""
This script upgrades just one pip module.

It is very useful if you have a ton of repos and want to upgrade some module in all of them.
"""

import sys
import subprocess
from pkg_resources import get_distribution, DistributionNotFound


def upgrade_module(module_name):
    try:
        module_dist = get_distribution(module_name)
        print(f"{module_name} version {module_dist.version} is installed.")
    except DistributionNotFound:
        print(f"{module_name} is not installed, skipping upgrade.")
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", module_name])
        print(f"{module_name} has been upgraded.")
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading {module_name}: {e}")


if len(sys.argv) != 2:
    print("usage: pip_upgrade [module_name]", file=sys.stderr)
    sys.exit(1)
upgrade_module(sys.argv[1])
