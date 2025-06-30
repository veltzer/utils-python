#!/usr/bin/env python

"""
Converts a Tab-Separated Values (TSV) file to a YAML file.

The first line of the TSV is treated as the header row for the field names.
Any spaces in the header names will be replaced with underscores to create the YAML keys.
This script ensures that all output YAML objects have the exact same set of fields,
inserting empty strings for any missing values in the source data.

Args:
    input_file (str): The path to the input TSV file.
    output_file (str): The path for the output YAML file.
"""

import sys
import csv

def convert_tsv_to_yaml(input_file, output_file):
    with open(input_file, "r", newline="", encoding="utf-8") as tsvfile:
        # Use the csv reader with a tab delimiter to handle TSV format
        reader = csv.reader(tsvfile, delimiter="\t")

        # Read the first line as the header
        raw_headers = next(reader)
        # Create YAML-friendly keys by replacing spaces with underscores
        headers = [header.replace(" ", "_") for header in raw_headers]
        num_headers = len(headers)

        # Prepare a list to hold all the data records (as dictionaries)
        records = []
        for row in reader:
            # Ensure every row has the same number of columns as the header
            # Pad with empty strings if the row is shorter
            if len(row) < num_headers:
                row.extend([''] * (num_headers - len(row)))

            # Create a dictionary for the current row, mapping modified headers to row values
            record = {headers[i]: row[i] for i in range(num_headers)}
            records.append(record)

    # Manually construct the YAML string
    with open(output_file, "w", encoding="utf-8") as yamlfile:
        # Write the root element
        yamlfile.write("items:\n")

        # Write each record
        for record in records:
            # Start of a list item in YAML
            yamlfile.write("  - ")

            # Write the key-value pairs for the record
            # Use a flag to handle indentation for the first key-value pair
            is_first_item = True
            for key, value in record.items():
                # All subsequent lines for this record need to be indented further
                if not is_first_item:
                    yamlfile.write("    ")

                # Write the key and the quoted value
                # Using quotes for all values is a safe way to handle special characters
                yamlfile.write(f'{key}: "{value}"\n')
                is_first_item = False

    print(f"Successfully converted [{input_file}] to [{output_file}]")


if __name__ == "__main__":
    convert_tsv_to_yaml(sys.argv[1], sys.argv[2])
