#!/usr/bin/env python

"""
Rebuild the "my sites" bookmark folder on Chrome's bookmarks bar.

The folder holds every address each deployed web app answers on, so a broken
layer can be told apart from a broken app: the custom domain (DNS, domain
mapping, certificate) next to the run.app urls (the Cloud Run service itself).

Only the repos listed in SITES are walked. For each one the GCP project,
service and region come from the repo's .gcp.conf, and the addresses come live
from gcloud: the service's run.app urls and its domain mappings. Nothing about
a deployment is written down here, so a project move needs no edit.

Every bookmark title says which kind of address it is:

  domain    the canonical custom domain (gcp_domain in .gcp.conf)
  alias     any other domain mapped to the service
  pr#       the run.app url that carries the project number
  old url   the older, hashed run.app url

Bookmarks are written through the chromium-bookmarks MCP server, so Chrome
stays open and the changes sync like any other bookmark edit.

Usage:
  chrome_my_sites.py show                  print the bookmarks it would create
  chrome_my_sites.py sync [--prune]        bring the folder up to date in place
  chrome_my_sites.py refill                empty the folder and fill it again
  chrome_my_sites.py recreate              delete the folder and create it again

sync, refill and recreate take --dry-run.
"""

import argparse
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import IO

FOLDER_TITLE = "my sites"
BOOKMARKS_BAR_ID = "1"
GIT_ROOT = Path.home() / "git"


@dataclass(frozen=True)
class Site:
    """A repo that deploys a web app to Cloud Run, and the path to open on it."""

    repo: str
    path: str = "/"


# The repos whose web apps go into the folder, in folder order. Repos that
# deploy no web app (gcp-calendar, gcp-gemini) are left out on purpose.
SITES = [
    Site("gcp-nikuda"),
    Site("gcp-miflaga"),
    Site("gcp-randomizer"),
    Site("gcp-myworld"),
    Site("gcp-machines"),
    Site("gcp-shareit", path="/shares"),
    Site("gcp-nlpsearch"),
]

# Bookmarks that are not Cloud Run services: the personal homepage, on its
# custom domain and on GitHub Pages. They go first.
STATIC_BOOKMARKS = [
    ("homepage (domain)", "https://veltzer.org/en/"),
    ("homepage (github pages)", "https://veltzer.github.io/"),
]

COMMANDS = {
    "show": "print the bookmarks the folder should hold, change nothing",
    "sync": "bring the folder up to date in place: add, rename and reorder",
    "refill": "keep the folder, delete everything in it and fill it again",
    "recreate": "delete the folder and create it again at the same position",
}


@dataclass(frozen=True)
class Bookmark:
    title: str
    url: str


# ─── reading JSON without Any ────────────────────────────────────────────────


def as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"expected a JSON object, got {value!r}")
    return {str(k): v for k, v in value.items()}


def as_list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"expected a JSON array, got {value!r}")
    return list(value)


def as_str(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"expected a JSON string, got {value!r}")
    return value


# ─── what the folder should hold ─────────────────────────────────────────────


def read_gcp_conf(repo: str) -> dict[str, str]:
    """Read the plain key=value assignments of a repo's .gcp.conf (a bash file)."""
    conf: dict[str, str] = {}
    path = GIT_ROOT / repo / ".gcp.conf"
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("#") or "=" not in line or line.endswith("("):
            continue
        key, value = line.split("=", 1)
        conf[key] = value.strip("\"'")
    return conf


