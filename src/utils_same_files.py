#!/usr/bin/python3

'''
say whether any several files have the same content or not.
'''

import sys # for argv, exit
import os.path # for isfile
import hashlib # for md5

if len(sys.argv)==1:
    print('{0}: usage: {0} [files...]'.format(sys.argv[0]))
    sys.exit(1)
if len(sys.argv)==2:
    print('{0}: only one file given...'.format(sys.argv[0]))
    print('{0}: usage: {0} [files...]'.format(sys.argv[0]))
    sys.exit(1)

files=sys.argv[1:]
for file in files:
    if not os.path.isfile(file):
        print('{0}: cannot find or access file [{1}]'.format(sys.argv[0], file))
        sys.exit(1)
md5=None
for file in files:
    new_md5=hashlib.md5(open(file, 'r').read().encode())
    if md5 is not None:
        if new_md5.hexdigest()!=md5.hexdigest():
            print('they are different')
            sys.exit(1)
    else:
        md5=new_md5
print('they are the same')
