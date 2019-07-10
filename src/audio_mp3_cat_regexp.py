#!/usr/bin/python3

'''
Script to be used to catenate many mp3 files.
'''

import subprocess # for check_call, call, DEVNULL
import glob # for glob

doRun=True
doDebug=False
doCheck=False
# do you want to redirect standard output?
doRedirect=False

def unite(l, out):
    #args=[ 'ffmpeg', '-i', 'concat:'+'|'.join(l), '-acodec', 'copy', out ]
    print('creating [%s] out of [%s]' % (out, ','.join(l)))
    args=[ 'avconv', '-i', 'concat:'+'|'.join(l), '-acodec', 'copy', out, '-loglevel', 'quiet' ]
    if doRun:
        if doCheck:
            if doRedirect:
                subprocess.check_call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.check_call(args)
        else:
            if doRedirect:
                subprocess.call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.call(args)
    else:
        print(l,out)

'''
lect=1
for x in range(1,37):
    newx='%02d' % (x,)
    if doDebug:
        print(newx)
    l=sorted(glob.glob('%s-*' % (str(newx),)))
    if doDebug:
        print(l)
    assert len(l)==6
    name=l[0][5:]
    res='%02d - %s' % (lect,name)
    if doDebug:
        print('new name is [%s]' % (res))
    unite(l, res)
    lect+=1
'''

l=[]
count=1
lect=1
for f in sorted(glob.glob('*.mp3')):
    l.append(f)
    if count%6==0:
        name=f[5:]
        res='%02d - %s' % (lect,name)
        #res='%02d.mp3' % (lect)
        unite(l, res)
        l=[]
        count=1
        lect+=1
    else:
        count+=1

'''
# unify same names
l=[]
count=1
lect=1
old_name=None
for f in sorted(glob.glob('*.mp3')):
    name=f[15:]
    if name!=old_name and len(l)>0:
        res='%02d - %s' % (lect,old_name)
        unite(l, res)
        lect+=1
        l=[]
    old_name=name
    l.append(f)
'''
