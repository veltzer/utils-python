#!/usr/bin/env python3

"""
This is based on:
https://github.com/ptarjan/viencrypt/blob/master/viencrypt
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    my_name = Path(sys.argv[0]).stem

    # -n: no swap file will be used
    # -i NONE: no .viminfo file updates
    editor = ["vim", "-n", "-i", "NONE", "-M"]
    
    key = ""
    encrypt_sh = Path.home() / ".config" / "encrypt.sh"
    if encrypt_sh.exists():
        res = subprocess.run(
            ["bash", "-c", f"source {encrypt_sh} && echo $key"], 
            capture_output=True, text=True, check=False
        )
        if res.returncode == 0:
            key = res.stdout.strip()

    filename = "passwords.gpg"
    if len(sys.argv) == 1:
        print(f"No filename specified. Using default [{filename}]")
    elif len(sys.argv) > 2:
        print(f"{sys.argv[0]} [filename.gpg]")
        sys.exit(2)
    else:
        filename = sys.argv[1]

    if shutil.which("shred"):
        rm_cmd = ["shred", "-u"]
    elif shutil.which("srm"):
        rm_cmd = ["srm", "-z"]
    else:
        rm_cmd = ["rm"]

    if not Path(filename).exists():
        print(f"{filename} doesn't exist.")
        sys.exit(1)
    elif not os.access(filename, os.R_OK):
        print(f"{filename} isn't readable.")
        sys.exit(2)

    tmp_fd, tmp_path = tempfile.mkstemp(prefix=f"{my_name}.", dir=str(Path.home() / "tmp"))
    os.close(tmp_fd)

    try:
        # decrypt into the tmp file
        gpg_args = ["gpg", "--quiet", "--decrypt", "--batch", "--output", tmp_path]
        if key:
            gpg_args.extend(["--default-key", key])
        gpg_args.append(filename)

        run_res = subprocess.run(gpg_args, check=False)
        if run_res.returncode != 0:
            subprocess.run(rm_cmd + [tmp_path], check=False)
            print(f"could not decrypt file with code [{res.returncode}]")
            sys.exit(res.returncode)

        # edit the file
        subprocess.run(editor + [tmp_path], check=False)
    finally:
        subprocess.run(rm_cmd + [tmp_path], check=False)


if __name__ == "__main__":
    main()
