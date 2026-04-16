#!/usr/bin/env python

"""
Delete all but the last N GitHub deployments for a repository.

Uses the `gh` CLI for authentication and API calls.
"""

import json
import subprocess
import sys


def gh_api(endpoint, method="GET", fields=None):
    """Call the GitHub API via the gh CLI."""
    cmd = ["gh", "api", endpoint]
    if method != "GET":
        cmd.extend(["-X", method])
    if fields:
        for key, value in fields.items():
            cmd.extend(["-f", f"{key}={value}"])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.stdout.strip():
        return json.loads(result.stdout)
    return None


def get_all_deployments(repo):
    """Fetch all deployment IDs, newest first."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/deployments", "--paginate", "--jq", ".[].id"],
        capture_output=True, text=True, check=True,
    )
    return [int(line) for line in result.stdout.strip().splitlines() if line.strip()]


def get_latest_deployment_state(repo, deployment_id):
    """Return the most recent status state for a deployment, or None if none exist."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/deployments/{deployment_id}/statuses",
         "--jq", ".[0].state"],
        capture_output=True, text=True, check=True,
    )
    state = result.stdout.strip()
    return state or None


def deactivate_deployment(repo, deployment_id):
    """Set deployment status to inactive so it can be deleted."""
    gh_api(
        f"repos/{repo}/deployments/{deployment_id}/statuses",
        method="POST",
        fields={"state": "inactive"},
    )


def delete_deployment(repo, deployment_id):
    """Delete a deployment."""
    gh_api(f"repos/{repo}/deployments/{deployment_id}", method="DELETE")


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

    print(f"Fetching deployments for {repo}...")
    deployment_ids = get_all_deployments(repo)
    total = len(deployment_ids)
    print(f"Found {total} deployments, keeping {keep} most recent (non-failed).")

    kept = []
    to_delete = []
    failed_states = {"failure", "error"}
    for dep_id in deployment_ids:
        state = get_latest_deployment_state(repo, dep_id)
        if state in failed_states:
            to_delete.append(dep_id)
        elif len(kept) < keep:
            kept.append(dep_id)
        else:
            to_delete.append(dep_id)

    if not to_delete:
        print("Nothing to delete.")
        sys.exit(0)

    print(f"Deleting {len(to_delete)} deployments...")
    for i, dep_id in enumerate(to_delete, 1):
        print(f"  [{i}/{len(to_delete)}] Deactivating and deleting {dep_id}...")
        deactivate_deployment(repo, dep_id)
        delete_deployment(repo, dep_id)

    print("Done.")


if __name__ == "__main__":
    main()
