#!/usr/bin/env python
import argparse

import myvideo


def main() -> None:
    parser = argparse.ArgumentParser(description="Show information about a video file.")
    parser.add_argument("filename", help="Video file path")
    args = parser.parse_args()
    video_info = myvideo.info(args.filename)
    print(f"duration: {video_info.get('duration')}")
    print(f"durationsecs: {video_info.get('durationsecs')}")
    print(f"bitrate: {video_info.get('bitrate')}")
    print(f"vcodec: {video_info.get('vcodec')}")
    print(f"vformat: {video_info.get('vformat')}")
    print(f"acodec: {video_info.get('acodec')}")
    print(f"asamplerate: {video_info.get('asamplerate')}")
    print(f"achannels: {video_info.get('achannels')}")
    print(f"size: {video_info.get('size')}")


if __name__ == "__main__":
    main()
