#!/usr/bin/env python

"""
Print an HTML page of every GCP project the gcloud account can see, with
every string that is meant to be the same as the project ID, what each
project holds and whether billing is on; then the projects pending deletion.

The fleet convention (fleet/docs/gcp-naming.md) is that the project ID is
the only name chosen: the display name, the gcloud configuration, the
.gcp.conf gcp_project= of the repo, the pass(1) folder gcp/<id>, the OAuth
client and the consent screen app are all named after it. Each such cell is
green when it equals the project ID and red when it does not.

Where each string comes from:
- display name: gcloud projects list
- gcloud configuration: ~/.config/gcloud/configurations/config_<name> files
  whose project is this one (CLOUDSDK_CONFIG moves the directory)
- repo: the git checkouts under --git-root whose .gcp.conf names the project
- pass folder: the folder gcp/<id> in the password store (PASSWORD_STORE_DIR)
- OAuth client ID: the client JSON in pass (gcp/<id>/oauth-client) and the
  repos' gcp_oauth_client_id=; it belongs to the project when its number
  prefix is the project number
- consent screen: the app name Google's sign-in page shows for that client.
  Google shows the domain instead of the name for an unverified web app.
The OAuth client's own name is not shown: only the console can read it.

Everything is read-only: gcloud runs with prompts off and an API is queried
only when it is already enabled, so nothing is ever turned on; pass is only
read; the sign-in page is fetched, never submitted.
"""

import argparse
import concurrent.futures
import configparser
import glob
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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
CONF_VALUE = re.compile(r"^(gcp_project|gcp_oauth_client_id|gcp_domain)=(\S+)\s*$", re.MULTILINE)
APP_NAME = re.compile(r'data-app-name="([^"]*)"')
# where a web client of the fleet's apps sends the user back after sign-in
WEB_REDIRECT_PATHS = ["/auth/login", "/auth/oauth/google/callback", "/oauth2callback"]
STYLE = """
body{font-family:system-ui,sans-serif;margin:2rem;color:#222}
table{border-collapse:collapse}
th,td{border:1px solid #ccc;padding:.35rem .55rem;text-align:left;vertical-align:top}
th{background:#f0f0f0;position:sticky;top:0}
td.same{background:#e6f4e6}
td.differs{background:#fbe3e3}
td.note{background:#fdf3d8}
td.none{color:#999}
.mono{font-family:monospace}
.legend span{padding:.1rem .4rem;margin-right:.6rem}
"""


@dataclass
class Repo:
    """A git checkout with a .gcp.conf."""

    name: str
    project: str
    client_id: str | None
    domain: str | None


@dataclass
class Project:
    """One project, as the table shows it."""

    project_id: str
    display_name: str
    number: str
    configs: list[str] = field(default_factory=list)
    repos: list[Repo] = field(default_factory=list)
    pass_kinds: list[str] = field(default_factory=list)
    clients: dict[str, str] = field(default_factory=dict)  # client ID -> where it was found
    consent: dict[str, str] = field(default_factory=dict)  # client ID -> app name shown
    holds: list[str] = field(default_factory=list)
    billing: str = "?"


@dataclass
class Cell:
    """A table cell: its text, and how it compares to the project ID."""

    text: str
    status: str = ""  # same, differs, note, none or ""
    mono: bool = False


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
    """The non-empty lines of a command's output."""
    return [line for line in (output or "").splitlines() if line.strip()]


def read_repos(git_root: str) -> list[Repo]:
    """The repos under git_root with a .gcp.conf that names a project."""
    repos: list[Repo] = []
    for conf in sorted(glob.glob(os.path.join(git_root, "*", ".gcp.conf"))):
        with open(conf, encoding="utf-8") as f:
            values = dict(CONF_VALUE.findall(f.read()))
        if "gcp_project" in values:
            repos.append(
                Repo(
                    name=os.path.basename(os.path.dirname(conf)),
                    project=values["gcp_project"],
                    client_id=values.get("gcp_oauth_client_id"),
                    domain=values.get("gcp_domain"),
                )
            )
    return repos


