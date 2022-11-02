#!/usr/bin/python

import os
import chardet

for n in os.listdir(".".encode()):
    encoding = chardet.detect(n)["encoding"]
    confidence = chardet.detect(n)["confidence"]
    print(f"{n.decode()} => {encoding} ({confidence})")
