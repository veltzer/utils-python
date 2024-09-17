#!/usr/bin/python

"""
This script upgrades just one pip module.

It is very useful if you have a ton of repos and want to upgrade some module in all of them.
"""

import sys
import subprocess
import importlib


def upgrade_module(module_name):
    try:
        importlib.import_module(module_name)
        # module_version = module.__version__
        print(f"{module_name} is installed.")
    except ImportError:
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
