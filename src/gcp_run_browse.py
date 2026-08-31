#!/usr/bin/env python

"""
Open a Cloud Run service of a GCP project in the local web browser.

Lists the Cloud Run services of the project of the application-default
credentials across all regions. With exactly one service (or a service name
argument that narrows it down to one) its URL is printed and opened in the
default browser; with several candidates they are listed instead so a name
can be given.
"""

import argparse
import re
import sys
import webbrowser

import google.auth
from googleapiclient import discovery


def list_services(project_id, credentials):
    """Returns all Cloud Run services of the project, in every region."""
    run = discovery.build("run", "v2", credentials=credentials)
    services = []
    # pylint: disable=no-member
    request = run.projects().locations().services().list(
        parent=f"projects/{project_id}/locations/-"
    )
    while request is not None:
        response = request.execute()
        services.extend(response.get("services", []))
        request = run.projects().locations().services().list_next(
            previous_request=request, previous_response=response
        )
    return services


def short_name(service):
    """Returns the plain service name from the full resource path."""
    return service["name"].rsplit("/", 1)[-1]


def region(service):
    """Returns the region from the full resource path."""
    # projects/<project>/locations/<region>/services/<name>
    return service["name"].split("/")[3]


def service_url(service):
    """
    Returns the URL the service serves traffic on, preferring the
    deterministic project-number form (<name>-<number>.<region>.run.app)
    over the older form with a random tag in the middle.
    """
    pattern = rf"https://{re.escape(short_name(service))}-\d+\.{region(service)}\.run\.app"
    for url in service.get("urls", []):
        if re.fullmatch(pattern, url):
            return url
    return service["uri"]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "service",
        nargs="?",
        help="service name to open (needed only when the project has several)",
    )
    args = parser.parse_args()
    credentials, project_id = google.auth.default()
    services = list_services(project_id, credentials)
    if args.service is not None:
        services = [s for s in services if short_name(s) == args.service]
    if not services:
        wanted = f"service '{args.service}'" if args.service else "services"
        sys.exit(f"No Cloud Run {wanted} in project {project_id}.")
    if len(services) > 1:
        print(f"Project {project_id} has several Cloud Run services, name one:")
        for service in services:
            print(f"  {short_name(service)} ({region(service)}) {service_url(service)}")
        sys.exit(1)
    url = service_url(services[0])
    print(url)
    if not webbrowser.open(url):
        sys.exit("Could not launch a browser; open the url above yourself.")


if __name__ == "__main__":
    main()
