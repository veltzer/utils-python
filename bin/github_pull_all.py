#!/usr/bin/python3

"""
This script pulls all the projects from a github account.

NOTES:
- this script should be python2 because it relies on the github module which
is python2 only

TODO:
- remove the username and password from this script.
"""

import glob  # for glob
import os.path  # for split, join, isfile, expanduser
import os  # for chdir
import subprocess  # for check_call
import configparser  # for ConfigParser
import github  # for Github

inifile = os.path.expanduser("~/.github.ini")
config = configparser.ConfigParser()
config.read(inifile)
opt_login = config.get("github", "login")
opt_pass = config.get("github", "pass")
g = github.Github(opt_login, opt_pass)

done = set()
for repo in g.get_user().get_repos():
    folder = repo.name
    project = folder
    if os.path.isdir(folder):
        if not os.path.isfile(os.path.join(folder, ".skip")):
            print(f"project [{project}] exists, pulling it...")
            os.chdir(folder)
            subprocess.check_call(
                [
                    "git",
                    "pull",
                    #'--tags',
                ]
            )
            os.chdir("..")
        else:
            print(f"project [{project}] exists, skipping it because of .skip file...")
    else:
        print(f"project [{project}] does not exists, cloning it...")
        # print(dir(repo))
        subprocess.check_call(
            [
                "git",
                "clone",
                repo.clone_url,
            ]
        )
    done.add(folder)

for gitfolder in glob.glob("*/.git"):
    folder = os.path.split(gitfolder)[0]
    if not folder in done:
        project = folder
        if not os.path.isfile(os.path.join(folder, ".skip")):
            print(f"doing non-github project [{project}]")
            os.chdir(folder)
            subprocess.check_call(
                [
                    "git",
                    "pull",
                    #'--tags',
                ]
            )
            os.chdir("..")
        else:
            print(f"skipping non-github project [{project}]")
