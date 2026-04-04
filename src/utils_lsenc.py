#!/usr/bin/python

"""
List encdings of files
"""

import os
import chardet

for n in os.listdir(".".encode()):
    result = chardet.detect(n)
    encoding = result["encoding"]
    confidence = result["confidence"]
    print(f"{n.decode()} => {encoding} ({confidence})")
