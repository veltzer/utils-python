#!/usr/bin/python3

'''
This script prints all of your github projects.
'''

import os.path # for expanduser
import configparser # for ConfigParser
import github # for Github
import json # for dumps
import sys # for stdout
import jsonpickle # for encode

inifile=os.path.expanduser('~/.details.ini')
config=configparser.ConfigParser()
config.read(inifile)

# all of our github secret info
opt_username=config.get('github','username')
opt_password=config.get('github','password')
opt_client_id=config.get('github','client_id')
opt_client_secret=config.get('github','client_secret')
opt_personal_token=config.get('github','personal_token')

'''
This is an unauthenticated call, we don't really need an authenticated call
for what we do here

for authenticated called pass one of:
1) login_or_token=opt_username, password=opt_password
    * this will cause issued with 2factor auth)
2) login_or_token=opt_personal_token
    The token is generated in the github gui.
3) client_id=opt_client_id, client_secret=opt_client_secret
    These items are also generated in the github gui.
'''

g=github.Github()
for repo in g.get_user(opt_username).get_repos():
    print(repo.name)
    print(repo.description)
    print(repo.fork)
#    print(jsonpickle.encode(repo, max_depth=1, unpicklable=False, make_refs=False))
#    json.dump(repo, sys.stdout, skipkeys=True);
#    print(repo)
