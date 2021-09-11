#!/usr/bin/python3

"""
This script fixes a bug in github:
- when you create a repo it does not have a homepage (repo.homepage==null).
- then if you add a homepage and remove it, the homepage is an empty string.

This script turns homepage=null in all repos where homepage=''
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
opt_client_id=config.get('github','client_id')
opt_client_secret=config.get('github','client_secret')
opt_personal_token=config.get('github','personal_token')

g=github.Github(login_or_token=opt_personal_token)
for repo in g.get_user(opt_username).get_repos():
    if repo.homepage=='' or repo.homepage is None:
        homepage = f"https://github.com/veltzer/{repo.name}"
        print(f"patching [{repo.name}]...")
        repo.edit(repo.name, homepage=homepage);
