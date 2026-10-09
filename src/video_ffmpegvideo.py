#!/usr/bin/env python

"""
This script transcodes various video formats to MPEG2 Video and
AC3 audio in an MPEG2 Transport Stream for the DirecTV HR2x

FFMpeg and Mediainfo must be installed for this script to work.

Input Parameters: Input, Output, Video Bitrate, Audio Bitrate

Revision 2.00  11/29/2008
Updated to work with the HR2x auto screen size feature
"""

import subprocess
import sys


def get_mediainfo(file_path: str, parameter: str) -> str:
    res = subprocess.run(
        ["/usr/bin/mediainfo", f"--Inform=Video;%{parameter}%", file_path],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


def main() -> None:
    if len(sys.argv) < 5:
        print(
            "Usage: video_ffmpegvideo.py <input> <output> <vbitrate> <abitrate>",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    vbitrate = sys.argv[3]
    abitrate = sys.argv[4]

    width_str = get_mediainfo(input_file, "Width")
    height_str = get_mediainfo(input_file, "Height")

    if not width_str or not height_str:
        print("Failed to read video dimensions using mediainfo", file=sys.stderr)
        sys.exit(1)

    width = float(width_str)
    height = float(height_str)

    audcodec = "ac3"

    aspect = (width / height) * 100
    print(f"{int(aspect)}")

    comp = 175
    bars = 0
    pad = 0

    if aspect > comp:
        # needs bars top and bottom
        bars = 1
        pad_float = ((width / 1.75) - height) / 2
        pad = int(pad_float)

        mod = pad % 2
        if mod == 1:
            # pad must be an even number
            pad += 1

    print(f"{pad}")

    # Make sure the ffmpeg path is correct
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-b:v",
        vbitrate,
        "-maxrate",
        vbitrate,
        "-minrate",
        vbitrate,
        "-bufsize",
        "5097k",
        "-threads",
        "2",
        "-b:a",
        abitrate,
        "-acodec",
        audcodec,
        "-async",
        "1",
        "-f",
        "mpegts",
        "-y",
    ]

    # Note: original used -bt 380k (bitrate tolerance, removed in modern ffmpeg), -b/-ab are -b:v/-b:a
    # It also used -padtop/-padbottom which is now replaced by -vf "pad=..."

    if bars == 1:
        # bars top and bottom
        # Original: -padtop ${pad} -padbottom ${pad}
        # Modern ffmpeg: -vf "pad=iw:ih+2*{pad}:0:{pad}" (width is iw, height is ih+2*pad, x is 0, y is pad)
        ffmpeg_cmd.extend(["-vf", f"pad=iw:ih+{pad * 2}:0:{pad}"])
    else:
        # bars left and right
        # Original: -padleft 4 -padright 4
        # Modern ffmpeg: -vf "pad=iw+8:ih:4:0"
        ffmpeg_cmd.extend(["-vf", "pad=iw+8:ih:4:0"])

    # the original script output to stdout when it used `-` and `> $2`, but we can directly output
    ffmpeg_cmd.append(output_file)

    print(f"Running command: {' '.join(ffmpeg_cmd)}")
    sys.exit(subprocess.run(ffmpeg_cmd, check=False).returncode)


if __name__ == "__main__":
    main()
