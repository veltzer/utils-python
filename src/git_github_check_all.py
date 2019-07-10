#!/usr/bin/python3

import glob # for glob
import os.path # for split, join, isfile
import subprocess # for check_call
import os # for chdir

for gitfolder in glob.glob('*/.git'):
    folder=os.path.split(gitfolder)[0]
    project=folder
    if not os.path.isfile(os.path.join(folder,'.skip')):
        print('doing [{project}]'.format(project=project))
        os.chdir(folder)
        subprocess.check_call([
            'git',
            'diff',
            '--name-only',
        ])
        '''
        # the --short flag is no good, it doesn't tell you if you are ahead...
        subprocess.check_call([
            'git',
            'status',
            '--short',
        ])
        '''
        out=subprocess.check_output([
            'git',
            'status',
        ])
        for line in out.split('\n'):
            if line.find('ahead')!=-1:
                print(line)
        os.chdir('..')
    else:
        print('skipping [{project}]'.format(project=project))
