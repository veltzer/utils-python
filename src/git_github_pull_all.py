#!/usr/bin/python2

'''
This script pulls all the project from a github account.

NOTES:
- this script should be python2 because it relies on the github module which
is python2 only

TODO:
- remove the username and password from this script.
'''

from __future__ import print_function
import glob # for glob
import os.path # for split, join, isfile, expanduser
import subprocess # for check_call
import os # for chdir
import github # for Github
import ConfigParser # for ConfigParser

inifile=os.path.expanduser('~/.github.ini')
config=ConfigParser.ConfigParser()
config.read(inifile)
opt_login=config.get('github','login')
opt_pass=config.get('github','pass')
g=github.Github(opt_login, opt_pass)

done=set()
for repo in g.get_user().get_repos():
    folder=repo.name
    project=folder
    if os.path.isdir(folder):
        if not os.path.isfile(os.path.join(folder,'.skip')):
            print('project [{project}] exists, pulling it...'.format(project=project))
            os.chdir(folder)
            subprocess.check_call([
                'git',
                'pull',
                #'--tags',
            ])
            os.chdir('..')
        else:
            print('project [{project}] exists, skipping it because of .skip file...'.format(project=project))
    else:
        print('project [{project}] does not exists, cloning it...'.format(project=project))
        #print(dir(repo))
        subprocess.check_call([
            'git',
            'clone',
            repo.clone_url,
        ])
    done.add(folder)

for gitfolder in glob.glob('*/.git'):
    folder=os.path.split(gitfolder)[0]
    if not folder in done:
        project=folder
        if not os.path.isfile(os.path.join(folder,'.skip')):
            print('doing non-github project [{project}]'.format(project=project))
            os.chdir(folder)
            subprocess.check_call([
                'git',
                'pull',
                #'--tags',
            ])
            os.chdir('..')
        else:
            print('skipping non-github project [{project}]'.format(project=project))
