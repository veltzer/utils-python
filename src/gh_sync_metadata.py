#!/usr/bin/env python

"""
Sync a repository's GitHub metadata (description, topics, and the
wiki/issues/projects feature policy), printing only what actually differs.

Source of truth for description and topics is config/project.lua in the repo:
  NAME              -- the repository name (must match the GitHub repo)
  DESCRIPTION_SHORT -- becomes the GitHub "description"
  KEYWORDS          -- a lua list, becomes the GitHub "topics"

The feature policy is a fixed fleet default, not read from the repo:
  wiki = off, issues = on, projects = off.

Usage:
  gh_sync_metadata.py            # every repo the owner has (same as --all)
  gh_sync_metadata.py --all      # every repo the owner has, checked out
                                 #   under the base dir
  gh_sync_metadata.py DIR ...    # each named repo directory
  DRY_RUN=1 gh_sync_metadata.py  # print differences but change nothing
"""

import json
import os
import shutil
import subprocess
import sys

# Fixed fleet feature policy: wiki off, issues on, projects off.
POLICY_WIKI = False
POLICY_ISSUES = True
POLICY_PROJECTS = False


def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def find_lua() -> str:
    for cmd in ["lua5.4", "lua"]:
        path = shutil.which(cmd)
        if path:
            return path
    die("lua is not installed")
    return ""


def lua_scalar(lua_bin: str, file_path: str, field: str) -> str:
    script = f"""
        local f, d = "{file_path}", "{field}"
        local ok = pcall(dofile, f)
        if not ok then os.exit(0) end
        local v = _G[d]
        if v ~= nil then io.write(tostring(v)) end
    """
    res = subprocess.run(  # noqa: PLW1510
        [lua_bin, "-e", script], capture_output=True, text=True
    )
    return res.stdout.strip()


