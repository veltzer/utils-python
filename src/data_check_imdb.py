#!/usr/bin/env python

"""
Check that .yaml files have correct names of movies
"""


import sys
import shelve
from imdb import Cinemagoer  # type: ignore
import yaml


def imdb_id_to_imdb_data(f_imdb_id, cache, cinemagoer):
    """ cached version of getting title by imdb """
    if f_imdb_id in cache:
        obj = cache[f_imdb_id]
    else:
        print(f"retrieving [{f_imdb_id}]...")
        obj = cinemagoer.get_movie(f_imdb_id)
        cache[f_imdb_id] = obj
    return obj


def main():
    """ main entry point """
    shelve_filename = "imdb_id_to_imdb_data.shelve"
    cache = shelve.open(shelve_filename)
    cinemagoer = Cinemagoer()
    files_to_check = sys.argv[1:]
    for file_to_check in files_to_check:
        # print(f"checking [{file_to_check}]")
        with open(file_to_check, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        data = data["items"]
        for datum in data:
            f_imdb_id = datum["imdb_id"]
            f_name = datum["name"]
            # print(f"doing [{f_name}] [{f_imdb_id}]")
            imdb_data = imdb_id_to_imdb_data(f_imdb_id, cache, cinemagoer)
            f_title = imdb_data["title"]
            assert f_title == f_name, f"{f_imdb_id} {f_title} {f_name}"
    cache.close()


if __name__ == "__main__":
    main()
