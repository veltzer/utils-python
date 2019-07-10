#!/usr/bin/python3

import sys # for argv
import subprocess # for check_call
import time # for sleep

if len(sys.argv)!=3:
    raise ValueError('usage: num dec')

num=int(sys.argv[1])
dec=int(sys.argv[2])

while num>0:
    subprocess.check_call([
        'espeak',
        'there are {num} seconds to end of exercise'.format(num=num),
    ])
    time.sleep(dec)
    num-=dec
subprocess.check_call([
    'espeak',
    'the exercise is over!',
])