def gcloud_json(args: list[str]) -> object:
    result = subprocess.run(["gcloud", *args, "--format=json"], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def site_bookmarks(site: Site) -> list[Bookmark]:
    conf = read_gcp_conf(site.repo)
    project = conf["gcp_project"]
    service = conf["gcp_service"]
    region = conf["gcp_region"]
    domain = conf.get("gcp_domain", "")
    location = ["--project", project, "--region", region]

    described = as_dict(gcloud_json(["run", "services", "describe", service, *location]))
    annotations = as_dict(as_dict(described["metadata"])["annotations"])
    run_urls = [as_str(u) for u in as_list(json.loads(as_str(annotations["run.googleapis.com/urls"])))]
    mappings = [as_dict(m) for m in as_list(gcloud_json(["beta", "run", "domain-mappings", "list", *location]))]
    mapped = sorted(
        as_str(as_dict(m["metadata"])["name"]) for m in mappings if as_str(as_dict(m["spec"])["routeName"]) == service
    )

    entries: list[tuple[str, str]] = []
    if domain in mapped:
        entries.append(("domain", f"https://{domain}"))
    entries.extend(("alias", f"https://{host}") for host in mapped if host != domain)
    # The project number form ends in .<region>.run.app; the older form is
    # hashed and ends in .a.run.app.
    entries.extend(("pr#", url) for url in run_urls if url.endswith(f".{region}.run.app"))
    entries.extend(("old url", url) for url in run_urls if not url.endswith(f".{region}.run.app"))
    path = site.path if site.path.startswith("/") else f"/{site.path}"
    return [Bookmark(f"{service} ({kind})", f"{url.rstrip('/')}{path}") for kind, url in entries]


def wanted_bookmarks() -> list[Bookmark]:
    """Every bookmark the folder should hold, in order. gcloud runs in parallel."""
    with ThreadPoolExecutor(max_workers=len(SITES)) as pool:
        per_site = list(pool.map(site_bookmarks, SITES))
    wanted = [Bookmark(title, url) for title, url in STATIC_BOOKMARKS]
    for bookmarks in per_site:
        wanted.extend(bookmarks)
    return wanted


# ─── talking to the bookmarks MCP server ─────────────────────────────────────


def server_command() -> list[str]:
    bun = shutil.which("bun") or str(Path.home() / "install" / "binaries" / "bun")
    server = Path.home() / "install" / "chromium-bookmarks-mcp" / "apps" / "mcp-server" / "dist" / "index.js"
    return [bun, str(server)]


class BookmarksServer:
    """A minimal MCP client over stdio: initialize once, then call tools."""

    def __init__(self) -> None:
        self.process = subprocess.Popen(
            server_command(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        self.next_id = 0
        self.request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "chrome_my_sites", "version": "1"},
        })
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def pipes(self) -> tuple[IO[str], IO[str]]:
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("the bookmarks server has no pipes")
        return self.process.stdin, self.process.stdout

    def send(self, message: dict[str, object]) -> None:
        stdin, _ = self.pipes()
        stdin.write(json.dumps(message) + "\n")
        stdin.flush()

    def request(self, method: str, params: dict[str, object]) -> dict[str, object]:
        self.next_id += 1
        self.send({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params})
        _, stdout = self.pipes()
        while True:
            line = stdout.readline()
            if not line:
                raise RuntimeError("the bookmarks server exited")
            reply = as_dict(json.loads(line))
            if reply.get("id") != self.next_id:
                continue
            if "error" in reply:
                raise RuntimeError(f"{method} failed: {reply['error']}")
            return as_dict(reply["result"])

    def call(self, tool: str, arguments: dict[str, object]) -> object:
        result = self.request("tools/call", {"name": tool, "arguments": arguments})
        text = as_str(as_dict(as_list(result["content"])[0])["text"])
        if result.get("isError"):
            raise RuntimeError(f"{tool} failed: {text}")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    def children(self, folder_id: str) -> list[dict[str, object]]:
        listing = as_dict(self.call("bookmark_list", {"folder_id": folder_id, "limit": 1000}))
        return [as_dict(item) for item in as_list(listing["items"])]

    def close(self) -> None:
        self.process.terminate()
        self.process.wait()


def find_folder(server: BookmarksServer) -> tuple[str | None, int | None]:
    """The id and bar position of the folder, or (None, None) when it is absent."""
    for item in server.children(BOOKMARKS_BAR_ID):
        if item.get("type") == "folder" and item.get("title") == FOLDER_TITLE:
            index = item["index"]
            return as_str(item["id"]), index if isinstance(index, int) else None
    return None, None


def create_folder(server: BookmarksServer, index: int | None) -> str:
    arguments: dict[str, object] = {"title": FOLDER_TITLE, "parent_id": BOOKMARKS_BAR_ID}
    if index is not None:
        arguments["index"] = index
    return as_str(as_dict(server.call("bookmark_create", arguments))["id"])


def fill(server: BookmarksServer, folder_id: str, wanted: list[Bookmark], *, dry_run: bool) -> None:
    for index, bookmark in enumerate(wanted):
        print(f"add    {bookmark.title:28} {bookmark.url}")
        if not dry_run:
            server.call("bookmark_create", {
                "title": bookmark.title,
                "url": bookmark.url,
                "parent_id": folder_id,
                "index": index,
            })


