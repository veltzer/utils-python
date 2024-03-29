#!/usr/bin/python

"""
This script converts files given to it to some encoding, utf_8 by default.
It auto-detects the current encoding, reads using the current
encoding and writes using the utf-encoding.
"""

import sys
import codecs
import chardet

# to which charset to translate to? the -sig is what causes codecs to emit the
# utf-8 BOM at the begining of the output file (these are 3 characters)
to_charset = "utf-8-sig"
# from which charset to translate from?
from_charset = "ascii"
# overwrite the files we read?
write = True
# do you want to debug?
debug = True

# list all encodings that are supported by python
# CAVEAT: does not list encodings that do not have aliases
# import encodings.aliases # for aliases
# print(encodings.aliases.aliases.keys())
# exit(1)

if len(sys.argv) < 2:
    print("usage: utils_to_encoding.py [filename]", file=sys.stderr)
    sys.exit(1)

for filename in sys.argv[1:]:
    if debug:
        print(f"doing file [{filename}]")
    with open(filename, "rb") as f:
        b = f.read()
        h = chardet.detect(b)
        detect_charset = h["encoding"]
        if detect_charset is None:
            if debug:
                print("could not detect charset, continuing to next file...")
            continue
        new_content = b.decode(detect_charset)
        if write:
            with codecs.open(filename, "w", to_charset) as f2:
                f2.write(new_content)
