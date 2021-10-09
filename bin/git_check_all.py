#!/usr/bin/python3

import glob # for glob
import os.path # for split, join, isfile
import os # for chdir
import subprocess # for check_call

for gitfolder in glob.glob('*/.git'):
    folder=os.path.split(gitfolder)[0]
    project=folder
    if not os.path.isfile(os.path.join(folder,'.skip')):
        print(f"doing [{project}]")
        os.chdir(folder)
        subprocess.check_call([
            'git',
            'diff',
            '--name-only',
        ])
        # the --short flag is no good, it doesn't tell you if you are ahead...
        out=subprocess.check_output([
            'git',
            'status',
            # '--short',
        ])
        for line in out.split('\n'):
            if line.find('ahead')!=-1:
                print(line)
        os.chdir('..')
    else:
        print(f"skipping [{project}]")
