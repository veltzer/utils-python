#!/usr/bin/python

"""
This script will change from one commiter to another in a git repository...
"""

import subprocess
import sys

if len(sys.argv) != 2:
    raise ValueError("usage: git_change_commiter.py [oldname]")


def main():
    oldname = sys.argv[1]
    commiter_name = "Mark Veltzer"
    author_name = "Mark Veltzer"
    commiter_email = "mark.veltzer@gmail.com"
    author_email = "mark.veltzer@gmail.com"
    expr = f"""if [ "$GIT_COMMITTER_NAME" = "{oldname}" ];
    then
        GIT_COMMITTER_NAME="{commiter_name}";
        GIT_AUTHOR_NAME="{author_name}";
        GIT_COMMITTER_EMAIL="{commiter_email}";
        GIT_AUTHOR_EMAIL="{author_email}";
        git commit-tree "$@";
    else
        git commit-tree "$@";
    fi"""
    args = ["git", "filter-branch", "--force", "--commit-filter", expr, "HEAD"]
    subprocess.check_call(args)


if __name__ == "__main__":
    main()