def read_configs() -> dict[str, list[str]]:
    """Map each project ID to the gcloud configurations that select it."""
    root = os.environ.get("CLOUDSDK_CONFIG") or os.path.expanduser("~/.config/gcloud")
    found: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(root, "configurations", "config_*"))):
        parser = configparser.ConfigParser()
        try:
            parser.read(path, encoding="utf-8")
        except configparser.Error:
            continue
        project = parser.get("core", "project", fallback=None)
        if project:
            found.setdefault(project, []).append(os.path.basename(path).removeprefix("config_"))
    return found


def pass_store() -> str:
    """The password store directory."""
    return os.environ.get("PASSWORD_STORE_DIR") or os.path.expanduser("~/.password-store")


def read_pass_kinds(project_id: str) -> list[str]:
    """The entries of the pass folder gcp/<project_id>, if there is one."""
    folder = os.path.join(pass_store(), "gcp", project_id)
    if not os.path.isdir(folder):
        return []
    return sorted(name.removesuffix(".gpg") for name in os.listdir(folder) if name.endswith(".gpg"))


def pass_client(project_id: str) -> tuple[str, str] | None:
    """The client ID and type (installed or web) of the client JSON in pass."""
    result = subprocess.run(
        ["pass", "show", f"gcp/{project_id}/oauth-client"],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    for kind, client in document.items():
        if isinstance(client, dict) and "client_id" in client:
            return str(client["client_id"]), kind
    return None


def consent_app_name(client_id: str, redirects: list[str]) -> str | None:
    """The app name Google's sign-in page shows for the client, or None."""
    for redirect in redirects:
        query = urllib.parse.urlencode(
            {"client_id": client_id, "redirect_uri": redirect, "response_type": "code", "scope": "email"}
        )
        request = urllib.request.Request(
            f"https://accounts.google.com/o/oauth2/v2/auth?{query}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                page = response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError, TimeoutError:
            continue
        match = APP_NAME.search(page)
        if match is not None:
            return html.unescape(match.group(1))
    return None


def describe(project: Project) -> Project:
    """Fill in the OAuth strings, what the project holds and its billing state."""
    pid = project.project_id
    project.pass_kinds = read_pass_kinds(pid)
    redirects: dict[str, list[str]] = {}
    if "oauth-client" in project.pass_kinds:
        found = pass_client(pid)
        if found is not None:
            client_id, kind = found
            project.clients[client_id] = "pass"
            redirects[client_id] = ["http://localhost"] if kind == "installed" else []
    for repo in project.repos:
        if repo.client_id:
            project.clients.setdefault(repo.client_id, f"{repo.name}/.gcp.conf")
            if repo.domain:
                redirects.setdefault(repo.client_id, []).extend(f"https://{repo.domain}{path}" for path in WEB_REDIRECT_PATHS)
    for client_id in project.clients:
        name = consent_app_name(client_id, redirects.get(client_id) or ["http://localhost"])
        if name is not None:
            project.consent[client_id] = name

    enabled = {
        name.removesuffix(".googleapis.com")
        for name in lines(gcloud("services", "list", "--enabled", "--project", pid, "--format=value(config.name)"))
    }
    billing = gcloud("billing", "projects", "describe", pid, "--format=value(billingEnabled)")
    project.billing = {"True": "on", "False": "off"}.get(billing or "", "?")
    if "run" in enabled:
        mappings = lines(
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
        for service in lines(gcloud("run", "services", "list", "--project", pid, "--format=value(metadata.name)")):
            names = ", ".join(m.split("\t")[0] for m in mappings if m.endswith(f"\t{service}"))
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
        project.holds.append("could not list its APIs")
    return project


def compared(values: list[str], project_id: str) -> Cell:
    """A cell listing strings that should equal the project ID."""
    if not values:
        return Cell("-", "none")
    return Cell(", ".join(values), "same" if all(v == project_id for v in values) else "differs", mono=True)


def consent_cell(project: Project) -> Cell:
    """The app names the consent screen shows."""
    if not project.clients:
        return Cell("-", "none")
    names = [project.consent.get(client_id, "?") for client_id in project.clients]
    if all(name == project.project_id for name in names):
        return Cell(", ".join(names), "same", mono=True)
    if all("." in name for name in names):
        return Cell(", ".join(names) + " (the domain: shown for an unverified web app)", "note", mono=True)
    return Cell(", ".join(names), "differs", mono=True)


def client_cell(project: Project) -> Cell:
    """The OAuth client IDs, and whether they belong to the project."""
    if not project.clients:
        return Cell("-", "none")
    parts = []
    owned = True
    for client_id, source in project.clients.items():
        number = client_id.split("-", 1)[0]
        owned = owned and number == project.number
        parts.append(f"{number}-… ({source})")
    return Cell(", ".join(parts), "same" if owned else "differs", mono=True)


def table(headers: list[str], rows: list[list[Cell]]) -> str:
    """An HTML table; every cell is escaped."""
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        cells = []
        for cell in row:
            classes = " ".join(c for c in (cell.status, "mono" if cell.mono else "") if c)
            attribute = f' class="{classes}"' if classes else ""
            cells.append(f"<td{attribute}>{html.escape(cell.text)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n" + "\n".join(body) + "\n</tbody>\n</table>"


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
    listing = gcloud("projects", "list", "--format=value(projectId,name,projectNumber)")
    deleting = gcloud("projects", "list", "--filter=lifecycleState:DELETE_REQUESTED", "--format=value(projectId)")
    if listing is None or deleting is None:
        print("gcp_projects_table: gcloud could not list the projects; is it logged in?", file=sys.stderr)
        raise SystemExit(1)
    repos = read_repos(args.git_root)
    configs = read_configs()
    active = []
    for line in sorted(lines(listing)):
        pid, name, number = [*line.split("\t"), "", ""][:3]
        active.append(
            Project(
                project_id=pid,
                display_name=name,
                number=number,
                configs=configs.get(pid, []),
                repos=[repo for repo in repos if repo.project == pid],
            )
        )
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        projects = list(pool.map(describe, active))
    pending = sorted(lines(deleting))

    rows = [
        [
            Cell(p.project_id, mono=True),
            compared([p.display_name], p.project_id),
            compared(p.configs, p.project_id),
            Cell(", ".join(repo.name for repo in p.repos) or "-", "" if p.repos else "none"),
            Cell(f"gcp/{p.project_id} ({', '.join(p.pass_kinds)})", "same", mono=True) if p.pass_kinds else Cell("-", "none"),
            consent_cell(p),
            client_cell(p),
            Cell("; ".join(p.holds) or "nothing but the default APIs"),
            Cell(p.billing),
        ]
        for p in projects
    ]
    print("<!DOCTYPE html>")
    print('<html lang="en"><head><meta charset="utf-8"><title>GCP projects</title>')
    print(f"<style>{STYLE}</style></head><body>")
    print(
        '<p class="legend"><span class="same" style="background:#e6f4e6">equals the project ID</span>'
        '<span style="background:#fbe3e3">differs</span>'
        '<span style="background:#fdf3d8">Google shows something else</span>'
        '<span style="color:#999">- none</span></p>'
    )
    print(f"<h2>Active projects ({len(projects)})</h2>")
    print(
        table(
            [
                "Project ID",
                "Display name",
                "gcloud configuration",
                "Repo (.gcp.conf)",
                "pass folder",
                "Consent screen shows",
                "OAuth client (project number, source)",
                "Holds",
                "Billing",
            ],
            rows,
        )
    )
    print(f"<h2>Pending deletion ({len(pending)})</h2>")
    still_named = {pid: [repo.name for repo in repos if repo.project == pid] for pid in pending}
    print(
        table(
            ["Project ID", "Repo still naming it", "gcloud configuration", "pass folder"],
            [
                [
                    Cell(pid, mono=True),
                    Cell(", ".join(still_named[pid]) or "-", "differs" if still_named[pid] else "none"),
                    Cell(", ".join(configs.get(pid, [])) or "-", "differs" if configs.get(pid) else "none"),
                    Cell(f"gcp/{pid}", "differs") if read_pass_kinds(pid) else Cell("-", "none"),
                ]
                for pid in pending
            ],
        )
    )
    print("</body></html>")


if __name__ == "__main__":
    main()
