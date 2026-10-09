from typing import Any

import requests


def escape_single_quote(string: str) -> str:
    return string.replace("'", "'")


def get_movie_by_imdbid(imdbid: str) -> str | None:
    url = "http://www.omdbapi.com"
    params = {"r": "json", "i": imdbid}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def get_movie_by_title(title: str) -> dict[str, Any] | None:
    url = "http://www.omdbapi.com"
    params = {"r": "json", "t": title}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("Response") == "True":
            f_title = data.get("Title")
            if f_title == title:
                return data
        return None
    except requests.RequestException:
        return None
