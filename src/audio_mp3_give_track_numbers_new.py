#!/usr/bin/python3

'''
This script gives track number according to order.
use like this: [script name] *.mp3

It works using id3v2 something like this:
let y=1; for x in *; do id3v2 -T $y/36 "$x" ; let "y=y+1"; done

'''

import subprocess # for check_call
import os.path # for isfile
import sys # for argv

# first check that all files are there
set_size=len(sys.argv)-1
for i, filename in enumerate(sys.argv[1:]):
    assert os.path.isfile(filename)
    subprocess.check_call([
        'id3v2',
        '-T',
        '{0}/{1}'.format(i+1, set_size),
        filename,
    ])
