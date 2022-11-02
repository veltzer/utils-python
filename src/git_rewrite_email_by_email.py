#!/usr/bin/python

"""
This will allow you to update your email in a git repository.
"""

import subprocess
import sys

if len(sys.argv) != 1:
    print(f"{sys.argv[0]}: usage: {sys.argv[0]}", file=sys.stderr)
    sys.exit(1)

old_emails = [
    "mark@twiggle.com",
    "mark.veltzer@gmail.net",
]
for old_email in old_emails:
    new_email = "mark.veltzer@gmail.com"
    expr = f"""if [ "$GIT_COMMITTER_EMAIL" = "{old_email}" ];
    then
            GIT_AUTHOR_EMAIL="{new_email}";
            git commit-tree "$@";
    else
            git commit-tree "$@";
    fi"""
    # --force is there to override old backup of 'git filter-branch'
    args = ["git", "filter-branch", "--force", "--commit-filter", expr]
    subprocess.check_call(args)

# commit everything
subprocess.check_call(
    [
        "git",
        "push",
        "--force",
        "--tags",
        "origin",
        "refs/heads/*",
    ]
)
