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
    except requests.RequestException:
        return None
    else:
        return response.text


def get_movie_by_title(title: str) -> dict[str, Any] | None:
    url = "http://www.omdbapi.com"
    params = {"r": "json", "t": title}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        if data.get("Response") == "True":
            f_title = data.get("Title")
            if f_title == title:
                return data
    except requests.RequestException:
        return None
    else:
        return None
