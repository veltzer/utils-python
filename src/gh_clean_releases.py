#!/usr/bin/env python

"""
Keep only the latest N GitHub releases and delete all others.

Uses the `gh` CLI for authentication and API calls.
"""

import json
import subprocess
import sys


def gh_api(endpoint, method="GET"):
    """Call the GitHub API via the gh CLI."""
    cmd = ["gh", "api", endpoint]
    if method != "GET":
        cmd.extend(["-X", method])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.stdout.strip():
        return json.loads(result.stdout)
    return None


def get_all_release_ids(repo):
    """Fetch all release IDs, newest first."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/releases", "--paginate", "--jq", ".[].id"],
        capture_output=True, text=True, check=True,
    )
    return [int(line) for line in result.stdout.strip().splitlines() if line.strip()]


def delete_release(repo, release_id):
    """Delete a release."""
    gh_api(f"repos/{repo}/releases/{release_id}", method="DELETE")


def get_repo():
    """Get the current repo's owner/name from gh."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def main():
    repo = get_repo()
    count = 4
    if len(sys.argv) > 1:
        count = int(sys.argv[1])

    print(f"Fetching releases for {repo}...")
    release_ids = get_all_release_ids(repo)
    total = len(release_ids)
    print(f"Found {total} releases.")

    to_delete = release_ids[count:]
    if not to_delete:
        print(f"Only {total} releases found, keeping all.")
        sys.exit(0)

    print(f"Keeping {count} latest releases, deleting {len(to_delete)} older releases...")
    for i, release_id in enumerate(to_delete, 1):
        print(f"  [{i}/{len(to_delete)}] Deleting release {release_id}...")
        delete_release(repo, release_id)

    print("Done.")


if __name__ == "__main__":
    main()