def lua_keywords(lua_bin: str, file_path: str) -> list[str]:
    script = f"""
        local f = "{file_path}"
        local ok = pcall(dofile, f)
        if not ok then os.exit(0) end
        if type(KEYWORDS) ~= "table" then os.exit(0) end
        table.sort(KEYWORDS)
        for _, k in ipairs(KEYWORDS) do print(k) end
    """
    res = subprocess.run(  # noqa: PLW1510
        [lua_bin, "-e", script], capture_output=True, text=True
    )
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def sync_one(dir_path: str, owner: str, lua_bin: str, dry_run: bool) -> None:
    lua_file = os.path.join(dir_path, "config", "project.lua")
    if not os.path.isfile(lua_file):
        print(f"{dir_path}: no config/project.lua, skipping", file=sys.stderr)
        return

    name = lua_scalar(lua_bin, lua_file, "NAME")
    if not name:
        print(f"{dir_path}: config/project.lua has no NAME, skipping", file=sys.stderr)
        return

    repo = f"{owner}/{name}"

    # --- description ---
    want_desc = lua_scalar(lua_bin, lua_file, "DESCRIPTION_SHORT")
    if want_desc:
        res = subprocess.run(  # noqa: PLW1510
            [
                "gh",
                "repo",
                "view",
                repo,
                "--json",
                "description",
                "--jq",
                '.description // ""',
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            have_desc = res.stdout.strip()
            if want_desc != have_desc:
                print(f"{name}: description")
                print(f"  local:  {want_desc}")
                print(f"  github: {have_desc}")
                if not dry_run:
                    subprocess.run(  # noqa: PLW1510
                        ["gh", "repo", "edit", repo, "--description", want_desc],
                        stdout=subprocess.DEVNULL,
                    )

    # --- topics ---
    want_topics = set(lua_keywords(lua_bin, lua_file))
    if want_topics:
        res = subprocess.run(  # noqa: PLW1510
            [
                "gh",
                "repo",
                "view",
                repo,
                "--json",
                "repositoryTopics",
                "--jq",
                "[.repositoryTopics[].name]",
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            try:
                have_topics_list = json.loads(res.stdout)
                have_topics = set(have_topics_list)
            except json.JSONDecodeError:
                have_topics = set()

            if want_topics != have_topics:
                print(f"{name}: topics")
                print(f"  local:  {' '.join(sorted(want_topics))}")
                print(f"  github: {' '.join(sorted(have_topics))}")
                if not dry_run:
                    args = []
                    for t in have_topics - want_topics:
                        args.extend(["--remove-topic", t])
                    for t in want_topics - have_topics:
                        args.extend(["--add-topic", t])
                    if args:
                        subprocess.run(  # noqa: PLW1510
                            ["gh", "repo", "edit", repo] + args,
                            stdout=subprocess.DEVNULL,
                        )

    # --- feature policy ---
    res = subprocess.run(  # noqa: PLW1510
        [
            "gh",
            "repo",
            "view",
            repo,
            "--json",
            "hasWikiEnabled,hasIssuesEnabled,hasProjectsEnabled",
        ],
        capture_output=True,
        text=True,
    )
    if res.returncode == 0:
        try:
            features = json.loads(res.stdout)
            have_wiki = features.get("hasWikiEnabled", False)
            have_issues = features.get("hasIssuesEnabled", False)
            have_projects = features.get("hasProjectsEnabled", False)

            fargs = []
            if have_wiki != POLICY_WIKI:
                fargs.append(f"--enable-wiki={str(POLICY_WIKI).lower()}")
            if have_issues != POLICY_ISSUES:
                fargs.append(f"--enable-issues={str(POLICY_ISSUES).lower()}")
            if have_projects != POLICY_PROJECTS:
                fargs.append(f"--enable-projects={str(POLICY_PROJECTS).lower()}")

            if fargs:
                print(f"{name}: features")
                print(
                    f"  want:   wiki={str(POLICY_WIKI).lower()} issues={str(POLICY_ISSUES).lower()} projects={str(POLICY_PROJECTS).lower()}"
                )
                print(
                    f"  github: wiki={str(have_wiki).lower()} issues={str(have_issues).lower()} projects={str(have_projects).lower()}"
                )
                if not dry_run:
                    subprocess.run(  # noqa: PLW1510
                        ["gh", "repo", "edit", repo] + fargs, stdout=subprocess.DEVNULL
                    )
        except json.JSONDecodeError:
            pass


def sync_all(owner: str, base_dir: str, lua_bin: str, dry_run: bool) -> None:
    res = subprocess.run(  # noqa: PLW1510
        [
            "gh",
            "repo",
            "list",
            owner,
            "--no-archived",
            "--source",
            "--limit",
            "1000",
            "--json",
            "name",
            "--jq",
            ".[].name",
        ],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        die("failed to list repositories")

    for name in res.stdout.splitlines():
        name = name.strip()
        if not name:
            continue
        dir_path = os.path.join(base_dir, name)
        if not os.path.isdir(dir_path):
            print(f"{name}: no checkout at {dir_path}, skipping", file=sys.stderr)
            continue
        sync_one(dir_path, owner, lua_bin, dry_run)


def main() -> None:
    owner = os.environ.get("GH_OWNER", "veltzer")
    dry_run = os.environ.get("DRY_RUN", "0") == "1"
    base_dir = os.environ.get("GH_BASE_DIR", os.path.expanduser("~/git"))

    if not shutil.which("gh"):
        die("gh is not installed")

    lua_bin = find_lua()

    args = sys.argv[1:]

    if not args or (len(args) == 1 and args[0] == "--all"):
        sync_all(owner, base_dir, lua_bin, dry_run)
    else:
        for d in args:
            if d == "--all":
                sync_all(owner, base_dir, lua_bin, dry_run)
            else:
                sync_one(d, owner, lua_bin, dry_run)


if __name__ == "__main__":
    main()
