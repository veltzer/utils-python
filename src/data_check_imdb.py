#!/usr/bin/env python

"""
Check that .yaml files have correct names of movies
"""


import shelve
from imdb import Cinemagoer  # type: ignore
import yaml


def imdbid_to_title(f_imdbid, cache, cinemagoer):
    """ cached version of getting title by imdb """
    if f_imdbid in cache:
        obj = cache[f_imdbid]
    else:
        print(f"retrieving {f_imdbid}...")
        obj = cinemagoer.get_movie(f_imdbid)
        cache[f_imdbid] = obj
    return obj["title"]


def main():
    """ main entry point """
    shelve_filename = "imdbid_to_object.shelve"
    cache = shelve.open(shelve_filename)
    cinemagoer = Cinemagoer()
    files_to_check = [
        "yaml/video_series.yaml",
        "yaml/video_features.yaml",
    ]
    inners = [
        None,
        "items",
    ]
    for file_to_check, inner in zip(files_to_check, inners):
        print(f"checking [{file_to_check}]")
        with open(file_to_check, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        if inner is not None:
            data = data[inner]
        for datum in data:
            f_imdbid = datum["imdb_id"]
            f_name = datum["name"]
            # print(f"doing [{f_name}] [{f_imdbid}]")
            f_title = imdbid_to_title(f_imdbid, cache, cinemagoer)
            assert f_title == f_name, f"{f_imdbid} {f_title} {f_name}"
    cache.close()


if __name__ == "__main__":
    main()
