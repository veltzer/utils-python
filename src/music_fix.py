#!/usr/bin/env python
import argparse
import pprint

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


def first(mp3, key):
    """the first value of a tag, or the empty string if it has none"""
    values = mp3.get(key)
    return values[0] if values else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix ID3 tag info in files.")
    parser.add_argument("files", nargs="+", help="MP3 files to process")
    parser.add_argument("--fix", action="store_true", help="Actually fix the files")
    parser.add_argument(
        "--no-print", action="store_true", dest="no_print", help="Do not print info"
    )
    args = parser.parse_args()
    debug = True
    should_print = not args.no_print
    fix = args.fix
    for filename in args.files:
        if should_print:
            print(f"analyzing [{filename}]...")
        try:
            mp3 = EasyID3(filename)
        except ID3NoHeaderError:
            print(f"ID3v2 tags do not exist in {filename}")
            continue
        if debug:
            print("====")
            pprint.pprint(dict(mp3))
            print("====")
            print(f"artist is {first(mp3, 'artist')}")
            print(f"album is {first(mp3, 'album')}")
            print(f"year is {first(mp3, 'date')}")
            print(f"genre is {first(mp3, 'genre')}")
        if fix:
            mp3.save()


if __name__ == "__main__":
    main()
