#!/usr/bin/env python

"""
Checks used by test.py.

Each check is a function taking no arguments and returning a list of problem
strings, empty when the check passes. They are deliberately shallow: this is a
smoke test, meant to catch a broken layout (an import that no longer resolves,
a shebang that was missed, a generated file that drifted from its source), not
to verify what any individual script computes.
"""

import ast
import os
import os.path
import subprocess
import sys
import tomllib

# realpath, not abspath: these scripts are installed as symlinks into
# ~/.local/bin, and the checks are about the checkout they point back into.
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SRC = os.path.join(ROOT, "src")
SCRIPTS = os.path.join(ROOT, "scripts")
SHEBANG = "#!/usr/bin/env python"
# packages under src that the scripts beside them import
PACKAGES = ["download", "imap", "jack_pulse"]


def python_files(folder: str) -> list[str]:
    """every .py file directly in folder, sorted, excluding caches"""
    if not os.path.isdir(folder):
        return []
    return sorted(
        os.path.join(folder, entry)
        for entry in os.listdir(folder)
        if entry.endswith(".py") and "__pycache__" not in entry
    )


def first_line(path: str) -> str:
    """the first line of a file, without its newline"""
    with open(path, encoding="utf-8") as stream:
        return stream.readline().rstrip("\n")


def check_packages_importable() -> list[str]:
    """the packages under src must import with only src on sys.path

    This is what makes the scripts in src work without PYTHONPATH: python puts
    a script's own folder first on sys.path, so a package beside it is found.
    """
    problems = []
    for package in PACKAGES:
        folder = os.path.join(SRC, package)
        if not os.path.isdir(folder):
            problems.append(f"missing package folder [{folder}]")
            continue
        code = f"import sys; sys.path.insert(0, {SRC!r}); import {package}"
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            last = result.stderr.strip().split("\n")[-1]
            problems.append(f"cannot import [{package}]: {last}")
    return problems


def check_shebangs() -> list[str]:
    """every executable script must start with the one agreed shebang

    Library modules have no shebang and are skipped: they are imported, never
    run. The rule is that a file has a shebang if and only if it is executable.
    """
    problems = []
    for path in python_files(SRC) + python_files(SCRIPTS):
        name = os.path.relpath(path, ROOT)
        line = first_line(path)
        executable = os.access(path, os.X_OK)
        if line.startswith("#!"):
            if line != SHEBANG:
                problems.append(f"wrong shebang in [{name}]: {line}")
            if not executable:
                problems.append(f"has shebang but is not executable [{name}]")
        elif executable:
            problems.append(f"executable but has no shebang [{name}]")
    return problems


def check_deps_in_sync() -> list[str]:
    """pyproject.toml is generated, so its deps must match their source"""
    source = os.path.join(ROOT, "rsconstruct.toml")
    generated = os.path.join(ROOT, "pyproject.toml")
    for path in (source, generated):
        if not os.path.isfile(path):
            return [f"missing [{os.path.relpath(path, ROOT)}]"]
    with open(source, "rb") as stream:
        want = tomllib.load(stream).get("dependencies", {}).get("pip", [])
    with open(generated, "rb") as stream:
        got = tomllib.load(stream).get("project", {}).get("dependencies", [])
    if want != got:
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want))
        return [f"pyproject.toml is stale: missing {missing}, extra {extra}"]
    return []


def check_scripts_parse() -> list[str]:
    """every script must at least be syntactically valid python

    Cheaper and safer than running them: many of these scripts touch the
    network, the desktop or the filesystem, so actually executing them is not
    something a smoke test should do.
    """
    problems = []
    for path in python_files(SRC) + python_files(SCRIPTS):
        name = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as stream:
            text = stream.read()
        try:
            ast.parse(text, filename=path)
        except SyntaxError as error:
            problems.append(f"syntax error in [{name}]: line {error.lineno}: {error.msg}")
    return problems


def check_imports_resolve() -> list[str]:
    """every module a script imports must be importable

    Catches a dependency that is used but missing from the dependency list.
    """
    problems = []
    available = set(sys.stdlib_module_names)
    for package in PACKAGES:
        available.add(package)
    # modules that sit beside a script are found via the script's own folder
    for folder in (SRC, SCRIPTS):
        for path in python_files(folder):
            available.add(os.path.basename(path)[: -len(".py")])
    for path in python_files(SRC) + python_files(SCRIPTS):
        name = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as stream:
            tree = ast.parse(stream.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [node.module.split(".")[0]] if node.level == 0 and node.module else []
            else:
                continue
            for root in roots:
                if root in available:
                    continue
                code = f"import sys; sys.path.insert(0, {SRC!r}); import {root}"
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    available.add(root)
                else:
                    problems.append(f"[{name}] imports [{root}] which is not installed")
                    available.add(root)  # report once, not once per file
    return problems


CHECKS = [
    ("local packages import from src", check_packages_importable),
    ("shebangs are consistent", check_shebangs),
    ("scripts are valid python", check_scripts_parse),
    ("imports are installed", check_imports_resolve),
    ("pyproject.toml matches its source", check_deps_in_sync),
]
