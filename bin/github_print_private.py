#!/usr/bin/python3

"""
This script prints all of your github projects.
"""

import os.path # for expanduser
import configparser # for ConfigParser
import github # for Github

inifile=os.path.expanduser('~/.details.ini')
config=configparser.ConfigParser()
config.read(inifile)

opt_personal_token=config.get('github','personal_token')
opt_username=config.get('github','username')

g=github.Github(login_or_token=opt_personal_token)
for repo in g.get_user().get_repos(type="private"):
    if not repo.fork:
        print(f"{repo.name}")
