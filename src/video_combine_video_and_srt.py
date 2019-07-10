#!/usr/bin/python3

"""
This script will combine a movie with it's subtitles.

References:
https://vanalboom.org/node/11

TODO:
- the output files produced by this script cannot be played
by the ps3. find another codec.
"""

import subprocess
import sys

debug=False
debug=True

if len(sys.argv)!=4:
    raise ValueError('usage: [movie] [srt] [outfile]')

# lavc is documented as the best encoding method so I use it.
codec_video_best='lavc'
codec_audio_best='lavc'
# ps3 does not support lavc so I use x264 instead
codec_video_ps3='x264'
codec_audio_ps3='lavc'
#codec_video=codec_video_ps3
#codec_audio=codec_audio_ps3
codec_video=codec_video_best
codec_audio=codec_audio_best

movie=sys.argv[1]
srt=sys.argv[2]
outfile=sys.argv[3]
if debug:
    print("movie is",movie);
    print("srt is",srt);
    print("outfile is",outfile);
args=[
    'mencoder',movie,
    # with copy you don't get the subtitles inserted, you have
    # to encode in order to get the subtitles in...
    '-ovc',codec_video,
    # audio can just be copied in theory. In practice you want
    # to encode it with the same encoder since if you don't you
    # will get video and audio out of sync...
    '-oac',codec_audio,
    # without this sync will be lost
    #'-of','mpeg',
    # plug in the subtitles...
    '-sub',srt,
    # you can control subtitles but I rather let mencoder do it's
    # thing here. I hope it will get better with time.
    #'-font','/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf',
    #'-subfont-autoscale','0',
    #'-subfont-text-scale','25',
    #'-subpos','100',
    '-o',outfile,
]
subprocess.check_call(args)
