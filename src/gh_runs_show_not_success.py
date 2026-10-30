#!/usr/bin/env python

"""
Show every repository whose default branch is not green on GitHub.

Instead of walking repos -> workflows -> runs over REST (one call per
workflow), this lists the repos with one REST call and then asks GraphQL
for the statusCheckRollup of each repo's default-branch head commit.

Resolving a rollup is slow on GitHub's side (~4.5s for 50 repos), and
cursor pagination would make the pages run one after another. So the
repos are split into small batches, each batch is a single query with one
aliased `repository` field per repo, and the batches run in parallel.
Repos that come back anything but SUCCESS then get one more query each,
also in parallel, to name the workflows behind the state.

Only the head commit of the default branch is looked at: a failed run on
another branch, or a scheduled run on an older commit, does not show.
Repos with no checks at all are skipped.

Uses the `gh` CLI for authentication and API calls.
"""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# repos per GraphQL query; measured fastest at around 10
BATCH_SIZE = 10
# queries in flight at once, well below GitHub's concurrency limits
WORKERS = 26

ROLLUP_FIELD = """
r{index}: repository(owner: {owner}, name: {name}) {{
  nameWithOwner
  defaultBranchRef {{ target {{ ... on Commit {{ statusCheckRollup {{ state }} }} }} }}
}}
"""

SUITES_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          checkSuites(first: 50) {
            nodes {
              status
              conclusion
              workflowRun { url workflow { name } }
            }
          }
        }
      }
    }
  }
}
"""


def gh(*args):
    """Run the gh CLI and return its stdout."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def gh_graphql(query, variables=None):
    """Run a GraphQL query via the gh CLI, return its data."""
    cmd = ["api", "graphql", "-f", f"query={query}"]
    for key, value in (variables or {}).items():
        cmd.extend(["-f", f"{key}={value}"])
    return json.loads(gh(*cmd))["data"]


def get_repos():
    """Return owner/name of every non-fork repository the user owns."""
    out = gh(
        "api",
        "--paginate",
        "user/repos?affiliation=owner&per_page=100",
        "--jq",
        ".[] | select(.fork | not) | .full_name",
    )
    return out.split()


def get_rollups(batch):
    """Return [(nameWithOwner, state)] for a batch; state is None without checks."""
    fields = []
    for index, name_with_owner in enumerate(batch):
        owner, name = name_with_owner.split("/", 1)
        # json.dumps gives a correctly quoted GraphQL string literal
        fields.append(ROLLUP_FIELD.format(index=index, owner=json.dumps(owner), name=json.dumps(name)))
    data = gh_graphql("query {" + "".join(fields) + "}")
    rollups = []
    for node in data.values():
        ref = node["defaultBranchRef"]
        rollup = ref and ref["target"].get("statusCheckRollup")
        rollups.append((node["nameWithOwner"], rollup and rollup["state"]))
    return rollups


def get_bad_suites(name_with_owner):
    """Return [(workflow name, status/conclusion, url)] for non-successful suites."""
    owner, name = name_with_owner.split("/", 1)
    data = gh_graphql(SUITES_QUERY, {"owner": owner, "name": name})
    suites = []
    for suite in data["repository"]["defaultBranchRef"]["target"]["checkSuites"]["nodes"]:
        run = suite["workflowRun"]
        # GitHub creates an empty, never-run suite for every installed app;
        # without a workflow run behind it, it tells us nothing
        if run is None or suite["conclusion"] in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            continue
        suites.append((run["workflow"]["name"], suite["conclusion"] or suite["status"], run["url"]))
    return suites


def main():
    repos = get_repos()
    batches = [repos[i:i + BATCH_SIZE] for i in range(0, len(repos), BATCH_SIZE)]
    with ThreadPoolExecutor(WORKERS) as executor:
        rollups = [rollup for result in executor.map(get_rollups, batches) for rollup in result]
        bad = sorted((name, state) for name, state in rollups if state not in (None, "SUCCESS"))
        details = executor.map(get_bad_suites, [name for name, _ in bad])
        for (name_with_owner, state), suites in zip(bad, details):
            print(f"{name_with_owner}: {state}")
            for workflow, suite_state, url in suites:
                print(f"    {workflow}: {suite_state} {url}")
    print(f"{len(bad)} of {len(rollups)} repositories not successful")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"command failed: {' '.join(e.cmd[:3])}\n{e.stderr.strip()}")
