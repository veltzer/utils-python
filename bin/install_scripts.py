#!/usr/bin/python3

"""
installation script

TODO:
- add easy option to copy files instead of sylinking them.
"""

import os
import os.path

# actually perform the actions?
doit = True
# print what we are doing?
debug = True
# remove target files if they are links
force = True


def do_install(source, target):
    if force:
        if os.path.islink(target):
            os.unlink(target)
    if doit:
        if debug:
            print(f"symlinking [{source}], [{target}]")
        os.symlink(source, target)


def file_gen(root_folder, recurse):
    if recurse:
        for root, dirs, files in os.walk(root_folder):
            yield root, dirs, files
    else:
        dirs = []
        files = []
        for file in os.listdir(root_folder):
            full = os.path.join(root_folder, file)
            if os.path.isdir(full):
                dirs.append(file)
            if os.path.isfile(full):
                files.append(file)
        yield root_folder, dirs, files


def install(root_folder, target_folder, recurse):
    target_folder = os.path.expanduser(target_folder)
    cwd = os.getcwd()
    if os.path.isdir(target_folder):
        for file in os.listdir(target_folder):
            full = os.path.join(target_folder, file)
            if os.path.islink(full):
                link_target = os.path.realpath(full)
                if link_target.startswith(cwd):
                    if doit:
                        if debug:
                            print(f"unlinking [{full}]")
                        os.unlink(full)
    else:
        os.mkdir(target_folder)
    for root, directories, files in file_gen(root_folder, recurse):
        for file in files:
            source = os.path.abspath(os.path.join(root, file))
            target = os.path.join(target_folder, file)
            do_install(source, target)
        for directory in directories:
            source = os.path.abspath(os.path.join(root, directory))
            target = os.path.join(target_folder, directory)
            do_install(source, target)


install("src", "~/install/bin", False)
