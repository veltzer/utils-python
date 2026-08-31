#!/usr/bin/env python

"""
Print the GCP project id of the application-default credentials.
"""

import google.auth


def main():
    """Main entry point."""
    _, project_id = google.auth.default()
    print(project_id)


if __name__ == "__main__":
    main()
