#!/usr/bin/env python
import argparse

from mutagen.id3 import ID3, ID3NoHeaderError


def main() -> None:
    parser = argparse.ArgumentParser(description="Print id3v2 info for a file.")
    parser.add_argument("files", nargs="+", help="MP3 files to process")
    args = parser.parse_args()
    for filename in args.files:
        print(f"info for file [{filename}]...")
        try:
            audio = ID3(filename)
        except ID3NoHeaderError:
            print("do not have tag info on the file")
            return
        for key, frame in audio.items():
            print(key)
            print(f"{type(frame).__name__} ({key}):")
            if hasattr(frame, "text"):
                print(f" * text => {frame.text}")
            elif hasattr(frame, "url"):
                print(f" * url => {frame.url}")
            else:
                print(f" * {frame!r}")


if __name__ == "__main__":
    main()
