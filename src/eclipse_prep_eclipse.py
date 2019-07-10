#!/usr/bin/python3

'''
This script preps eclipse for my use by installing cdt and vrapper
on it

TODO:
- check if the features we install exist before we install them.
This will save time (see my eclipse notes about how to do that)
and only install the feature if it is missing.
- the name 'neon' is hardcoded in this script. find out how to find
the version of a specific eclipse without running it and remove
this hardcoding.
'''

###########
# imports #
###########
import subprocess # for check_call, DEVNULL
import os.path # for isfile
import os # for access, X_OK
import sys # for exit, stderr

##############
# parameters #
##############
# what file to check to see that we are in an eclipse folder
checkfile='eclipse'
# show progress?
progress=True
# debug
debug=False
# what features do I want installed?
features=[
    'org.eclipse.cdt',
    'net.sourceforge.vrapper',
]

########
# code #
########

def die(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)

# first check if this is an eclipse folder
if not os.path.isfile(checkfile):
    die('this is not an eclipse folder')
if not os.access(checkfile, os.X_OK):
    die('this is not an eclipse folder')

for feature in features:
    if progress:
        print('doing feature [{0}]'.format(feature))
    args=[
        './eclipse',
        '-nosplash',
        '-application',
        'org.eclipse.equinox.p2.director',
        '-repository',
        'http://download.eclipse.org/releases/neon/',
        '-installIU',
        feature+'.feature.group',
    ]
    if debug:
        subprocess.check_call(args)
    else:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
