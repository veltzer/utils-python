#!/usr/bin/env python

"""
Validate a yaml file including order of elements
"""

import sys
import argparse
import requests
from ruamel.yaml import YAML
from jsonschema import validate, Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

ROOT="root"
SCHEMA_CACHE : dict[str, None] = {}
DEBUG = True


def load_yaml_with_order(file_path):
    """
    Loads a YAML file while preserving the order of keys.
    Uses ruamel.yaml for this purpose.
    """
    yaml = YAML(typ="rt") # rt stands for round-trip, preserving order and comments
    with open(file_path, encoding="UTF8") as f:
        return yaml.load(f)


def fetch_schema(schema_url):
    """
    Fetches a JSON schema from a given URL, using a cache to avoid re-fetching.
    """
    if schema_url in SCHEMA_CACHE:
        return SCHEMA_CACHE[schema_url]
    response = requests.get(schema_url, timeout=5)
    response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
    schema = response.json()
    SCHEMA_CACHE[schema_url] = schema
    return schema

def check_order_recursively(data, schema, filename, path="", debug=False):
    """
    Recursively traverses the data and checks property order against the schema.
    Returns True if all orders are valid, False otherwise.
    """
    is_valid = True
    if debug:
        print(f"DEBUG: Checking order at path [{path}]")

    # Case 1: The data is a dictionary (an object in YAML/JSON)
    if isinstance(data, dict):
        # Check property order for the current object if specified
        if "propertyOrdering" in schema:
            expected_order = schema["propertyOrdering"]
            actual_keys = list(data.keys())
            ordered_actual_keys = [key for key in expected_order if key in actual_keys]

            if ordered_actual_keys != [key for key in actual_keys if key in expected_order]:
                line_num = data.lc.line if hasattr(data, "lc") else "N/A"
                print(f"Error in filename: {filename}:{line_num}")
                print(f"Property Order FAILED at path: {path}")
                print(f"Expected order of keys: {expected_order}")
                print(f"Actual order of keys: {actual_keys}")
                is_valid = False

        # Recursively check each property of the object
        for key, value in data.items():
            sub_schema = schema.get("properties", {}).get(key)
            if sub_schema:
                new_path = f"{path}.{key}" if path else key
                if not check_order_recursively(value, sub_schema, filename, new_path, debug):
                    is_valid = False
    elif isinstance(data, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]"
                if not check_order_recursively(item, item_schema, filename, new_path, debug):
                    is_valid = False
    return is_valid


def main():
    """
    Main function to run the validation script.
    """
    parser = argparse.ArgumentParser(
        description="Validate a YAML file against a JSON schema, including property order."
    )
    parser.add_argument("yaml_files", nargs="+", help="One or more YAML files to validate.")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug output for resolver and order checking.")
    args = parser.parse_args()

    for yaml_file in args.yaml_files:
        data = load_yaml_with_order(yaml_file)
        schema_url = data.get("$schema")
        if not schema_url:
            print(f"Error: [{yaml_file}] does not contain a $schema URL reference")
            sys.exit(1)
        schema = fetch_schema(schema_url)
        if DEBUG:
            # In debug mode, create a custom registry to see remote lookups
            # print("DEBUG: Setting up validator with a debug registry...")
            def logging_retriever(uri):
                # print(f"DEBUG: referencing library is fetching remote ref: {uri}")
                # Use our caching fetch_schema function
                return Resource.from_contents(fetch_schema(uri))

            # The schema itself is a resource, and we define a retriever for any *other* URIs
            resource = Resource.from_contents(schema, default_specification=DRAFT7)
            registry = Registry(retrieve=logging_retriever).with_resource(schema_url, resource)
            # Use a specific validator class with our custom registry
            validator = Draft7Validator(schema, registry=registry)
            validator.validate(data)
        else:
            # Default, non-debug behavior
            validate(instance=data, schema=schema)
        assert check_order_recursively(data, schema, yaml_file, debug=args.debug)


if __name__ == "__main__":
    # To run this script, you need to install the required libraries:
    # pip install ruamel.yaml jsonschema requests referencing
    main()
