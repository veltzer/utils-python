#!/usr/bin/env python3

"""
Remove old Claude Code binaries left behind by the self-updater.

The native installer keeps every version it ever downloaded under
  ~/.local/share/claude/versions/<version>
and points ~/.local/bin/claude at the current one. Each binary is ~200MB
and nothing ever removes the old ones, so the directory grows with every
update. This script deletes every version except the one in use.

Which version is "in use" is decided by resolving the claude symlink
(~/.local/bin/claude, or whatever `claude` on PATH resolves to). The newest
version by version-sort is always kept too, so a broken or missing symlink
can never lead to deleting everything.

Usage:
  claude_remove_old_versions.py
  DRY_RUN=1 claude_remove_old_versions.py

Environment:
  CLAUDE_VERSIONS_DIR  where the versions live
  DRY_RUN=1            print what would be removed but remove nothing
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def get_version_tuple(v_str: str) -> tuple:
    return tuple(map(int, v_str.split('.')))


def get_size(path: Path) -> str:
    res = subprocess.run(["du", "-sh", str(path)], capture_output=True, text=True, check=False)
    if res.returncode == 0:
        return res.stdout.split('\t')[0]
    return "unknown"


def main() -> None:
    versions_dir_env = os.environ.get("CLAUDE_VERSIONS_DIR")
    versions_dir = Path(versions_dir_env) if versions_dir_env else Path.home() / ".local" / "share" / "claude" / "versions"
    dry_run = os.environ.get("DRY_RUN", "0") == "1"

    if not versions_dir.is_dir():
        print(f"no versions directory at {versions_dir}", file=sys.stderr)
        sys.exit(1)

    versions = []
    version_pattern = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')
    for p in versions_dir.iterdir():
        if p.is_dir() and version_pattern.match(p.name):
            versions.append(p.name)

    if not versions:
        print(f"no versions found under {versions_dir}", file=sys.stderr)
        sys.exit(1)

    versions.sort(key=get_version_tuple)

    keep = set()
    
    links_to_check = [Path.home() / ".local" / "bin" / "claude"]
    claude_path = shutil.which("claude")
    if claude_path:
        links_to_check.append(Path(claude_path))

    resolved_versions_dir = versions_dir.resolve()
    for link in links_to_check:
        if link.exists():
            target = link.resolve()
            if target.parent == resolved_versions_dir:
                keep.add(target.name)
                
    keep.add(versions[-1])

    print(f"keeping: {' '.join(sorted(keep))}")

    removed = 0
    for version in versions:
        if version in keep:
            continue
        path = versions_dir / version
        size = get_size(path)
        if dry_run:
            print(f"would remove: {version} ({size})")
        else:
            print(f"removing: {version} ({size})")
            shutil.rmtree(path, ignore_errors=True)
        removed += 1

    if removed == 0:
        print("nothing to remove")
    elif not dry_run:
        print(f"total size now: {get_size(versions_dir)}")


if __name__ == '__main__':
    main()
