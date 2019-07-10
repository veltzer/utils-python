#!/usr/bin/python3

'''
This script will catenate mp3 files correctly using ffmpeg.
see: http://superuser.com/questions/314239/how-to-join-merge-many-mp3-files
'''

import subprocess # for check_call
import optparse # for OptionParser
import os.path # for isfile
import sys # for exit

##############
# parameters #
##############
# version of this script
__version__ = '0.1'

########################
# command line parsing #
########################
parser = optparse.OptionParser(
    description=__doc__,
    usage='%prog [options] [files to catenate]',
    version=__version__
)

parser.add_option('-o', '--output', dest='output', default=None, help='output file [default: %default]')
(options, free_args) = parser.parse_args()

# check that all free files are there
for file in free_args:
    if not os.path.isfile(file):
        print('file [{0}] is not there...'.format(file))
        sys.exit(1)
if options.output is None:
    print('must supply -o argument')
    sys.exit(1)
if os.path.isfile(options.output):
    print('file [{0}] is there...'.format(options.output))
    sys.exit(1)

########
# code #
########
args=[ 'avconv', '-i', 'concat:'+'|'.join(free_args), '-acodec', 'copy', options.output, '-loglevel', 'quiet' ]
subprocess.check_call(args)
