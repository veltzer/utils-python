#!/usr/bin/env python

"""
This script checks goodreads ids of books
"""


import sys
import shelve
import yaml
import requests
import bs4  # type: ignore


SAVE_TEMP = True


def get_goodreads_data(f_goodreads_id, session):
    # print(f"retrieving {f_goodreads_id}...")
    url = f"https://www.goodreads.com/book/show/{f_goodreads_id}"
    response = session.get(url)
    response.raise_for_status()
    # print(response.content)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    if SAVE_TEMP:
        with open("/tmp/temp.html", "w") as file:
            file.write(str(soup))
    f_title = soup.find(id="bookTitle")
    if f_title is None:
        f_title = soup.find("h1", {"data-testid":"bookTitle"})
        # print("title is ", f_title)
    else:
        # print(f_title)
        f_title = f_title.text.strip()
    return {
        "title": f_title,
    }


def goodreads_id_to_goodreads_data(f_goodreads_id, cache, session):
    if f_goodreads_id in cache:
        obj = cache[f_goodreads_id]
    else:
        obj = get_goodreads_data(f_goodreads_id, session)
        cache[f_goodreads_id] = obj
    return obj


def main():
    """ main entry point """
    shelve_filename = "goodreads_id_to_goodreads_data.shelve"
    cache = shelve.open(shelve_filename)
    session = requests.Session()
    files_to_check = sys.argv[1:]
    for file_to_check in files_to_check:
        # print(f"checking [{file_to_check}]")
        with open(file_to_check, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        data = data["items"]
        for datum in data:
            for name in datum["names"]:
                if "goodreads_id" in name:
                    f_goodreads_id = name["goodreads_id"]
                    f_name = name["name"]
                    print(f"doing [{f_name}] [{f_goodreads_id}]")
                    goodreads_data = goodreads_id_to_goodreads_data(f_goodreads_id, cache, session)
                    f_title = goodreads_data["title"]
                    assert f_title == f_name, f"{f_goodreads_id} {f_title} {f_name}"
    cache.close()


if __name__ == "__main__":
    main()
