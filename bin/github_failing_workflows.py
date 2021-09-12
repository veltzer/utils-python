#!/usr/bin/python3

"""
This script finds which workflows in you github accounts are failing.
"""

import os.path # for expanduser
import configparser # for ConfigParser
import github # for Github

inifile=os.path.expanduser('~/.details.ini')
config=configparser.ConfigParser()
config.read(inifile)

# all of our github secret info
opt_username=config.get('github','username')
opt_password=config.get('github','password')
opt_personal_token=config.get('github','personal_token')

g=github.Github(login_or_token=opt_personal_token)
for repo in g.get_user(opt_username).get_repos():
    for workflow in repo.get_workflows():
        for run in workflow.get_runs():
            last_run = run
            break
        else:
            continue
        if last_run.conclusion != "success":
            print(f"{repo.name}: {workflow.name}")
