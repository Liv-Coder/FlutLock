#!/usr/bin/env python3
"""
FlutLock Custom Signing Configuration Example

This example demonstrates how to use custom signing configuration names
with the FlutLock tool. This is particularly useful for:

1. Multiple flavor configurations in a single app
2. Custom build variants
3. Different signing configurations for debug/staging/production

Usage:
    python custom_signing_config_example.py --path=/path/to/flutter/project --signing-config-name=staging
"""

import argparse
import json
import os
import sys
import tempfile

# Add the parent directory to the Python path for importing
# or use the installed package if available
try:
    from flutter_signer.main import main as flutlock_main
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from src.flutter_signer.main import main as flutlock_main
    except ImportError:
        print(
            "Error: Could not import FlutLock. Make sure it's installed or run from the project root."
        )
        sys.exit(1)


def create_temp_config(signing_config_name):
    """Create a temporary configuration file with variable substitution."""
    config = {
        "keystore": {
            "path": "${PROJECT_DIR}/android/app/${KEYSTORE_NAME:-my_keystore.jks}",
            "alias": "${SIGNING_ALIAS:-upload}",
            "use_existing": "${USE_EXISTING_KEYSTORE:-false}",
        },
        "build": {"type": "${BUILD_TYPE:-apk}", "verify": True},
        "flutter": {"additional_args": ["--${BUILD_MODE:-release}"]},
    }

    # Create a temporary file to store the configuration
    fd, config_path = tempfile.mkstemp(suffix=".json", prefix="flutlock_config_")
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Created temporary configuration file at: {config_path}")
    print("Configuration contents:")
    print(json.dumps(config, indent=2))

    return config_path


def main():
    """Run the example."""
    parser = argparse.ArgumentParser(description="FlutLock Custom Signing Configuration Example")
    parser.add_argument(
        "--path", default=".", help="Path to Flutter project (default: current directory)"
    )
    parser.add_argument(
        "--signing-config-name",
        default="staging",
        help="Custom name for the signing configuration (default: staging)",
    )
    parser.add_argument(
        "--keystore-name",
        help="Name of the keystore file (sets KEYSTORE_NAME environment variable)",
    )
    parser.add_argument(
        "--signing-alias",
        help="Alias for the signing key (sets SIGNING_ALIAS environment variable)",
    )
    parser.add_argument(
        "--build-type",
        choices=["apk", "aab"],
        help="Build type (sets BUILD_TYPE environment variable)",
    )
    parser.add_argument(
        "--build-mode",
        choices=["debug", "profile", "release"],
        default="release",
        help="Build mode (sets BUILD_MODE environment variable)",
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use existing keystore (sets USE_EXISTING_KEYSTORE environment variable)",
    )
    args = parser.parse_args()

    # Set environment variables for variable substitution
    if args.keystore_name:
        os.environ["KEYSTORE_NAME"] = args.keystore_name
    if args.signing_alias:
        os.environ["SIGNING_ALIAS"] = args.signing_alias
    if args.build_type:
        os.environ["BUILD_TYPE"] = args.build_type
    os.environ["BUILD_MODE"] = args.build_mode
    os.environ["USE_EXISTING_KEYSTORE"] = "true" if args.use_existing else "false"

    # Create temporary configuration file
    config_path = create_temp_config(args.signing_config_name)

    # Construct FlutLock arguments
    flutlock_args = [
        "--path",
        args.path,
        "--config",
        config_path,
        "--signing-config-name",
        args.signing_config_name,
        "--verbose",  # Use verbose mode to see what's happening
    ]

    print(f"\nRunning FlutLock with custom signing configuration name: {args.signing_config_name}")
    print(f"Command arguments: {' '.join(flutlock_args)}")

    # Reset sys.argv for flutlock_main
    sys.argv = [sys.argv[0]] + flutlock_args

    try:
        return_code = flutlock_main()
        if return_code == 0:
            print(
                f"\n✅ Successfully completed using signing configuration name: {args.signing_config_name}"
            )
        else:
            print(f"\n❌ FlutLock exited with error code: {return_code}")
        return return_code
    finally:
        # Clean up temporary file
        try:
            os.unlink(config_path)
            print(f"Removed temporary configuration file: {config_path}")
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
