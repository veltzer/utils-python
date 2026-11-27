#!/usr/bin/env python

"""
Script to be used to catenate many mp3 files.
"""

import glob
import subprocess

do_run = True
do_check = False
# do you want to redirect standard output?
do_redirect = False


def unite(filenames, out):
    print(f"creating [{out}] out of [{filenames}]")
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
    if do_run:
        if do_check:
            if do_redirect:
                subprocess.check_call(args, stdout=subprocess.DEVNULL)
            else:
                subprocess.check_call(args)
        elif do_redirect:
            subprocess.call(args, stdout=subprocess.DEVNULL)
        else:
            subprocess.call(args)
    else:
        print(filenames, out)


def main() -> None:
    do_debug = False
    do_numbers = False
    do_six = True
    do_same_names = False
    if do_numbers:
        lect = 1
        for x in range(1, 37):
            newx = f"{x:02d}"
            if do_debug:
                print(newx)
            file_list = sorted(glob.glob(f"{newx}-*"))
            if do_debug:
                print(file_list)
            assert len(file_list) == 6
            name = file_list[0][5:]
            res = f"{lect:02d} - {name}"
            if do_debug:
                print(f"new name is [{res}]")
            unite(file_list, res)
            lect += 1
    if do_six:
        file_list: list[str] = []
        count = 1
        lect = 1
        for f in sorted(glob.glob("*.mp3")):
            file_list.append(f)
            if count % 6 == 0:
                name = f[5:]
                res = f"{lect:02d} - {name}"
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


if __name__ == "__main__":
    main()
