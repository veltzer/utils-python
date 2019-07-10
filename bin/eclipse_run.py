#!/usr/bin/python3

# this script launches eclipse
# this script also maximizes the eclipse window using the technique
# described in:
# http://unix.stackexchange.com/questions/103602/how-to-maximize-a-window-programmably-in-x-window

# this will require that the workspace created will be unique (say tmpfile or something).
# this will also require that we signal the zoom of the window with that tmpfile id.

###########
# imports #
###########
import os.path # for isdir, expanduser
import subprocess # for check_call, DEVNULL
import time # for sleep
import os # for getcwd

##############
# parameters #
##############
# project
project=os.getcwd().split('/')[-1]
# where to put the workspace
folder=os.path.expanduser('~/shared_archive/workspaces/{project}'.format(project=project))
# where is the eclipse to run
eclipse=os.path.expanduser('~/install/eclipse/eclipse')
# debug the script?
debug=False

#############
# functions #
#############
def max_output(out):
    found_cnt=0
    found_id=None
    for x in out.split('\n'):
        fields=x.split()
        if debug:
            print(fields)
        if len(fields)>=2:
            name=' '.join(fields[2:])
            if name.endswith('Eclipse'):
                found_cnt+=1
                found_id=fields[0]
    if found_cnt==1:
        #time.sleep(2)
        args=[
            'wmctrl',
            '-i',
            '-r',
            found_id,
            '-b',
            #'toggle,maximized_vert,maximized_horz',
            'add,maximized_vert,maximized_horz',
        ]
        if debug:
            print('sending signal to', found_id)
            print(' '.join(args))
        subprocess.check_call(args)
        return True
    else:
        return False

########
# code #
########

# run eclipse with the folder as the workspace
pid=os.fork()
if pid==0:
    # child
    # we MUST launch with '-nosplash' so that the trick of sending
    # a 'maximize' event to the window will work...
    subprocess.check_call([
        eclipse,
        '-nosplash',
        '-data',
        folder,
        '-pluginCustomization',
        'support/pluginCustomization.ini',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    # parent
    # wait for child to appear as window and then maximize it
    for x in range(10):
        out=subprocess.check_output([
            'wmctrl',
            '-l',
        ]).decode()
        if max_output(out):
            break
        else:
            time.sleep(2)
    if debug:
        print('in end of script')
