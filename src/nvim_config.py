#!/usr/bin/env python

"""
Script to set up LazyVim for Neovim.
"""

import datetime
import shutil
import subprocess
import sys
from pathlib import Path


def print_color(color: str, text: str) -> None:
    colors = {
        "green": "\033[0;32m",
        "red": "\033[0;31m",
        "yellow": "\033[0;33m",
    }
    code = colors.get(color, "")
    reset = "\033[0m"
    print(f"{code}{text}{reset}")


def check_requirements() -> None:
    missing_requirements = False

    if not shutil.which("nvim"):
        print_color(
            "red",
            "Error: Neovim is not installed. Please install Neovim 0.8.0+ (0.9+ recommended).",
        )
        missing_requirements = True

    if not shutil.which("git"):
        print_color("red", "Error: Git is not installed. Please install Git.")
        missing_requirements = True

    if missing_requirements:
        sys.exit(1)


def setup_lazyvim() -> None:
    print_color("yellow", "This script will set up LazyVim for Neovim.")
    print_color(
        "yellow", "It will backup your existing Neovim configuration if it exists."
    )

    try:
        reply = input("Do you want to proceed? (y/n): ").strip().lower()
    except EOFError:
        reply = ""

    if reply != "y":
        print_color("yellow", "Setup cancelled.")
        sys.exit(0)

    home = Path.home()
    timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d%H%M%S")

    # Backup existing configuration
    nvim_config = home / ".config" / "nvim"
    if nvim_config.is_dir():
        print_color("yellow", "Backing up existing Neovim configuration...")
        backup_path = home / ".config" / f"nvim.bak.{timestamp}"
        shutil.move(str(nvim_config), str(backup_path))

    # Optional backups
    dirs_to_backup = [
        home / ".local" / "share" / "nvim",
        home / ".local" / "state" / "nvim",
        home / ".cache" / "nvim",
    ]

    for d in dirs_to_backup:
        if d.is_dir():
            print_color("yellow", f"Backing up {d}...")
            backup_path = Path(f"{d}.bak.{timestamp}")
            shutil.move(str(d), str(backup_path))

    # Clone LazyVim starter
    print_color("green", "Cloning LazyVim starter...")
    subprocess.run(
        ["git", "clone", "https://github.com/LazyVim/starter", str(nvim_config)],
        check=False,
    )

    # Remove .git folder
    git_folder = nvim_config / ".git"
    if git_folder.is_dir():
        print_color("green", "Removing .git folder...")
        shutil.rmtree(git_folder)

    print_color("green", "LazyVim setup complete!")
    print_color("yellow", "You can now start Neovim by running 'nvim'.")
    print_color("yellow", "LazyVim will automatically install plugins on first run.")


def main() -> None:
    check_requirements()
    setup_lazyvim()


if __name__ == "__main__":
    main()
