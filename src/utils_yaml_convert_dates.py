#!/usr/bin/env python3
"""
Convert date/time fields in YAML from local time format to UTC timestamp and timezone.

Usage:
    python convert_yaml_dates.py file1.yaml file2.yaml ...
    python convert_yaml_dates.py *.yaml

Example:
    python convert_yaml_dates.py events.yaml meetings.yaml
    python convert_yaml_dates.py data/*.yaml
"""

import re
import sys
from typing import Tuple

import pytz
import yaml
from dateutil import parser


class DateTimeParseError(ValueError):
    """Raised when datetime string cannot be parsed"""


class TimezoneError(ValueError):
    """Raised when timezone is unknown or invalid"""


def parse_datetime_string(dt_string: str) -> Tuple[str, str]:
    """
    Parse datetime string like "Sat 07 Jun 2025 22:57:54 IDT"
    Returns: (utc_timestamp, timezone_name)
    """
    try:
        # Use dateutil.parser which handles many formats and timezones automatically
        dt = parser.parse(dt_string)

        # Check if timezone was parsed
        if dt.tzinfo is None:
            raise TimezoneError(f"No timezone information found in: {dt_string}")

        # Get the timezone name
        if hasattr(dt.tzinfo, 'zone'):
            timezone_name = dt.tzinfo.zone
        elif hasattr(dt.tzinfo, 'tzname'):
            timezone_name = dt.tzinfo.tzname(dt)
        else:
            # For offset-based timezones, create a name from the offset
            utc_offset = dt.utcoffset()
            if utc_offset:
                total_seconds = int(utc_offset.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                timezone_name = f"UTC{hours:+03d}:{minutes:02d}"
            else:
                timezone_name = "UTC"

        # Convert to UTC
        dt_utc = dt.astimezone(pytz.UTC)

        # Format as ISO 8601 with Z suffix
        utc_timestamp = dt_utc.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

        return utc_timestamp, timezone_name
    except parser.ParserError as e:
        raise DateTimeParseError(f"Cannot parse datetime '{dt_string}': {e}") from e
    except ValueError as e:
        raise DateTimeParseError(f"Invalid datetime format '{dt_string}': {e}") from e
    except Exception as e:
        raise TimezoneError(f"Error processing timezone for '{dt_string}': {e}") from e


def is_datetime_field(value) -> bool:
    """Check if a value looks like our datetime format"""
    if not isinstance(value, str):
        return False
    # Pattern for "Sat 07 Jun 2025 22:57:54 IDT"
    pattern = r'^[A-Za-z]{3}\s+\d{2}\s+[A-Za-z]{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+[A-Z]{3,4}$'
    return bool(re.match(pattern, value))


def convert_datetime_fields(data):
    """
    Recursively convert datetime fields in the data structure.
    For each datetime field found, create two new fields:
    - original_field_name + '_timestamp_utcz'
    - original_field_name + '_timezone'
    And remove the original field.
    """
    if isinstance(data, dict):
        keys_to_remove = []
        items_to_add = {}

        for key, value in data.items():
            if is_datetime_field(value):
                try:
                    utc_timestamp, timezone = parse_datetime_string(value)
                    keys_to_remove.append(key)
                    items_to_add[f"{key}_timestamp_utcz"] = utc_timestamp
                    items_to_add[f"{key}_timezone"] = timezone
                    print(f"  Converted {key}: {value} -> {utc_timestamp} ({timezone})")
                except (DateTimeParseError, TimezoneError) as e:
                    print(f"  Warning: Skipping {key}: {e}")
            elif isinstance(value, (dict, list)):
                convert_datetime_fields(value)

        # Apply changes
        for key in keys_to_remove:
            del data[key]
        data.update(items_to_add)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                convert_datetime_fields(item)


def process_file(file_path: str):
    """Process a single YAML file."""
    print(f"Processing: {file_path}")

    # Load YAML
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Convert datetime fields
    convert_datetime_fields(data)

    # Save converted YAML
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print("Done")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Expand file patterns
    file_paths = sys.argv[1:]
    if not file_paths:
        print("No files found")
        sys.exit(1)

    # Process files
    for file_path in file_paths:
        process_file(file_path)


if __name__ == "__main__":
    main()
