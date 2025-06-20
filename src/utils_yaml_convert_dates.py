#!/usr/bin/env python
"""
A script for converting date strings within YAML files to UTC "Z" format.

This script is idempotent and targets only YAML elements with a specific key.
Running it multiple times on the same files will not produce further changes.

It processes a list of YAML files provided as command-line arguments.
It recursively finds a specific key (e.g., "start_date") and converts its
string value to a UTC date. It then inserts a new "timezone" key
immediately following it.

Example transformation:
Given the key "start_date", this YAML:
  start_date: Fri Oct 13 11:19:22 IDT 2017
Becomes:
  start_date: "2017-10-13T08:19:22Z"
  timezone: "Asia/Jerusalem"

It uses `ruamel.yaml` to preserve the overall file structure and comments.

Usage:
    python your_script_name.py <key_name> <file1.yaml> [file2.yaml] ...

Requirements:
    pip install ruamel.yaml python-dateutil
"""

import sys
from datetime import timezone
from typing import Any, Dict, Optional, Tuple

# ruamel.yaml is a library specifically designed for round-trip YAML
# processing, which preserves comments and formatting.
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

# dateutil is a powerful third-party library for parsing dates.
from dateutil.parser import parse
from dateutil.parser._parser import ParserError

# --- Configuration ---

# Maps common timezone abbreviations from your data to IANA timezone names.
TIMEZONE_MAP: Dict[str, str] = {
    "IDT": "Asia/Jerusalem",
    "IST": "Asia/Jerusalem",
    # Add other mappings here if needed, e.g., "PST": "America/Los_Angeles"
}


def parse_date_and_tz(date_string: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Parse a date string and return the UTC string and IANA timezone.
    """
    if not isinstance(date_string, str):
        return None

    try:
        dt_original = parse(date_string)
    except (ParserError, ValueError):
        return None

    original_tz_name = dt_original.tzname()
    iana_timezone = TIMEZONE_MAP.get(original_tz_name, original_tz_name) if original_tz_name else None

    if dt_original.tzinfo is None:
        dt_utc = dt_original.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt_original.astimezone(timezone.utc)

    utc_string = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return (utc_string, iana_timezone)


def find_and_convert_dates_in_data(data: Any, key_name: str) -> Any:
    """
    Recursively traverse a data structure and convert the value of a specific
    key, inserting a new "timezone" key after it.

    This function is idempotent.
    """
    if isinstance(data, dict):
        # Use a static list of keys to iterate over, as we may modify the dict
        keys = list(data.keys())
        for i, key in enumerate(keys):
            # Check if the current key matches the target key
            if key == key_name:
                tz_key = f"{key}_timezone"
                # IDEMPOTENCY CHECK: If the next key is "timezone",
                # assume this has already been converted and skip.
                is_last_key = (i + 1) == len(keys)
                if not is_last_key and keys[i + 1] == tz_key:
                    continue

                value = data[key]
                if isinstance(value, str):
                    parsed_info = parse_date_and_tz(value)
                    if parsed_info:
                        utc_string, iana_timezone = parsed_info
                        print(f"Converted value for key [{key}]")
                        # Update the original keys value
                        data[key] = DoubleQuotedScalarString(utc_string)
                        # Insert the new "timezone" key after the current key
                        if iana_timezone:
                            data.insert(i + 1, tz_key, DoubleQuotedScalarString(iana_timezone))  # type: ignore[attr-defined]
            else:
                # If the key doesnt match, recurse into the value.
                data[key] = find_and_convert_dates_in_data(data[key], key_name)
        return data

    if isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = find_and_convert_dates_in_data(item, key_name)
        return data

    # Return any other data type unchanged.
    return data


def process_yaml_file(file_path: str, key_name: str) -> None:
    """
    Read a YAML file, convert specified keys, and write it back.
    """
    print(f"\nProcessing file: {file_path}")

    ryaml = YAML()
    ryaml.preserve_quotes = True
    # This is the key change: Set the indentation to match common styles.
    # `mapping` is the indent for dictionary keys.
    # `sequence` is the indent for list items content.
    # `offset` is the indent for the list item dash ("-").
    ryaml.indent(mapping=2, sequence=4, offset=2)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml_content = ryaml.load(f)

        find_and_convert_dates_in_data(yaml_content, key_name)

        with open(file_path, "w", encoding="utf-8") as f:
            ryaml.dump(yaml_content, f)

        print(f"  -> Successfully processed and saved: {file_path}")

    except FileNotFoundError:
        print(f"  -> Error: File not found at [{file_path}]")


def main() -> None:
    """
    Entry point of the script.
    """
    if len(sys.argv) < 3:
        print("--- YAML Date Conversion (Structure-Preserving by Key) ---")
        print(f"Usage: python {sys.argv[0]} <key_name> <file1.yaml> [file2.yaml] ...")
        print("\nExample: To convert fields with the key [date], use:")
        print(f"         python {sys.argv[0]} date file.yaml")
        sys.exit(1)

    key_to_find = sys.argv[1]
    files_to_process = sys.argv[2:]

    print(f"--- Starting YAML Date Conversion for key [{key_to_find}] in {len(files_to_process)} file(s) ---")

    for file_path in files_to_process:
        process_yaml_file(file_path, key_to_find)


if __name__ == "__main__":
    main()
