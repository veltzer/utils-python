#!/usr/bin/env python3

"""
https://medium.com/@ewertonjordao/github-actions-how-to-remove-all-failed-actions-pwsh-github-api-93de9c2cfe46
This script finds which workflows in you github accounts are failing and deletes them.
"""

import os.path
import configparser
import github

inifile = os.path.expanduser("~/.details.ini")
config = configparser.ConfigParser()
config.read(inifile)

# all of our github secret info
opt_username = config.get("github", "username")
opt_password = config.get("github", "password")
opt_personal_token = config.get("github", "personal_token")


def delete(workflow_run):
    # stolen from
    # https://github.com/PyGithub/PyGithub/blob/master/github/WorkflowRun.py
    # which is not yet in released
    # pylint: disable=protected-access
    status, _, _ = workflow_run._requester.requestJson("DELETE", workflow_run.url)
    return status == 204


g = github.Github(login_or_token=opt_personal_token)
for repo in g.get_user(opt_username).get_repos():
    for workflow in repo.get_workflows():
        for run in workflow.get_runs():
            print(f"inspecting {repo.name} {workflow.name} {run.conclusion}")
            delete_it = False
            # if it's a pages build delete it unless it's in mid work (run.conclusion is None)
            if workflow.name == "pages-build-deployment" and run.conclusion is not None:
                delete_it = True
            # if it's not a paged build and it failed then delete it
            if workflow.name != "pages-build-deployment" and run.conclusion == "failure":
                delete_it = True
            if delete_it:
                print(f"deleting {repo.name} {workflow.name} {run.conclusion}")
                delete(run)
