#!/usr/bin/env python
import argparse
import pprint

import myimdb


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch IMDb data by ID.")
    parser.add_argument("imdbid", help="The IMDb ID to fetch")
    args = parser.parse_args()
    print("fetching from imdbapi...")
    data = myimdb.get_movie_by_imdbid(args.imdbid)
    if data is not None:
        print(f"data is [{data}]")
    else:
        print(f"imdbid [{args.imdbid}] not found")
    print("fetching from IMDB...")
    if data:
        pprint.pprint(data)


if __name__ == "__main__":
    main()
