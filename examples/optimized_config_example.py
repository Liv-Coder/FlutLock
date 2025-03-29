#!/usr/bin/env python3
"""
Enhanced example script for using FlutLock with optimized configuration.
This demonstrates the variable substitution and environment specific features.
"""

import os
import sys
import json
import tempfile
import argparse

# Add parent directory to system path to find flutter_signer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from the package
from flutter_signer import main


def create_example_config(environment="dev"):
    """
    Create an example configuration file with environment-specific settings.

    Args:
        environment: The environment to use (dev, staging, prod)

    Returns:
        Path to the created config file
    """
    # Base configuration
    base_config = {
        "keystore": {
            "path": "${PROJECT_DIR}/android/app/upload.keystore",
            "alias": "upload",
            "store_password": "${KEYSTORE_PASSWORD:-K@ranstha2525}",
            "key_password": "${KEY_PASSWORD:-K@ranstha2525}",
            "use_existing": False,
        },
        "signer": {
            "name": "Nawal Shrestha",
            "org_unit": "Development",
            "organization": "DevGen",
            "locality": "Sarlahi",
            "state": "Janakpur",
            "country": "NP",
        },
        "build": {"type": "apk", "verify": True, "skip_build": False, "update_gradle": True},
        "flutter": {"package": "com.devgen.${APP_NAME}"},
    }

    # Environment-specific customizations
    if environment == "dev":
        # Development environment
        base_config["build"]["verify"] = False
        base_config["flutter"]["package"] = "com.devgen.${APP_NAME}.dev"
    elif environment == "staging":
        # Staging environment
        base_config["build"]["verify"] = True
        base_config["flutter"]["package"] = "com.devgen.${APP_NAME}.staging"
    elif environment == "prod":
        # Production environment
        base_config["build"]["type"] = "aab"
        base_config["build"]["verify"] = True
        # Use production package name without suffix
    else:
        print(f"Warning: Unknown environment '{environment}', using default settings")

    # Create a temporary file for the config
    fd, config_path = tempfile.mkstemp(suffix=".json", prefix=f"flutlock_config_{environment}_")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(base_config, f, indent=2)

        print(f"Created {environment} config at: {config_path}")
        return config_path
    except Exception as e:
        print(f"Error creating config file: {e}")
        return None


def run_with_config(config_path, flutter_project_path="."):
    """
    Run FlutLock with a configuration file.

    Args:
        config_path: Path to the configuration file
        flutter_project_path: Path to the Flutter project

    Returns:
        Return code from FlutLock
    """
    if not config_path:
        print("No config file available")
        return 1

    # Create a temporary arguments list
    args = [
        "--config",
        config_path,
        "--path",
        flutter_project_path,
        "--verbose",
        "--skip-build",  # Skip build to avoid dependency checks
    ]

    # Pass the args to sys.argv
    old_argv = sys.argv
    sys.argv = [sys.argv[0]] + args

    try:
        # Run the main function
        return_code = main()

        # Check the return code
        if return_code == 0:
            print("FlutLock execution successful!")
        else:
            print(f"FlutLock execution failed with code {return_code}")

        return return_code
    finally:
        # Restore original argv
        sys.argv = old_argv


def parse_example_args():
    """Parse command-line arguments for this example."""
    parser = argparse.ArgumentParser(
        description="FlutLock Optimized Configuration Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment to configure",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to Flutter project",
    )
    parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Don't delete the temporary config file after execution",
    )
    return parser.parse_args()


if __name__ == "__main__":
    print("FlutLock Optimized Configuration Example")
    print("=======================================")

    # Parse example arguments
    example_args = parse_example_args()

    # Create example configuration for the specified environment
    config_path = create_example_config(example_args.env)

    # Run with configuration
    try:
        # Set a sample environment variable for demonstration
        os.environ["APP_VERSION"] = "1.0.0"

        # Run FlutLock with the config
        sys.exit(run_with_config(config_path, example_args.path))
    finally:
        # Clean up the temporary config file unless --keep-config is specified
        if config_path and os.path.exists(config_path) and not example_args.keep_config:
            os.remove(config_path)
            print(f"Cleaned up temporary config file: {config_path}")
        elif config_path and example_args.keep_config:
            print(f"Kept config file for inspection: {config_path}")
