#!/usr/bin/python2.7

import chardet
import os  

for n in os.listdir('.'):
    print('{0} => {1} ({2})'.format(n, chardet.detect(n)['encoding'], chardet.detect(n)['confidence']))
