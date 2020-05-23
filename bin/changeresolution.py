#!/usr/bin/python

"""
A script to change the resolution of the screen on my DELL LATITUDE laptop

    Mark Veltzer
"""

import subprocess
import sys

# run xrandr(1) to know how to fill those params out
debug=False
width=1024;
height=768;
refresh=60;
output='eDP1';
highmodename='1280x800';
lowmodename='lowmodename';

if len(sys.argv)!=2 or (sys.argv[1]!='low' and sys.argv[1]!='high'):
    print('usage: changeresolution.py [high|low]')
    sys.exit(1)

# first lets find the low mode line etc...
# you can also call 'cvt(1' instead of 'gtf(1)'...
out=subprocess.check_output(['gtf',str(width),str(height),str(refresh)]);
line=out.strip().split('\n')[1].strip();
modeline=line.split()[2:];
if debug:
    print(modeline);
if sys.argv[1]=='low':
    args=['xrandr','--newmode',lowmodename];
    args.extend(modeline);
    subprocess.check_output(args);
    subprocess.check_output(['xrandr','--addmode',output,lowmodename]);
    subprocess.check_output(['xrandr','--output',output,'--mode',lowmodename]);
else:
    subprocess.check_output(['xrandr','--output',output,'--mode',highmodename]);
    subprocess.check_output(['xrandr','--delmode',output,lowmodename]);
    subprocess.check_output(['xrandr','--rmmode',lowmodename]);
