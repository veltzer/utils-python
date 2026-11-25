#!/usr/bin/env python

"""
Print an HTML table of every GCP project the gcloud account can see: the
repo that uses it, what it holds, and whether billing is on, then a second
table of the projects pending deletion.

Everything is read fresh with gcloud, read-only: prompts are off and an API
is queried only when it is already enabled, so nothing is ever turned on.
The repo of a project is the git checkout whose .gcp.conf names it in
gcp_project=. OAuth clients and consent screens are not listed: Google has
no API that lists them.
"""

import argparse
import concurrent.futures
import glob
import html
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field

# APIs worth naming in "holds": they say what a project is for. The many
# others every project has (logging, storage, bigquery...) say nothing.
NOTABLE_APIS = {
    "calendar-json": "Calendar API",
    "people": "People API",
    "contacts": "Contacts API",
    "youtube": "YouTube API",
    "gmail": "Gmail API",
    "generativelanguage": "Gemini API",
    "aiplatform": "Vertex AI API",
    "searchconsole": "Search Console API",
    "identitytoolkit": "Identity Toolkit",
}
REGION = "us-central1"
GCP_PROJECT = re.compile(r"^gcp_project=(\S+)\s*$", re.MULTILINE)


@dataclass
class Project:
    """What one project holds, as the table shows it."""

    project_id: str
    repos: list[str] = field(default_factory=list)
    holds: list[str] = field(default_factory=list)
    billing: str = "?"
    errors: list[str] = field(default_factory=list)


def gcloud(*args: str) -> str | None:
    """Run gcloud read-only and return its output, or None when it failed."""
    env = dict(os.environ, CLOUDSDK_CORE_DISABLE_PROMPTS="1")
    for attempt in range(4):
        result = subprocess.run(
            ["gcloud", *args],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            env=env,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # the billing API allows few requests a minute: wait and retry
        if "RESOURCE_EXHAUSTED" in result.stderr or "429" in result.stderr:
            time.sleep(10 * (attempt + 1))
            continue
        return None
    return None


def lines(output: str | None) -> list[str]:
    """The non-empty lines of a gcloud output."""
    return [line for line in (output or "").splitlines() if line.strip()]


def repos_by_project(git_root: str) -> dict[str, list[str]]:
    """Map each project ID to the repos under git_root whose .gcp.conf names it."""
    found: dict[str, list[str]] = {}
    for conf in sorted(glob.glob(os.path.join(git_root, "*", ".gcp.conf"))):
        with open(conf, encoding="utf-8") as f:
            match = GCP_PROJECT.search(f.read())
        if match is not None:
            repo = os.path.basename(os.path.dirname(conf))
            found.setdefault(match.group(1), []).append(repo)
    return found


def describe(project: Project) -> Project:
    """Fill in what the project holds and its billing state."""
    pid = project.project_id
    enabled = {
        name.removesuffix(".googleapis.com")
        for name in lines(gcloud("services", "list", "--enabled", "--project", pid, "--format=value(config.name)"))
    }
    billing = gcloud("billing", "projects", "describe", pid, "--format=value(billingEnabled)")
    project.billing = {"True": "on", "False": "off"}.get(billing or "", "?")
    if "run" in enabled:
        for service in lines(gcloud("run", "services", "list", "--project", pid, "--format=value(metadata.name)")):
            domains = [
                domain
                for domain in lines(
                    gcloud(
                        "beta",
                        "run",
                        "domain-mappings",
                        "list",
                        "--project",
                        pid,
                        "--region",
                        REGION,
                        "--format=value(metadata.name,spec.routeName)",
                    )
                )
                if domain.endswith(f"\t{service}")
            ]
            names = ", ".join(domain.split("\t")[0] for domain in domains)
            project.holds.append(f"Cloud Run {service}" + (f" ({names})" if names else ", no domain"))
    if "sqladmin" in enabled:
        for instance in lines(gcloud("sql", "instances", "list", "--project", pid, "--format=value(name,state)")):
            name, _, state = instance.partition("\t")
            project.holds.append(f"Cloud SQL {name} ({state.lower()})")
    if "firestore" in enabled or "datastore" in enabled:
        databases = gcloud("firestore", "databases", "list", "--project", pid, "--format=json")
        for database in json.loads(databases or "[]"):
            project.holds.append(f"Firestore ({database.get('type', '?').lower().replace('_', ' ')})")
    if "secretmanager" in enabled:
        secrets = lines(gcloud("secrets", "list", "--project", pid, "--format=value(name)"))
        if secrets:
            project.holds.append(f"{len(secrets)} secret{'s' if len(secrets) != 1 else ''}")
    apis = [label for api, label in NOTABLE_APIS.items() if api in enabled]
    if apis:
        project.holds.append(", ".join(apis))
    policy = gcloud("projects", "get-iam-policy", pid, "--format=json")
    if policy is not None:
        account = gcloud("config", "get-value", "account") or ""
        others = sorted(
            {
                member.removeprefix("user:")
                for binding in json.loads(policy).get("bindings", [])
                for member in binding.get("members", [])
                if member.startswith("user:") and member != f"user:{account}"
            }
        )
        if others:
            project.holds.append("IAM member " + ", ".join(others))
    if not enabled:
        project.errors.append("could not list its APIs")
    return project


def table(headers: list[str], rows: list[list[str]]) -> str:
    """An HTML table; every cell is escaped."""
    head = "".join(f"<th>{html.escape(cell)}</th>" for cell in headers)
    body = "\n".join("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>"


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--git-root",
        default=os.path.expanduser("~/git"),
        help="where the repos with a .gcp.conf live (default: ~/git)",
    )
    parser.add_argument("--jobs", type=int, default=4, help="projects described at once (default: 4)")
    args = parser.parse_args()

    # `projects list` shows the active projects only, unless asked for others
    listing = gcloud("projects", "list", "--format=value(projectId)")
    deleting = gcloud("projects", "list", "--filter=lifecycleState:DELETE_REQUESTED", "--format=value(projectId)")
    if listing is None or deleting is None:
        print("gcp_projects_table: gcloud could not list the projects; is it logged in?", file=sys.stderr)
        raise SystemExit(1)
    repos = repos_by_project(args.git_root)
    active = [Project(pid, repos.get(pid, [])) for pid in sorted(lines(listing))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        projects = list(pool.map(describe, active))
    pending = sorted(lines(deleting))

    print(f"<h2>Active projects ({len(projects)})</h2>")
    print(
        table(
            ["Project", "Repo", "Holds", "Billing"],
            [
                [
                    p.project_id,
                    ", ".join(p.repos) or "-",
                    "; ".join(p.holds + p.errors) or "nothing but the default APIs",
                    p.billing,
                ]
                for p in projects
            ],
        )
    )
    print(f"<h2>Pending deletion ({len(pending)})</h2>")
    print(table(["Project", "Repo (still naming it)"], [[pid, ", ".join(repos.get(pid, [])) or "-"] for pid in pending]))


if __name__ == "__main__":
    main()
