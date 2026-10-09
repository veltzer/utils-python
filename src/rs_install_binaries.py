#!/usr/bin/env python3

"""
Install the rs* tools from their GitHub releases into ~/install/binaries.

These tools used to live in that folder as symlinks into
~/git/<repo>/target/release/<repo>. That coupling means a "clean" of a
repository (cargo clean, a fresh checkout, a pruned target dir) breaks the
command: the link survives but points at nothing. Installing the released
binary instead makes each tool independent of the state of its checkout.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    install_dir_env = os.environ.get("RS_INSTALL_DIR")
    install_dir = Path(install_dir_env) if install_dir_env else Path.home() / "install" / "binaries"
    owner = "veltzer"

    tools = [
        "rscalendar",
        "rsconstruct",
        "rscontacts",
        "rsdedup",
        "rsear",
        "rsevo",
        "rsimagetag",
        "rslily",
        "rsmarkdownlint",
        "rsmermaid",
        "rsmultigit",
        "rspandoc",
        "rspass",
        "rspdfoverlay",
        "rsshell",
        "rssite",
        "rsslide",
        "rsspell",
        "rssvglint",
        "rstube",
        "rstype",
    ]

    if not shutil.which("gh"):
        print("gh(1) is required but was not found, install it first", file=sys.stderr)
        sys.exit(1)

    system = platform.system()
    if system == "Linux":
        os_name = "linux"
    elif system == "Darwin":
        os_name = "macos"
    else:
        print(f"unsupported operating system [{system}]", file=sys.stderr)
        sys.exit(1)

    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "aarch64"
    else:
        print(f"unsupported machine architecture [{machine}]", file=sys.stderr)
        sys.exit(1)

    suffix = f"{os_name}-{arch}"

    install_dir.mkdir(parents=True, exist_ok=True)

    installed = 0
    updated = 0
    current = 0
    missing = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        for tool in tools:
            # Get the released version
            res = subprocess.run(
                ["gh", "release", "view", "--repo", f"{owner}/{tool}", "--json", "tagName", "--jq", ".tagName"],
                capture_output=True, text=True, check=False
            )
            if res.returncode != 0:
                print(f"{tool}: no release found, skipping", file=sys.stderr)
                missing += 1
                continue

            tag = res.stdout.strip()
            remote_version = tag.removeprefix("v")

            target = install_dir / tool
            marker = install_dir / f".{tool}_version"
            local_version = ""

            if target.is_file() and os.access(target, os.X_OK) and marker.is_file():
                local_version = marker.read_text(encoding='utf-8').strip()

            if local_version == remote_version:
                print(f"{tool}: {local_version} is up to date")
                current += 1
                continue

            asset = f"{tool}-{suffix}"
            print(f"{tool}: installing {remote_version}")

            download_path = tmp_path / tool
            dl_res = subprocess.run(
                ["gh", "release", "download", tag, "--repo", f"{owner}/{tool}", 
                 "--pattern", asset, "--output", str(download_path), "--clobber"],
                check=False
            )
            if dl_res.returncode != 0:
                print(f"{tool}: could not download asset [{asset}] from [{tag}]", file=sys.stderr)
                sys.exit(1)

            download_path.chmod(0o755)

            # Move and write marker
            shutil.move(str(download_path), str(target))
            marker.write_text(remote_version + "\n", encoding='utf-8')

            if not local_version:
                installed += 1
            else:
                updated += 1

    print(f"{installed} installed, {updated} updated, {current} already current, {missing} without a release")


if __name__ == '__main__':
    main()
