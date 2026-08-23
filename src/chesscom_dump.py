#!/usr/bin/env python
"""Download every chess.com game for a user into one PGN. No auth, stdlib only."""
import argparse
import configparser
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.chess.com/pub/player"
CONFIG = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "chesscom.ini",
)
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


def load_config(path=CONFIG):
    """[chesscom] section of the ini, or an empty mapping if there is no file."""
    cp = configparser.ConfigParser()
    cp.read(path)
    return cp["chesscom"] if cp.has_section("chesscom") else {}


def main():
    cfg = load_config()

    p = argparse.ArgumentParser(
        epilog=f"defaults are read from the [chesscom] section of {CONFIG}",
    )
    # optional: falls back to the config file, so the common case is bare
    p.add_argument("username", nargs="?", default=None)
    p.add_argument("-o", "--output", default=None)
    p.add_argument("-c", "--cache", default=cfg.get("cache", "pgn_cache"),
                   help="per-month cache dir")
    p.add_argument("--delay", type=float,
                   default=float(cfg.get("delay", 0.5)))
    a = p.parse_args()

    # CLI wins over config; config exists so the username need not be retyped
    username = a.username or cfg.get("username")
    if not username:
        sys.exit(
            f"no username given and none in {CONFIG}\n"
            f"either pass one, or create the file:\n\n"
            f"  [chesscom]\n  username = your_name\n"
        )

    user = username.lower()
    out = a.output or cfg.get("output") or f"{user}.pgn"
    os.makedirs(a.cache, exist_ok=True)

    profile = get(f"{API}/{user}")
    if profile is None:
        sys.exit(f"no such chess.com user: {user}")
    profile = json.loads(profile)

    raw = get(f"{API}/{user}/games/archives")
    if raw is None:
        sys.exit(f"no archives for {user} (account may be closed)")
    archives = json.loads(raw)["archives"]

    # a wrong-but-real username is the common failure: it fetches fine and
    # yields almost nothing. Say whose account this is before downloading.
    who = ", ".join(
        str(profile[k]) for k in ("name", "location") if profile.get(k)
    )
    print(f"{user} -> {profile.get('url', '?')}" + (f" ({who})" if who else ""),
          file=sys.stderr)
    print(f"{len(archives)} monthly archives", file=sys.stderr)
    if len(archives) < 3:
        print(f"WARNING: only {len(archives)} archive month(s). If you expected "
              f"more, check the username above is really yours.", file=sys.stderr)

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
