#!/usr/bin/python3

"""
This script runs 'make' (make(1)) in every project
that is mine.
"""

import os
import os.path
import subprocess
import sys
import yaml

home = os.getenv("HOME")
print_all = True
stop_on_fail = False


def run_check_string(args, string, string_to_print=None, do_exit=False, do_print=False):
    """this method runs make and checks that the output does not have lines with warnings in them"""
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        res_out, res_err = p.communicate()
    res_out = res_out.decode()
    res_err = res_err.decode()
    error = False
    error_code = p.returncode
    if p.returncode:
        error = True
    if any(line.find(string) > 0 for line in res_err.split()):
        error = True
        error_code = 1
    if error:
        if string_to_print:
            print(string_to_print)
        if do_print:
            print(res_out, file=sys.stderr, end="")
            print(res_err, file=sys.stderr, end="")
        if do_exit:
            sys.exit(p.returncode)
    return error_code


def run_empty_output(args, string_to_print=None, do_exit=False, do_print=False):
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        res_out, res_err = p.communicate()
    res_out = res_out.decode()
    res_err = res_err.decode()
    if p.returncode or res_out != "" or res_err != "":
        if string_to_print:
            print(string_to_print)
        if do_print:
            print(res_out, file=sys.stderr, end="")
            print(res_err, file=sys.stderr, end="")
        if do_exit:
            sys.exit(p.returncode)
    return p.returncode


def get_projects():
    # projects=[(repo.name, os.path.join(home,'git',repo.name)) for repo in utils.github.get_nonforked_repos_list()]
    projects = []
    filename = os.path.expanduser("~/.mrconfig")
    with open(filename) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("["):
                project_root = os.path.join(home, line[1:-1])
                project_name = line[1:-1].split("/")[-1]
                projects.append((project_name, project_root))
    return projects


def do_stats(code, events):
    if code:
        print("ERROR")
        events["error"] += 1
        if stop_on_fail:
            sys.exit(code)
    else:
        print("OK")
        events["ok"] += 1


def main():
    projects = get_projects()
    project_options_file = os.path.expanduser("~/.mroptions.yaml")
    if os.path.isfile(project_options_file):
        with open(project_options_file) as f:
            opts = yaml.safe_load(f)
    else:
        opts = {}

    events = {
        "error": 0,
        "ok": 0,
        "makefile": 0,
    }
    for project_name, project_root in projects:
        if not os.path.isdir(project_root):
            continue
        string_to_print = f"building [{project_name}] at [{project_root}]..."
        if print_all:
            print(string_to_print, end="")
            sys.stdout.flush()
        makefile = os.path.join(project_root, "Makefile")
        bootstrap = os.path.join(project_root, "bootstrap")
        if os.path.isfile(makefile):
            os.chdir(project_root)
            check_empty_output = True
            if project_name in opts:
                if "dont_check_empty_output" in opts[project_name]:
                    check_empty_output = False
            if check_empty_output:
                code = run_empty_output(["make"])
                do_stats(code, events)
            else:
                code = run_check_string(["make"], string="warning")
                do_stats(code, events)
            # os.system('make')
        elif os.path.isfile(bootstrap):
            os.chdir(project_root)
            code = run_empty_output(["./bootstrap"])
            do_stats(code, events)
            code = run_empty_output(["./configure"])
            do_stats(code, events)
            code = run_empty_output(["make"])
            do_stats(code, events)
            print("OK")
        else:
            # print(f"dont know how to build [{project_name}]...")
            print("MAKEFILE NOT FOUND")
            events["makefile"] += 1

    print(f"events [{events}]")


main()
