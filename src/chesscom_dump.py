#!/usr/bin/env python3
"""Download every chess.com game for a user into one PGN. No auth, stdlib only."""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.chess.com/pub/player"
UA = "chesscom_dump/1.0 (contact: you@example.com)"  # chess.com 403s generic agents


def get(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 503):
                wait = int(e.headers.get("Retry-After", 2 ** i))
                print(f"  {e.code}, sleeping {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** i)
    raise RuntimeError(f"gave up on {url}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("username")
    p.add_argument("-o", "--output", default=None)
    p.add_argument("-c", "--cache", default="pgn_cache", help="per-month cache dir")
    p.add_argument("--delay", type=float, default=0.5)
    a = p.parse_args()

    user = a.username.lower()
    out = a.output or f"{user}.pgn"
    os.makedirs(a.cache, exist_ok=True)

    archives = json.loads(get(f"{API}/{user}/games/archives"))["archives"]
    print(f"{len(archives)} monthly archives", file=sys.stderr)

    current = archives[-1] if archives else None
    for url in archives:
        ym = "-".join(url.split("/")[-2:])          # 2026-08
        path = os.path.join(a.cache, ym + ".pgn")
        # never trust the cache for the in-progress month
        if os.path.exists(path) and url != current:
            continue
        print(f"fetch {ym}", file=sys.stderr)
        body = get(url + "/pgn") or b""
        with open(path, "wb") as f:
            f.write(body)
        time.sleep(a.delay)

    with open(out, "wb") as f:
        for url in archives:
            ym = "-".join(url.split("/")[-2:])
            path = os.path.join(a.cache, ym + ".pgn")
            if not os.path.exists(path):
                continue
            with open(path, "rb") as g:
                data = g.read().strip()
            if data:
                f.write(data + b"\n\n")

    with open(out, "rb") as f:
        games = f.read().count(b"[Event ")
    print(f"wrote {out}: {games} games, {os.path.getsize(out)/1e6:.1f} MB", file=sys.stderr)


if __name__ == "__main__":
    main()
