#!/usr/bin/python3

import glob
import os
import os.path
import subprocess

for gitfolder in glob.glob("*/.git"):
    folder = os.path.split(gitfolder)[0]
    project = folder
    if not os.path.isfile(os.path.join(folder, ".skip")):
        print(f"doing [{project}]")
        os.chdir(folder)
        subprocess.check_call(
            [
                "git",
                "diff",
                "--name-only",
            ]
        )
        # the --short flag is no good, it doesn't tell you if you are ahead...
        out = subprocess.check_output(
            [
                "git",
                "status",
                # '--short',
            ]
        ).decode()
        for line in out.split("\n"):
            if line.find("ahead") != -1:
                print(line)
        os.chdir("..")
    else:
        print(f"skipping [{project}]")
