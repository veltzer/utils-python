#!/usr/bin/env python

"""
A short script to print all available IANA timezone names.

Requires the `pytz` library to be installed.
To install, run: pip install pytz
"""

import pytz


for tz in sorted(pytz.all_timezones):
    print(tz)
