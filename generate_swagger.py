#!/usr/bin/env python3
"""
Script to generate OpenAPI specification files (swagger.yaml and swagger.json)
at the root of the repository.

This script imports the FastAPI application from src/main.py and uses
its OpenAPI schema to generate the specification files.
"""

import json
import os
import sys

import yaml

# Add the src directory to the Python path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)


def generate_swagger_files():
    """
    Generate OpenAPI specification files (swagger.yaml and swagger.json) at the root.

    This function imports the FastAPI app from src/main.py,
    retrieves its OpenAPI schema, and writes it to swagger.yaml and swagger.json files.
    """
    try:
        # Import the FastAPI app from src/main.py
        import main

        # Get the OpenAPI schema
        openapi_schema = main.app.openapi()

        # Ensure OpenAPI version is compatible with Backstage
        # Replace 3.1.0 with 3.0.3 for better compatibility
        if openapi_schema.get("openapi", "").startswith("3.1"):
            openapi_schema["openapi"] = "3.0.3"

        # Define the paths for the swagger files
        swagger_yaml_path = os.path.join(current_dir, "swagger.yaml")
        swagger_json_path = os.path.join(current_dir, "swagger.json")

        # Write the OpenAPI schema to the swagger.yaml file
        with open(swagger_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(openapi_schema, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Swagger YAML generated successfully at {swagger_yaml_path}")

        # # Also write to swagger.json for backward compatibility
        with open(swagger_json_path, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2)

        print(f"✅ Swagger JSON generated successfully at {swagger_json_path}")

        return True

    except ImportError as e:
        print(f"❌ Error importing FastAPI app: {e}")
        print("Make sure all dependencies are installed and the src directory is accessible.")
        return False

    except (OSError, ValueError, TypeError) as e:
        print(f"❌ Error generating Swagger files: {e}")
        return False


if __name__ == "__main__":
    print("Generating Swagger files...")
    SUCCESS = generate_swagger_files()
    sys.exit(0 if SUCCESS else 1)
