#!/usr/bin/python3

'''
This script runs a browser on the output of the current project
'''

###########
# imports #
###########
import subprocess # for check_call
import os # for getcwd

##############
# parameters #
##############
# project
project=os.getcwd().split('/')[-1]

########
# code #
########
subprocess.check_call([
    'gnome-open',
    'https://localhost:8443/{project}'.format(project=project),
])
