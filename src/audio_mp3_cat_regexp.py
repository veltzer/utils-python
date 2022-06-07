#!/usr/bin/python3

"""
Script to be used to catenate many mp3 files.
"""

import subprocess  # for check_call, call, DEVNULL
import glob  # for glob

##############
# parameters #
##############
doRun = True
doDebug = False
doCheck = False
# do you want to redirect standard output?
doRedirect = False
do_numbers = False
do_six = True
do_same_names = False


def unite(filenames, out):
    print(f"creating [{out}] out of [{','.join(filenames)}]")
    args = [
        # "ffmpeg",
        "avconv",
        "-i",
        "concat:" + "|".join(filenames),
        "-acodec",
        "copy",
        out,
        "-loglevel",
        "quiet",
    ]
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
        print(filenames, out)


if do_numbers:
    lect = 1
    for x in range(1, 37):
        newx = f"{x:02d}"
        if doDebug:
            print(newx)
        file_list = sorted(glob.glob(f"{newx}-*"))
        if doDebug:
            print(file_list)
        assert len(file_list) == 6
        name = file_list[0][5:]
        res = f"{lect:02d} - {name}"
        if doDebug:
            print(f"new name is [{res}]")
        unite(file_list, res)
        lect += 1

if do_six:
    file_list = []
    count = 1
    lect = 1
    for f in sorted(glob.glob("*.mp3")):
        file_list.append(f)
        if count % 6 == 0:
            name = f[5:]
            res = f"{lect:02d} - {name}"
            # res=f"{lect:02d}.mp3"
            unite(file_list, res)
            file_list = []
            count = 1
            lect += 1
        else:
            count += 1

if do_same_names:
    file_list = []
    count = 1
    lect = 1
    old_name = None
    for f in sorted(glob.glob("*.mp3")):
        name = f[15:]
        if name != old_name and len(file_list) > 0:
            res = f"{lect:02d} - {old_name}"
            unite(file_list, res)
            lect += 1
            file_list = []
        old_name = name
        file_list.append(f)
