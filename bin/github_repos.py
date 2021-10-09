#!/usr/bin/python3

"""
This script finds which workflows in you github accounts are failing.
"""

import os.path  # for expanduser
import configparser  # for ConfigParser
import github  # for Github

inifile = os.path.expanduser("~/.details.ini")
config = configparser.ConfigParser()
config.read(inifile)
opt_username = config.get("github", "username")
opt_personal_token = config.get("github", "personal_token")

g = github.Github(login_or_token=opt_personal_token)
for repo in g.get_user(opt_username).get_repos():
    print(repo.name)
