#!/usr/bin/env python

"""
Renames Google Chrome profile directories under ~/.config/google-chrome/
and updates Chrome's Local State so the profile dropdown still works.

Usage (interactive):
  ./chrome_rename_profiles.py

Usage (batch):
  ./chrome_rename_profiles.py "Profile 1=Teaching" "Profile 4=Personal"

Flags: --dry-run, --no-backup, --help
"""

import datetime
import json
import subprocess
import sys
from pathlib import Path


def list_profiles(local_state_path: Path) -> list:
    try:
        with open(local_state_path, 'r', encoding='utf-8') as file_handle:
            data = json.load(file_handle)
    except Exception as e:  # noqa: BLE001
        print(f"error reading {local_state_path}: {e}", file=sys.stderr)
        return []

    info_cache = data.get("profile", {}).get("info_cache", {})
    profiles = []
    for directory, info in info_cache.items():
        name = info.get("name", "?")
        email = info.get("user_name", "no account")
        profiles.append((directory, name, email))
    return profiles

def main() -> None:
    home = Path.home()
    chrome_config = home / ".config" / "google-chrome"
    local_state = chrome_config / "Local State"
    backup_dir = home / ".local" / "share" / "chrome-profile-backups"
    
    dry_run = False
    do_backup = True
    rename_pairs_raw = []

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in ('--help', '-h'):
            print(__doc__.strip())
            sys.exit(0)
        elif arg == '--dry-run':
            dry_run = True
        elif arg == '--no-backup':
            do_backup = False
        elif arg.startswith('--'):
            print(f"unknown flag: {arg}", file=sys.stderr)
            sys.exit(1)
        else:
            if '=' not in arg:
                print(f"expected OLD=NEW, got: {arg}", file=sys.stderr)
                sys.exit(1)
            rename_pairs_raw.append(arg)

    if not chrome_config.is_dir():
        print(f"no {chrome_config}", file=sys.stderr)
        sys.exit(1)
    if not local_state.is_file():
        print(f"no {local_state}", file=sys.stderr)
        sys.exit(1)

    # Check if chrome is running
    try:
        if subprocess.run(["pgrep", "-x", "chrome"], capture_output=True).returncode == 0 or \
           subprocess.run(["pgrep", "-x", "google-chrome"], capture_output=True).returncode == 0:  # noqa: PLW1510
            print("close Chrome first (pgrep -a chrome to see what's running)", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        pass # pgrep not installed, ignore

    if not rename_pairs_raw:
        print("current profiles:\n")
        print(f"  {'DIRECTORY':<20}  {'DISPLAY NAME':<20}  ACCOUNT")
        print(f"  {'-'*20}  {'-'*20}  {'-'*7}")
        for directory, name, email in list_profiles(local_state):
            print(f"  {directory:<20}  {name:<20}  {email}")
        print("\nenter renames as OLD=NEW, empty line to finish:")
        while True:
            try:
                pair = input("rename> ").strip()
            except EOFError:
                break
            if not pair:
                break
            if '=' not in pair:
                print("  (need OLD=NEW)")
                continue
            rename_pairs_raw.append(pair)

    if not rename_pairs_raw:
        print("nothing to do")
        sys.exit(0)

    old_names = []
    new_names = []
    for pair in rename_pairs_raw:
        old, new = pair.split('=', 1)
        if not old or not new:
            print(f"bad pair: {pair}", file=sys.stderr)
            sys.exit(1)
        if old == "Default":
            print("refusing to rename Default", file=sys.stderr)
            sys.exit(1)
        if new == "Default":
            print("refusing to rename to Default", file=sys.stderr)
            sys.exit(1)
        if '/' in new:
            print(f"bad new name: {new}", file=sys.stderr)
            sys.exit(1)
        
        old_dir = chrome_config / old
        if not old_dir.is_dir():
            print(f"no such profile dir: {old}", file=sys.stderr)
            sys.exit(1)
        
        new_dir = chrome_config / new
        if new_dir.exists():
            print(f"dest exists: {new}", file=sys.stderr)
            sys.exit(1)
            
        old_names.append(old)
        new_names.append(new)

    print("\nplan:")
    for old, new in zip(old_names, new_names):
        print(f"  '{old}' -> '{new}'")

    if dry_run:
        print("--dry-run: no changes made")
        sys.exit(0)

    print()
    try:
        ans = input("proceed? [y/N] ").strip().lower()
    except EOFError:
        ans = ''
    if ans != 'y':
        print("aborted")
        sys.exit(0)

    if do_backup:
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d-%H%M%S")
        backup_file = backup_dir / f"chrome-config-{ts}.tar"
        print(f"backing up to {backup_file}...")
        try:
            subprocess.run(["tar", "-cf", str(backup_file), "-C", str(home / ".config"), "google-chrome"], check=True)
            du_out = subprocess.run(["du", "-h", str(backup_file)], capture_output=True, text=True).stdout  # noqa: PLW1510
            size = du_out.split('\t')[0] if du_out else "?"
            print(f"backup: {size}")
        except subprocess.CalledProcessError as e:
            print(f"backup failed: {e}", file=sys.stderr)
            sys.exit(1)

    print("renaming directories...")
    for old, new in zip(old_names, new_names):
        src = chrome_config / old
        dst = chrome_config / new
        print(f"'{src}' -> '{dst}'")
        src.rename(dst)

    print("rewriting Local State...")
    try:
        with open(local_state, 'r', encoding='utf-8') as file_handle:
            data = json.load(file_handle)
    except Exception as e:  # noqa: BLE001
        print(f"error reading {local_state}: {e}", file=sys.stderr)
        sys.exit(1)

    mapping = dict(zip(old_names, new_names))

    profile_data = data.get("profile", {})
    
    # Update info_cache
    info_cache = profile_data.get("info_cache", {})
    new_info_cache = {}
    for k, v in info_cache.items():
        new_key = mapping.get(k, k)
        new_info_cache[new_key] = v
    profile_data["info_cache"] = new_info_cache

    # Update last_used
    last_used = profile_data.get("last_used")
    if last_used is not None:
        profile_data["last_used"] = mapping.get(last_used, last_used)

    # Update profiles_order
    profiles_order = profile_data.get("profiles_order")
    if profiles_order is not None:
        profile_data["profiles_order"] = [mapping.get(p, p) for p in profiles_order]

    try:
        with open(local_state, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, separators=(',', ':')) # Chrome uses compact JSON usually, or can just dump normally
    except Exception as e:  # noqa: BLE001
        print(f"ERROR rewriting {local_state}: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("done.\n")

    print("result:")
    for directory, name, email in list_profiles(local_state):
        marker = " " if (chrome_config / directory).is_dir() else "!"
        print(f"{marker} {directory:<20}  {name:<20}  {email}")

    print("\nnext: test with")
    for new in new_names:
        print(f"  google-chrome --profile-directory=\"{new}\"")
    print("then re-run chrome_regen_launchers.py to update .desktop files")
    if do_backup:
        print(f"restore: tar -xf {backup_file} -C {home}/.config")

if __name__ == '__main__':
    main()
