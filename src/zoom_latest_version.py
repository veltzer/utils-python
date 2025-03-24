#!/usr/bin/python

"""
zoom_latest_version
"""

import requests


def get_latest_zoom_version():
    """
    Fetches the latest Zoom version number for Linux clients.
    Returns: string with version number or None if not found
    """
    try:
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Try Ubuntu/Debian client URL
        url = 'https://zoom.us/client/latest/zoom_amd64.deb'
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=500)

        # The version is usually in the redirect URL
        final_url = response.url
        if 'zoom_amd64.deb' in final_url:
            version = final_url.split('/')[-2]
            return version

        return None

    except requests.RequestException as e:
        print(f"Error fetching Zoom version: {e}")
        return None


def main():
    version = get_latest_zoom_version()
    if version:
        print(f"Latest Zoom Linux version: {version}")
    else:
        print("Could not retrieve Zoom version")


if __name__ == "__main__":
    main()
