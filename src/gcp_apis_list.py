#!/usr/bin/env python

"""
List all enabled Google Cloud services (APIs) of a GCP project.

By default the project of the application-default credentials is listed;
pass a project id to list another project the credentials can read.
"""

import argparse

import google.auth
from googleapiclient import discovery


def list_enabled_apis(project_id):
    """Print every enabled API of the project, one per line."""
    credentials, default_project = google.auth.default()
    if project_id is None:
        project_id = default_project
    service_usage = discovery.build("serviceusage", "v1", credentials=credentials)
    print(f"Listing enabled APIs for project: {project_id}")
    # pylint: disable=no-member
    request = service_usage.services().list(
        parent=f"projects/{project_id}", filter="state:ENABLED"
    )
    while request is not None:
        response = request.execute()
        for service in response.get("services", []):
            print(service.get("config", {}).get("name", "N/A"))
        request = service_usage.services().list_next(
            previous_request=request, previous_response=response
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_id",
        nargs="?",
        help="project to list (default: the application-default credentials project)",
    )
    args = parser.parse_args()
    list_enabled_apis(args.project_id)


if __name__ == "__main__":
    main()
