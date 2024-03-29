#!/usr/bin/python

"""
This script uses git to clean all of my projects.
"""

import os
import os.path
import subprocess

home = os.getenv("HOME")
assert home is not None

projects = []
filename = os.path.expanduser("~/.mrconfig")
with open(filename) as f:
    for line_b in f:
        line = line_b.rstrip()
        if line.startswith("["):
            project_root = os.path.join(home, line[1:-1])
            project_name = line[1:-1].split("/")[-1]
            projects.append((project_name, project_root))

# projects=[(repo.name, os.path.join(home,'git',repo.name)) for repo in utils.github.get_nonforked_repos_list()]

for project_name, project_root in projects:
    print(f"cleaning [{project_name}] at [{project_root}]...", end="")
    if os.path.isdir(project_root):
        os.chdir(project_root)
        subprocess.check_call(["git", "clean", "-qffxd"])
        print("OK")
    else:
        print("NOT FOUND")
