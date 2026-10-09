#!/usr/bin/env python

"""
Script to set Firefox as the default browser in Linux environments.
"""

import subprocess


def get_default_browser() -> str:
    res = subprocess.run(
        ["xdg-settings", "get", "default-web-browser"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


def set_default_browser(browser: str) -> None:
    subprocess.run(["xdg-settings", "set", "default-web-browser", browser], check=False)


def get_mime_default(mime_type: str) -> str:
    res = subprocess.run(
        ["xdg-mime", "query", "default", mime_type],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


def set_mime_default(browser: str, mime_type: str) -> None:
    subprocess.run(["xdg-mime", "default", browser, mime_type], check=False)


def get_kde_browser() -> str:
    try:
        from pathlib import Path

        kdeglobals = Path.home() / ".config" / "kdeglobals"
        if not kdeglobals.exists():
            return ""

        # kdeglobals might have issues with strict ini format, reading manually is safer
        with open(kdeglobals, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("BrowserApplication="):
                    return line.strip().split("=", 1)[1]
    except Exception:  # noqa: BLE001, S110
        pass
    return ""


def set_kde_browser(browser: str) -> None:
    from pathlib import Path

    kdeglobals = Path.home() / ".config" / "kdeglobals"
    subprocess.run(
        [
            "kwriteconfig5",
            "--file",
            str(kdeglobals),
            "--group",
            "General",
            "--key",
            "BrowserApplication",
            browser,
        ],
        check=False,
    )


def main() -> None:
    browser_wanted = "firefox.desktop"

    current = get_default_browser()
    if current != browser_wanted:
        print(
            f"your current browser is [{current}], we will change it to {browser_wanted}..."
        )
        set_default_browser(browser_wanted)
        current = get_default_browser()
        print(f"your current browser is now [{current}]...")
    else:
        print(f"your current browser is [{current}], that's good...")

    for x in [
        "text/html",
        "x-scheme-handler/http",
        "x-scheme-handler/https",
        "x-scheme-handler/about",
    ]:
        current_handler = get_mime_default(x)
        if current_handler != browser_wanted:
            print(
                f"your current {x} handler is [{current_handler}], we will change it to {browser_wanted}..."
            )
            set_mime_default(browser_wanted, x)
            current_handler = get_mime_default(x)
            print(f"your current {x} handler is now [{current_handler}]...")
        else:
            print(f"your current {x} handler is [{current_handler}], that's good...")

    current_kde = get_kde_browser()
    if current_kde != browser_wanted:
        print(
            f"your current kde browser is [{current_kde}], we will change it to {browser_wanted}..."
        )
        set_kde_browser(browser_wanted)
        current_kde = get_kde_browser()
        print(f"your current kde browser is now [{current_kde}]...")
    else:
        print(f"your current kde browser is [{current_kde}], that's good...")


if __name__ == "__main__":
    main()
