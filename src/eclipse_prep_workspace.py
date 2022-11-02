#!/usr/bin/python

"""
this script will create a workspace where eclipse can be launched
this script also maximizes the eclipse window using the technique
described in:
http://unix.stackexchange.com/questions/103602/how-to-maximize-a-window-programmably-in-x-window
"""

import shutil
import os
import os.path
import subprocess
import sys

# project
project = os.getcwd().split("/")[-1]
# where to put the workspace
folder = os.path.expanduser(f"~/shared_archive/workspaces/{project}")
# where is the eclipse to run
eclipse = os.path.expanduser("~/install/eclipse-jee/eclipse")
# remove and recreate the workspace everytime?
remove_and_recreate = True
# debug the script?
debug = False
# report progress?
do_progress = True
# do import?
do_import = True


def progress(msg):
    if do_progress:
        print(msg, file=sys.stderr)


if remove_and_recreate:
    # remove the old folder
    if os.path.isdir(folder):
        progress(f"removing the old folder ([{folder}])")
        shutil.rmtree(folder)
    # create the new folder
    progress("making the new folder ([{folder}])")
    os.mkdir(folder)

if do_import:
    progress("running headless eclipse to import the project")
    subprocess.check_call(
        [
            eclipse,
            "-nosplash",
            "-data",
            folder,
            "-application",
            "org.eclipse.cdt.managedbuilder.core.headlessbuild",
            "-import",
            ".",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

progress(f"eclipse workspace is ready ([{format}])")
