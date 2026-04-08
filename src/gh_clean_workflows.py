#!/usr/bin/env python

"""
Delete all but the last N GitHub Actions workflow runs for a repository.

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


def get_all_workflow_runs(repo):
    """Fetch all workflow run IDs, newest first."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/runs", "--paginate", "--jq", ".workflow_runs[].id"],
        capture_output=True, text=True, check=True,
    )
    return [int(line) for line in result.stdout.strip().splitlines() if line.strip()]


def delete_workflow_run(repo, run_id):
    """Delete a workflow run."""
    gh_api(f"repos/{repo}/actions/runs/{run_id}", method="DELETE")


def get_repo():
    """Get the current repo's owner/name from gh."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def main():
    repo = get_repo()
    keep = 4
    if len(sys.argv) > 1:
        keep = int(sys.argv[1])

    print(f"Fetching workflow runs for {repo}...")
    run_ids = get_all_workflow_runs(repo)
    total = len(run_ids)
    print(f"Found {total} workflow runs, keeping {keep} most recent.")

    to_delete = run_ids[keep:]
    if not to_delete:
        print("Nothing to delete.")
        sys.exit(0)

    print(f"Deleting {len(to_delete)} workflow runs...")
    for i, run_id in enumerate(to_delete, 1):
        print(f"  [{i}/{len(to_delete)}] Deleting run {run_id}...")
        delete_workflow_run(repo, run_id)

    print("Done.")


if __name__ == "__main__":
    main()
