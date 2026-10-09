#!/usr/bin/env python

"""
This script checks the books database for extension, permission, and depth problems.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    # First check that we are in the right folder
    if not Path("by_name").is_dir():
        print("put me in the folder where by_name is...", file=sys.stderr)
        sys.exit(1)

    folders = ["by_name", "by_topic"]

    allowed_extensions = {
        ".chm",
        ".tar.bz2",
        ".pdf",
        ".ps",
        ".html",
        ".dvi",
        ".lit",
        ".doc",
        ".djvu",
        ".zip",
        ".rtf",
        ".txt",
        ".pdb",
        ".mht",
        ".rar",
        ".jpg",
        ".js",
        ".gif",
        ".epub",
        ".mobi",
        ".nfo",
        ".tar.xz",
    }

    print("EXTENSION PROBLEMS")
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for root, _, files in os.walk(folder):
            # mindepth 2 means we don't check files directly in by_name/ or by_topic/
            # Assuming mindepth 2 means root != folder
            if root == folder:
                continue
            for f in files:
                p = Path(root) / f
                # Extract double extensions for tar.bz2 and tar.xz
                suffix = (
                    "".join(p.suffixes[-2:])
                    if p.name.endswith(".tar.bz2") or p.name.endswith(".tar.xz")
                    else p.suffix
                )
                if suffix not in allowed_extensions:
                    print(p)

    print("FILE PERMISSION PROBLEMS")
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for root, _, files in os.walk(folder):
            if root == folder:
                continue
            for f in files:
                p = Path(root) / f
                try:
                    mode = p.stat().st_mode & 0o777
                    if mode != 0o444:
                        print(p)
                except OSError:
                    pass

    print("FOLDER PERMISSION PROBLEMS")
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for root, dirs, _ in os.walk(folder):
            if root == folder:
                continue
            for d in dirs:
                p = Path(root) / d
                try:
                    mode = p.stat().st_mode & 0o777
                    if mode != 0o775:
                        print(p)
                except OSError:
                    pass

    print("DEPTH PROBLEMS")
    by_name = Path("by_name")
    if by_name.exists():
        for root, _, files in os.walk("by_name"):
            # mindepth 4 (folder counts as 0, 1st subdir as 1, 2nd as 2, 3rd as 3)
            # path split length > 4
            depth = len(Path(root).parts)
            if depth >= 4:
                for f in files:
                    print(Path(root) / f)

    print("ARTICLES FILE PERMISSION PROBLEMS")
    articles = Path("articles")
    if articles.exists():
        for root, _, files in os.walk("articles"):
            if root == "articles":
                continue
            for f in files:
                p = Path(root) / f
                try:
                    mode = p.stat().st_mode & 0o777
                    if mode != 0o444:
                        print(p)
                except OSError:
                    pass

    print("ARTICLES EXTENSIONS")
    if articles.exists():
        for root, _, files in os.walk("articles"):
            if root == "articles":
                continue
            for f in files:
                p = Path(root) / f
                if p.suffix != ".pdf":
                    print(p)


if __name__ == "__main__":
    main()
