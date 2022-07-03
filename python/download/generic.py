"""
A module to download a url

References:
- http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
"""

import urllib.request
import os
import os.path
import progressbar  # type: ignore


def get(url, file):
    """
    A function to download a file and show progress report
    while doing it
    """
    print(f"downloading [{url}]...")
    if os.path.dirname(file) != '':
        os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "wb") as f, urllib.request.urlopen(url) as u:
        meta = u.info()
        file_size = int(meta['Content-Length'])
        block_sz = 8192

        maxval = file_size // block_sz
        if file_size % block_sz > 0:
            maxval += 1

        pbar = progressbar.ProgressBar(maxval=maxval)
        pbar.start()
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            f.write(buffer)
            pbar.update(pbar.currval + 1)
        pbar.finish()
        f.close()
