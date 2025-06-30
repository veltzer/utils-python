#!/usr/bin/env python

"""
Converts a Tab-Separated Values (TSV) file to a YAML file.

The first line of the TSV is treated as the header row for the field names.
Any spaces in the header names will be replaced with underscores to create the YAML keys.
This script performs a pre-scan of the data to:
1. Omit any column that is entirely empty across all records.
2. Identify columns that are exclusively boolean. Empty values in these columns default to 'false'.
3. Convert specified columns from comma-separated strings into a YAML array.

Args:
    input_file (str): The path to the input TSV file.
    output_file (str): The path for the output YAML file.
    --array-columns (str): Optional. A comma-separated string of column headers to be
                           treated as arrays (e.g., "Genre,Tags").
"""

import csv
import argparse

# Define recognizable boolean string values
BOOLEAN_TRUE_STRS = {'true', 'yes', 't', 'y'}
BOOLEAN_FALSE_STRS = {'false', 'no', 'f', 'n'}
ALL_BOOLEAN_STRS = BOOLEAN_TRUE_STRS | BOOLEAN_FALSE_STRS

def _parse_tsv_data(input_file, array_columns_str=""):
    """Reads and processes the TSV data, returning a list of records."""
    array_keys = {key.strip().replace(" ", "_").lower() for key in (array_columns_str or "").split(',') if key.strip()}

    with open(input_file, "r", newline="", encoding="utf-8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter="\t")
        raw_headers = next(reader)
        data_rows = list(reader)

    # --- First Pass: Analyze column content ---
    num_columns = len(raw_headers)
    column_info = [{'values': set(), 'is_potentially_boolean': True} for _ in range(num_columns)]

    for row in data_rows:
        for i, raw_value in enumerate(row):
            if i >= num_columns:
                continue
            value = raw_value.strip().lower()
            if value:
                column_info[i]['values'].add(value)
                if value not in ALL_BOOLEAN_STRS:
                    column_info[i]['is_potentially_boolean'] = False

    # --- Determine Final Column Set and Types ---
    active_headers_map = {}
    boolean_column_indices = set()
    for i, info in enumerate(column_info):
        if info['values']:
            active_headers_map[i] = raw_headers[i].replace(" ", "_")
            if info['is_potentially_boolean']:
                boolean_column_indices.add(i)

    # --- Second Pass: Build records ---
    records = []
    for row in data_rows:
        record = {}
        for index, key in active_headers_map.items():
            value_str = row[index].strip() if index < len(row) else ""
            if index in boolean_column_indices:
                record[key] = value_str.lower() in BOOLEAN_TRUE_STRS
            elif key.lower() in array_keys:
                record[key] = [item.strip() for item in value_str.split(',') if item.strip()]
            else:
                record[key] = value_str
        records.append(record)

    return records

def _write_yaml_file(records, output_file):
    """Writes a list of records to a YAML file."""
    with open(output_file, "w", encoding="utf-8") as yamlfile:
        yamlfile.write("items:\n")
        for record in records:
            yamlfile.write("  - ")
            is_first_item = True
            for key, value in record.items():
                if not is_first_item:
                    yamlfile.write("    ")

                if isinstance(value, bool):
                    yamlfile.write(f'{key}: {str(value).lower()}\n')
                elif isinstance(value, list):
                    if value:
                        yamlfile.write(f'{key}:\n')
                        for item in value:
                            yamlfile.write(f'      - "{item}"\n')
                    else:
                        yamlfile.write(f'{key}: []\n')
                else:
                    yamlfile.write(f'{key}: "{value}"\n')
                is_first_item = False

def convert_tsv_to_yaml(input_file, output_file, array_columns_str=""):
    """Orchestrates the conversion from TSV to YAML."""
    records = _parse_tsv_data(input_file, array_columns_str)
    _write_yaml_file(records, output_file)
    print(f"Successfully converted [{input_file}] to [{output_file}]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a Tab-Separated Values (TSV) file to a YAML file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_file", help="The path to the input TSV file.")
    parser.add_argument("output_file", help="The path for the output YAML file.")
    parser.add_argument(
        "--array-columns",
        dest="array_columns_str",
        default="",
        help="Optional. A comma-separated string of column headers to be treated as arrays (e.g., \"Genre,Tags\")."
    )

    args = parser.parse_args()

    convert_tsv_to_yaml(args.input_file, args.output_file, args.array_columns_str)
