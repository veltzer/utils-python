#!/usr/bin/env python

"""
check_keyring.py

Tests whether the default GNOME keyring (Secret Service collection) is
unlocked, locked-but-openable-with-empty-password, or locked with a real
password.

Requirements:
    sudo apt install python3-secretstorage

Usage:
    python3 check_keyring.py

Exit codes:
    0 - keyring is accessible without a password prompt
    1 - keyring is locked and needs a password
    2 - error (D-Bus, no secret service running, etc.)
"""

import sys

try:
    import secretstorage
except ImportError:
    print("ERROR: python3-secretstorage is not installed.")
    print("Install it with: sudo apt install python3-secretstorage")
    sys.exit(2)


def main() -> int:
    try:
        conn = secretstorage.dbus_init()
    except Exception as e:
        print(f"ERROR: could not connect to D-Bus secret service: {e}")
        print("Is gnome-keyring-daemon or kwalletd running?")
        return 2

    try:
        collection = secretstorage.get_default_collection(conn)
    except Exception as e:
        print(f"ERROR: could not get default collection: {e}")
        return 2

    label = collection.get_label()
    print(f"Default collection: {label!r}")

    if not collection.is_locked():
        print("Status: ALREADY UNLOCKED")
        print("(Either it has no password, or PAM/the session already "
              "unlocked it.)")
        return 0

    print("Status: locked — attempting to unlock...")
    try:
        # This will pop a dialog ONLY if a real password is required.
        # If the keyring has an empty password, it unlocks silently.
        was_dismissed = collection.unlock()
    except Exception as e:
        print(f"ERROR while unlocking: {e}")
        return 2

    if was_dismissed:
        print("Status: LOCKED — unlock prompt was dismissed or failed.")
        print("The keyring has a real password set.")
        return 1

    if collection.is_locked():
        print("Status: STILL LOCKED after unlock attempt.")
        return 1

    print("Status: UNLOCKED successfully without a password prompt.")
    print("(Keyring password is empty, or PAM provided the password "
          "transparently.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
