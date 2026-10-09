#!/usr/bin/env python

"""
This script will combine a movie with its subtitles using ffmpeg.
"""

import subprocess
import sys


def main() -> None:
    debug = True
    if len(sys.argv) != 4:
        raise ValueError("usage: [movie] [srt] [outfile]")
    movie = sys.argv[1]
    srt = sys.argv[2]
    outfile = sys.argv[3]
    if debug:
        print(f"movie is {movie}")
        print(f"srt is {srt}")
        print(f"outfile is {outfile}")
    
    # Use ffmpeg to burn the subtitles into the video stream
    # using the subtitles filter.
    args = [
        "ffmpeg",
        "-i", movie,
        "-vf", f"subtitles={srt}",
        "-c:a", "copy",
        outfile,
    ]
    subprocess.check_call(args)


if __name__ == "__main__":
    main()
