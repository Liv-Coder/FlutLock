#!/usr/bin/env python3
"""
Example script for using FlutLock in CI/CD environments.
This demonstrates non-interactive mode with environment variables.
"""

import os
import sys
import subprocess

# Add parent directory to system path to find flutter_signer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from the package
from flutter_signer import main


def setup_environment_variables():
    """Set up environment variables for non-interactive mode."""
    # These would normally be set by your CI/CD system (GitHub Actions, Jenkins, etc.)
    # Here we set them programmatically for example purposes
    os.environ["KEYSTORE_PASSWORD"] = "ci_password"
    os.environ["KEY_PASSWORD"] = "ci_password"
    os.environ["STORE_ALIAS"] = "upload"

    # Print a message (this would be logged in CI)
    print("Environment variables set for non-interactive signing")


def run_with_args():
    """Run FlutLock with command-line arguments."""
    # Create a temporary arguments list
    # In a real CI/CD environment, you would adjust these paths to match your project structure
    args = [
        "--non-interactive",
        "--path",
        "./flutter_project",  # Path to your Flutter project
        "--keystore-path",
        "./keystore/ci_keystore.jks",  # Path to keystore
        "--build-type",
        "aab",  # Build Android App Bundle instead of APK
        "--verify",  # Verify the signature after build
    ]

    # Pass the args to sys.argv
    old_argv = sys.argv
    sys.argv = [sys.argv[0]] + args

    try:
        # Run the main function
        return_code = main()

        # Check the return code
        if return_code == 0:
            print("Build successful!")
        else:
            print(f"Build failed with code {return_code}")

        return return_code
    finally:
        # Restore original argv
        sys.argv = old_argv


if __name__ == "__main__":
    print("FlutLock CI/CD Example")
    print("=====================")

    # Set up environment variables
    setup_environment_variables()

    # Run with arguments
    sys.exit(run_with_args())
