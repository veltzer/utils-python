#!/usr/bin/env python

"""
Reads Google Chrome profiles from Local State and generates one
.desktop launcher per profile in ~/.local/share/applications/.
Removes any previously-generated Chrome per-profile launchers first.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def main() -> None:
    home = Path.home()
    chrome_config = home / ".config" / "google-chrome"
    local_state = chrome_config / "Local State"
    apps_dir = home / ".local" / "share" / "applications"
    launcher_prefix = "chrome-profile-"
    chrome_bin = "/usr/bin/google-chrome-stable"

    if not local_state.is_file():
        print(f"error: {local_state} not found", file=sys.stderr)
        print(
            "is Google Chrome installed and has it been run at least once?",
            file=sys.stderr,
        )
        sys.exit(1)

    if not Path(chrome_bin).is_file() or not os.access(chrome_bin, os.X_OK):
        print(f"warning: {chrome_bin} not found or not executable", file=sys.stderr)
        print(
            "the launchers will still be written but may not work until Chrome is installed",
            file=sys.stderr,
        )

    apps_dir.mkdir(parents=True, exist_ok=True)

    # Collect launchers we previously generated (matched by our prefix).
    stale_ours = [
        f for f in apps_dir.glob(f"{launcher_prefix}*.desktop") if f.is_file()
    ]

    # Also collect user-local launchers that point at google-chrome with a
    # --profile-directory flag and weren't written by us — stale hand-rolled ones.
    stale_other = []
    for f in apps_dir.glob("*.desktop"):
        if not f.is_file() or f.name.startswith(launcher_prefix):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            if re.search(
                r"^Exec=.*google-chrome.*--profile-directory=",
                content,
                flags=re.MULTILINE,
            ):
                stale_other.append(f)
        except Exception:  # noqa: BLE001, S110
            pass

    # Read profiles
    try:
        with open(local_state, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except Exception as e:  # noqa: BLE001  # noqa: BLE001
        print(f"error reading {local_state}: {e}", file=sys.stderr)
        sys.exit(1)

    info_cache = data.get("profile", {}).get("info_cache", {})
    if not info_cache:
        print(f"no profiles found in {local_state}", file=sys.stderr)
        sys.exit(1)

    wanted_paths = set()
    wrote = 0
    unchanged = 0

    for directory, info in info_cache.items():
        name = info.get("name", "Unnamed")
        email = info.get("user_name", "")

        # Sanitize display name
        slug = re.sub(r"[^a-z0-9-]", "", name.lower().replace(" ", "-"))
        if not slug:
            slug = re.sub(r"[^a-z0-9-]", "", directory.lower().replace(" ", "-"))

        out_path = apps_dir / f"{launcher_prefix}{slug}.desktop"
        wanted_paths.add(out_path)

        wmclass = f"chrome-{slug}"
        comment = f"{name} ({email})" if email else name

        desired = f"""[Desktop Entry]
Version=1.0
Name=Chrome — {name}
GenericName=Web Browser
Comment={comment}
Exec={chrome_bin} --profile-directory="{directory}" --class="{wmclass}" %U
Terminal=false
Icon=google-chrome
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass={wmclass}
Actions=new-window;new-incognito-window;

[Desktop Action new-window]
Name=New Window
Exec={chrome_bin} --profile-directory="{directory}" --new-window

[Desktop Action new-incognito-window]
Name=New Incognito Window
Exec={chrome_bin} --profile-directory="{directory}" --incognito
"""

        if out_path.is_file():
            try:
                current_content = out_path.read_text(encoding="utf-8")
                if current_content == desired:
                    print(f"  unchanged {out_path}  ({directory} → {name})")
                    unchanged += 1
                    continue
            except Exception:  # noqa: BLE001, S110
                pass

        out_path.write_text(desired, encoding="utf-8")
        print(f"  wrote {out_path}  ({directory} → {name})")
        wrote += 1

    removed = 0
    for f in stale_ours:
        if f not in wanted_paths:
            print(f"removing stale per-profile launcher: {f}")
            f.unlink()
            removed += 1

    for f in stale_other:
        print(f"removing stale hand-rolled per-profile launcher: {f}")
        f.unlink()
        removed += 1

    if wrote > 0 or removed > 0:
        if (
            subprocess.run(  # noqa: PLW1510
                ["command", "-v", "update-desktop-database"],
                capture_output=True,
                shell=True,
            ).returncode
            == 0
        ):
            print("\nrefreshing desktop database...")
            subprocess.run(  # noqa: PLW1510
                ["update-desktop-database", str(apps_dir)], stderr=subprocess.DEVNULL
            )
        print(
            f"\ndone. wrote {wrote}, unchanged {unchanged}, removed {removed} launcher(s) in {apps_dir}."
        )
        print("they should appear in KRunner / Kickoff within a few seconds.")
    else:
        print(
            f"\nno changes were needed — {unchanged} launcher(s) already up to date in {apps_dir}."
        )


if __name__ == "__main__":
    main()
