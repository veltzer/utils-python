#!/usr/bin/env python

"""
This script checks goodreads ids of books
"""


import sys
import shelve
import yaml
import requests
import bs4  # type: ignore


CHEKC_ID_FOR_EVERY_BOOK = True


def get_goodreads_data(f_goodreads_id, session):
    # print(f"retrieving {f_goodreads_id}...")
    url = f"https://www.goodreads.com/book/show/{f_goodreads_id}"
    response = session.get(url)
    response.raise_for_status()
    # print(response.content)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    f_title = soup.find(id="bookTitle")
    if f_title is None:
        f_title = soup.find("h1", {"data-testid":"bookTitle"})
    else:
        f_title = f_title.text.strip()
    if f_title is None:
        with open("/tmp/temp.html", "w") as file:
            file.write(str(soup))
    assert f_title is not None, "Could not find title"
    return {
        "title": f_title,
    }


def get_simania_data(f_simania_id, session):
    # print(f"retrieving [{f_simania_id}]...")
    url = f"https://simania.co.il/bookdetails.php?item_id={f_simania_id}"
    response = session.get(url)
    response.raise_for_status()
    # print(response.content)
    soup = bs4.BeautifulSoup(response.content, "html.parser")
    results = soup.findAll("h2", {"style":""})
    assert len(results) == 1
    f_title = results[0].text
    if f_title is None:
        with open("/tmp/temp.html", "w") as file:
            file.write(str(soup))
    assert f_title is not None, "Could not find title"
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


def simania_id_to_simania_data(f_simania_id, cache, session):
    if f_simania_id in cache:
        obj = cache[f_simania_id]
    else:
        obj = get_simania_data(f_simania_id, session)
        cache[f_simania_id] = obj
    return obj


def main():
    """ main entry point """
    cache_goodreads = shelve.open("goodreads_id_to_goodreads_data.shelve")
    cache_simania = shelve.open("simania_id_to_simania_data.shelve")
    session = requests.Session()
    files_to_check = sys.argv[1:]
    for file_to_check in files_to_check:
        # print(f"checking [{file_to_check}]")
        with open(file_to_check, encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
        data = data["items"]
        for datum in data:
            done = False
            for name in datum["names"]:
                if "goodreads_id" in name:
                    f_goodreads_id = name["goodreads_id"]
                    f_name = name["name"]
                    goodreads_data = goodreads_id_to_goodreads_data(f_goodreads_id, cache_goodreads, session)
                    f_title = goodreads_data["title"]
                    assert f_title == f_name, f"{f_goodreads_id} {f_title} {f_name}"
                    done = True
                if "simania_id" in name:
                    f_simania_id = name["simania_id"]
                    f_name = name["name"]
                    simania_data = simania_id_to_simania_data(f_simania_id, cache_simania, session)
                    f_title = simania_data["title"]
                    assert f_title == f_name, f"{f_simania_id} {f_title} {f_name}"
                    done = True
            if CHEKC_ID_FOR_EVERY_BOOK:
                assert done is True, f"no id found for {datum['names']}..."
    cache_goodreads.close()
    cache_simania.close()


if __name__ == "__main__":
    main()
