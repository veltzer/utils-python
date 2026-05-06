#!/usr/bin/env python

"""
Clean up GitHub deployments, releases, and workflow runs for a repository.

Keeps only the last N most recent (non-failed) of each, deleting the rest.
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


def get_repo():
    """Get the current repo's owner/name from gh."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


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


def get_all_workflow_runs(repo):
    """Fetch all workflow runs as (id, conclusion) pairs, newest first."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/actions/runs", "--paginate",
         "--jq", r'.workflow_runs[] | "\(.id) \(.conclusion // "")"'],
        capture_output=True, text=True, check=True,
    )
    runs = []
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split(" ", 1)
        run_id = int(parts[0])
        conclusion = parts[1] if len(parts) > 1 else ""
        runs.append((run_id, conclusion))
    return runs


def delete_workflow_run(repo, run_id):
    """Delete a workflow run."""
    gh_api(f"repos/{repo}/actions/runs/{run_id}", method="DELETE")


def clean_deployments(repo, keep):
    print("\n=== Deployments ===")
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
        return

    print(f"Deleting {len(to_delete)} deployments...")
    for i, dep_id in enumerate(to_delete, 1):
        deactivate_deployment(repo, dep_id)
        delete_deployment(repo, dep_id)
        print(f"  [{i}/{len(to_delete)}] Deleted deployment {dep_id}")


def clean_releases(repo, keep):
    print("\n=== Releases ===")
    print(f"Fetching releases for {repo}...")
    release_ids = get_all_release_ids(repo)
    total = len(release_ids)
    print(f"Found {total} releases, keeping {keep} most recent.")

    to_delete = release_ids[keep:]
    if not to_delete:
        print("Nothing to delete.")
        return

    print(f"Deleting {len(to_delete)} releases...")
    for i, release_id in enumerate(to_delete, 1):
        delete_release(repo, release_id)
        print(f"  [{i}/{len(to_delete)}] Deleted release {release_id}")


def clean_workflows(repo, keep):
    print("\n=== Workflow runs ===")
    print(f"Fetching workflow runs for {repo}...")
    runs = get_all_workflow_runs(repo)
    total = len(runs)
    print(f"Found {total} workflow runs, keeping {keep} most recent (non-failed).")

    kept = []
    to_delete = []
    failed_conclusions = {"failure", "cancelled", "timed_out", "startup_failure", "action_required"}
    for run_id, conclusion in runs:
        if conclusion in failed_conclusions:
            to_delete.append(run_id)
        elif len(kept) < keep:
            kept.append(run_id)
        else:
            to_delete.append(run_id)

    if not to_delete:
        print("Nothing to delete.")
        return

    print(f"Deleting {len(to_delete)} workflow runs...")
    for i, run_id in enumerate(to_delete, 1):
        delete_workflow_run(repo, run_id)
        print(f"  [{i}/{len(to_delete)}] Deleted workflow run {run_id}")


def main():
    repo = get_repo()
    keep = 4
    if len(sys.argv) > 1:
        keep = int(sys.argv[1])

    clean_deployments(repo, keep)
    clean_releases(repo, keep)
    clean_workflows(repo, keep)

    print("\nDone.")


if __name__ == "__main__":
    main()
