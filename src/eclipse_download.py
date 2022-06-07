#!/usr/bin/python3

"""
This is a script that knows how to download eclipse.

These are examples of urls to download
http://kambing.ui.ac.id/eclipse/technology/epp/downloads/release/luna/SR2/eclipse-cpp-luna-SR2-linux-gtk-x86_64.tar.gz
http://mirrors.hustunique.com/eclipse/technology/epp/downloads/release/luna/SR2/eclipse-cpp-luna-SR2-linux-gtk.tar.gz

TODO:
- make this script convert the files to .xz storage.
"""

import os.path  # for isfile
import hashlib  # for new
import sys  # for exit

import download.generic  # for get


def hexdigest(filename, algo):
    BLOCKSIZE = 65536
    hasher = hashlib.new(algo)
    with open(filename, "rb") as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


protocol = "http"
# mirror='http://ftp.jaist.ac.jp/pub/eclipse/technology/epp/downloads/release'
mirror = (
    "http://mirror.netcologne.de/"
    "eclipse/technology/epp/downloads/release"
)
products = [
    ("jee", False),
    ("java", False),
    ("cpp", False),
    ("php", False),
    ("android", True),
    ("committers", False),
    ("javascript", False),
    ("rcp", False),
    ("dsl", False),
    ("modeling", False),
    ("reporting", False),
    ("parallel", False),
    ("testing", False),
    ("scout", False),
    #    ('automotive', True),
]
version = "R"
release = "2018-12"
platforms = [
    "-x86_64",  # x64
    #    '', # i386
]
cs_type = "sha512"


def main():

    for product, incubation in products:
        if incubation:
            incubation_str = "-incubation"
        else:
            incubation_str = ""
        for platform in platforms:
            url = (
                f"{mirror}/{release}/{version}/"
                f"eclipse-{product}-{release}-{version}{incubation_str}"
                f"-linux-gtk{platform}.tar.gz"
            )
            cs_url = (
                f"{mirror}/{release}/{version}/"
                f"eclipse-{product}-{release}-{version}{incubation_str}"
                f"-linux-gtk{platform}.tar.gz.{cs_type}"
            )
            filename = (
                f"eclipse-{product}-{release}-{version}" f"-linux-gtk{platform}.tar.gz"
            )
            cs_filename = (
                f"eclipse-{product}-{release}-{version}"
                f"-linux-gtk{platform}.tar.gz.{cs_type}"
            )
            if os.path.isfile(filename):
                print(f"skipping download for [{filename}]...")
            else:
                download.generic.get(url, filename)
            if os.path.isfile(cs_filename):
                print(f"skipping download for [{cs_filename}]...")
            else:
                download.generic.get(cs_url, cs_filename)
            # read the checksum and compare
            with open(cs_filename) as f:
                read_cs = f.readline().split()[0]
                calc_cs = hexdigest(filename, cs_type)
                if read_cs != calc_cs:
                    print(f"checksum for [{filename}] is bad...")
                    sys.exit(1)
                else:
                    print(f"checksum for [{filename}] is good...")


main()
