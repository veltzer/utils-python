#!/usr/bin/python

"""
This script prints repos which are not registered in mr.

It will first read the projects registered in ~/.mrconfig

TODO:
- make this script query github and bitbucket and do the
reverse check as well: that all the repos that I have
there are here too.
"""

import os.path


def add_folder(base, have_folder):
    for f in os.listdir(base):
        full = os.path.join(base, f)
        if os.path.isdir(full):
            have_folder.add(f)


def main():
    have_mrconfig = set()
    filename = os.path.expanduser("~/.mrconfig")
    with open(filename) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("["):
                project = line[1:-1].split("/")[-1]
                have_mrconfig.add(project)

    have_folder = set()
    add_folder(os.path.expanduser("~/git"), have_folder)
    # add_folder(os.path.expanduser('~/twiggle/git'), have_folder)

    if have_folder != have_mrconfig:
        print("in mrconfig and not found")
        print(have_mrconfig - have_folder)
        print("found in folder and not in mrconfig")
        print(have_folder - have_mrconfig)
        print("total diff")
        print(have_folder ^ have_mrconfig)
    else:
        print(f"all ok with {len(have_mrconfig)} entries...")


main()
