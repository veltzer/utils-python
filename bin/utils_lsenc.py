#!/usr/bin/python3

import chardet
import os  

for n in os.listdir('.'.encode()):
    encoding = chardet.detect(n)['encoding']
    confidence = chardet.detect(n)['confidence']
    print(f"{n} => {encoding} ({confidence})")