def empty(server: BookmarksServer, folder_id: str, *, dry_run: bool) -> None:
    items = server.children(folder_id)
    for item in items:
        print(f"delete {as_str(item.get('title', '')):28} {as_str(item.get('url', '<folder>'))}")
    if dry_run:
        return
    bookmark_ids = [as_str(item["id"]) for item in items if item.get("type") != "folder"]
    if bookmark_ids:
        server.call("bookmark_batch_delete", {"ids": bookmark_ids, "confirm": True})
    for item in items:
        if item.get("type") == "folder":
            server.call("bookmark_delete_folder", {"id": as_str(item["id"]), "confirm": True})


def normalize(url: str) -> str:
    return url.rstrip("/")


def sync(server: BookmarksServer, folder_id: str, wanted: list[Bookmark], *, prune: bool, dry_run: bool) -> None:
    """Match existing bookmarks to wanted ones by url; fix titles and order, add the missing."""
    existing = [item for item in server.children(folder_id) if item.get("type") != "folder"]
    by_url = {normalize(as_str(item["url"])): item for item in existing}
    used: set[str] = set()
    # Placing each wanted bookmark at its index in turn only ever moves a
    # bookmark up, since every position before it already holds a wanted one.
    for index, bookmark in enumerate(wanted):
        item = by_url.get(normalize(bookmark.url))
        if item is None:
            print(f"add    {bookmark.title:28} {bookmark.url}")
            if not dry_run:
                server.call("bookmark_create", {
                    "title": bookmark.title,
                    "url": bookmark.url,
                    "parent_id": folder_id,
                    "index": index,
                })
            continue
        item_id = as_str(item["id"])
        used.add(item_id)
        if item.get("title") != bookmark.title:
            print(f"rename {as_str(item['title']):28} -> {bookmark.title}")
            if not dry_run:
                server.call("bookmark_update", {"id": item_id, "title": bookmark.title})
        if item.get("index") != index and not dry_run:
            server.call("bookmark_move", {"id": item_id, "parent_id": folder_id, "index": index})
    extras = [item for item in existing if as_str(item["id"]) not in used]
    for item in extras:
        verb = "delete" if prune else "keep  "
        print(f"{verb} {as_str(item['title']):28} {as_str(item['url'])}  (not an address of a listed site)")
    if prune and extras and not dry_run:
        server.call("bookmark_batch_delete", {"ids": [as_str(item["id"]) for item in extras], "confirm": True})


# ─── command line ────────────────────────────────────────────────────────────


def print_commands(prog: str) -> None:
    print(f"usage: {prog} <command>\n\ncommands:")
    for name, description in COMMANDS.items():
        print(f"  {name:10} {description}")
    print(f"\nRun '{prog} <command> --help' for the options.")


def parse_args(prog: str, argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=prog, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", metavar="<command>")
    commands.add_parser("show", help=COMMANDS["show"])
    for name in ("sync", "refill", "recreate"):
        sub = commands.add_parser(name, help=COMMANDS[name])
        sub.add_argument("--dry-run", action="store_true", help="print what would change, change nothing")
        if name == "sync":
            sub.add_argument("--prune", action="store_true", help="also delete bookmarks that are no listed site's address")
    return parser.parse_args(argv)


def main() -> int:
    prog = Path(sys.argv[0]).name
    argv = sys.argv[1:]
    # Without a command word, list the commands - also when only options were given.
    if not any(arg in COMMANDS for arg in argv) and not {"-h", "--help"} & set(argv):
        print_commands(prog)
        return 2
    args = parse_args(prog, argv)
    wanted = wanted_bookmarks()
    if args.command == "show":
        for bookmark in wanted:
            print(f"{bookmark.title:28} {bookmark.url}")
        return 0

    dry_run: bool = args.dry_run
    if dry_run:
        print("dry run: nothing is changed")
    server = BookmarksServer()
    try:
        folder_id, folder_index = find_folder(server)
        if args.command == "recreate" and folder_id is not None:
            print(f"delete folder [{FOLDER_TITLE}]")
            if not dry_run:
                server.call("bookmark_delete_folder", {"id": folder_id, "confirm": True})
            folder_id = None
        if folder_id is None:
            print(f"create folder [{FOLDER_TITLE}] on the bookmarks bar")
            folder_id = "<new>" if dry_run else create_folder(server, folder_index)
            fill(server, folder_id, wanted, dry_run=dry_run)
        elif args.command == "refill":
            empty(server, folder_id, dry_run=dry_run)
            fill(server, folder_id, wanted, dry_run=dry_run)
        else:
            sync(server, folder_id, wanted, prune=args.prune, dry_run=dry_run)
    finally:
        server.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
