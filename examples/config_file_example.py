#!/usr/bin/env python3
"""
Example script for using FlutLock with a configuration file.
This demonstrates how to use JSON configuration for keystore settings.
"""

import os
import sys
import json
import tempfile

# Add parent directory to system path to find flutter_signer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from the package
from flutter_signer import main


def create_example_config():
    """Create an example configuration file."""
    config = {
        "keystore": {
            "path": "./keystore/my_keystore.jks",
            "alias": "upload",
            "store_password": "store_password_here",
            "key_password": "key_password_here",
            "use_existing": False,
        },
        "signer": {
            "name": "John Doe",
            "org_unit": "Development",
            "organization": "Example Company",
            "locality": "San Francisco",
            "state": "California",
            "country": "US",
        },
        "build": {"type": "apk", "verify": True, "skip_build": False},
    }

    # Create a temporary file for the config
    fd, config_path = tempfile.mkstemp(suffix=".json", prefix="flutlock_config_")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Created example config at: {config_path}")
        return config_path
    except Exception as e:
        print(f"Error creating config file: {e}")
        return None


def run_with_config(config_path):
    """Run FlutLock with a configuration file."""
    if not config_path:
        print("No config file available")
        return 1

    # Create a temporary arguments list
    args = ["--config", config_path, "--path", "./flutter_project"]  # Path to your Flutter project

    # Pass the args to sys.argv
    old_argv = sys.argv
    sys.argv = [sys.argv[0]] + args

    try:
        # Run the main function
        return_code = main()

        # Check the return code
        if return_code == 0:
            print("Build with config successful!")
        else:
            print(f"Build with config failed with code {return_code}")

        return return_code
    finally:
        # Restore original argv
        sys.argv = old_argv


if __name__ == "__main__":
    print("FlutLock Configuration Example")
    print("=============================")

    # Create example configuration
    config_path = create_example_config()

    # Run with configuration
    try:
        sys.exit(run_with_config(config_path))
    finally:
        # Clean up the temporary config file
        if config_path and os.path.exists(config_path):
            os.remove(config_path)
            print(f"Cleaned up temporary config file: {config_path}")
