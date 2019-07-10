#!/usr/bin/python3

'''
A small app exiting with the error code you want.
'''

import re # for .compile, .finditer
import sys # for argv, exit
import os # for .path.join

if len(sys.argv)!=2:
    print('usage: utils_error.py [error_code]')
    sys.exit(1)
print('this is stdout', file=sys.stdout)
print('this is stderr', file=sys.stderr)
sys.exit(int(sys.argv[1]))
