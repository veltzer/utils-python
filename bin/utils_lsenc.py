#!/usr/bin/python3

import os
import chardet

for n in os.listdir('.'.encode()):
    encoding = chardet.detect(n)['encoding']
    confidence = chardet.detect(n)['confidence']
    print(f"{n} => {encoding} ({confidence})")
