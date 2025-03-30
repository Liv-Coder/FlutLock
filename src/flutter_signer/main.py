#!/usr/bin/env python3
"""
Main entry point for the FlutLock tool.

Handles command-line arguments and orchestrates the signing process.
"""

import argparse
import logging
import os
import sys
import traceback

from . import __version__
from .core.keystore import generate_keystore, KeystoreError
from .core.properties import create_key_properties
from .core.build import build_flutter_app, BuildError
from .core.verify import verify_signature, SignatureError
from .core.dependencies import check_dependencies, DependencyError
from .core.gradle import update_app_build_gradle, GradleError
from .utils.config_processor import (
    load_config_file,
    process_config,
    validate_config,
    find_global_config,
)
from .utils.exceptions import FlutLockError, ConfigError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flutlock")


def parse_args():
    """Parse command-line arguments."""

    # Custom formatter for better help formatting
    class CustomHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
        def _split_lines(self, text, width):
            # Allow for newlines in help text
            if "\n" in text:
                return text.splitlines()
            return super()._split_lines(text, width)

        def _get_help_string(self, action):
            # Add default values to help strings
            help_text = action.help
            if (
                action.default is not argparse.SUPPRESS
                and action.default is not None
                and action.default != ""
            ):
                help_text = f"{help_text} (default: %(default)s)"
            return help_text

    # Create parser with enhanced description and epilog
    parser = argparse.ArgumentParser(
        description="""
Flutter Android App Signing Tool

FlutLock automates the Android app signing process for Flutter applications.
It handles keystore generation, key.properties creation, build.gradle modification,
and Flutter build execution.

For detailed documentation: https://github.com/yourusername/flutlock
        """,
        formatter_class=CustomHelpFormatter,
        epilog="""
Examples:
  # Basic usage (interactive mode)
  flutlock
  
  # Use a configuration file
  flutlock --config config/flutlock_config.json
  
  # Use a global configuration file
  flutlock --config global
  
  # Build an Android App Bundle instead of APK
  flutlock --build-type aab
  
  # Skip the build step (just set up signing)
  flutlock --skip-build
  
  # Only update the build.gradle file
  flutlock --only-update-gradle
  
  # Non-interactive mode for CI/CD
  flutlock --non-interactive --keystore-path android/app/keystore.jks
  
  # Custom signing configuration name
  flutlock --signing-config-name production
  
  # Run from outside the project
  flutlock --path /path/to/flutter/project
  
Environment Variables:
  KEYSTORE_PASSWORD - Password for the keystore
  KEY_PASSWORD - Password for the key (defaults to keystore password)
  
Configuration File (JSON):
  See config/flutlock_config.json for an example
  Supports variable substitution: ${VAR_NAME:-default_value}
  
Global Configuration:
  A global flutlock_config.json can be placed in any of these locations:
  - Current working directory
  - User's home directory (~/ or ~/.flutlock/)
  - ~/.config/flutlock/ (Linux)
  - %APPDATA%/flutlock/ (Windows)
  - ~/Library/Application Support/flutlock/ (macOS)
        """,
    )

    # Create argument groups for better organization
    basic_group = parser.add_argument_group("Basic Options")
    keystore_group = parser.add_argument_group("Keystore Options")
    build_group = parser.add_argument_group("Build Options")
    ci_group = parser.add_argument_group("CI/CD Environment Options")
    verbosity_group = parser.add_argument_group("Logging Options")

    # Basic options
    basic_group.add_argument(
        "--path",
        default=".",
        help="Path to Flutter project",
    )
    basic_group.add_argument(
        "--config",
        help="Path to JSON configuration file. Use '--config global' or '--config true' to automatically find and use a global flutlock_config.json file.",
    )

    # Build options
    build_group.add_argument(
        "--build-type",
        choices=["apk", "aab"],
        default="apk",
        help="Build type: apk or aab (Android App Bundle)",
    )
    build_group.add_argument(
        "--verify",
        dest="verify",
        action="store_true",
        default=True,
        help="Verify app signature after build",
    )
    build_group.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        help="Skip signature verification",
    )
    build_group.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the build step (useful for testing keystores)",
    )
    build_group.add_argument(
        "--update-gradle",
        action="store_true",
        default=True,
        help="Update app-level build.gradle with signing configuration",
    )
    build_group.add_argument(
        "--no-update-gradle",
        dest="update_gradle",
        action="store_false",
        help="Skip updating build.gradle file",
    )
    build_group.add_argument(
        "--only-update-gradle",
        action="store_true",
        help="Only update the app-level build.gradle file with signing configuration without generating keystore or performing other operations",
    )

    # Keystore options
    keystore_group.add_argument(
        "--keystore-path",
        help="Path to existing keystore or where to create a new one",
    )
    keystore_group.add_argument(
        "--keystore-alias",
        help="Keystore alias to use",
    )
    keystore_group.add_argument(
        "--use-existing-keystore",
        action="store_true",
        help="Use an existing keystore instead of generating a new one",
    )
    keystore_group.add_argument(
        "--signing-config-name",
        default="release",
        help="Custom name for the signing configuration in build.gradle",
    )

    # CI/CD Environment options
    ci_group.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (for CI/CD environments)",
    )
    ci_group.add_argument(
        "--keystore-password-env",
        default="KEYSTORE_PASSWORD",
        help="Environment variable containing keystore password",
    )
    ci_group.add_argument(
        "--key-password-env",
        default="KEY_PASSWORD",
        help="Environment variable containing key password",
    )

    # Add version argument
    basic_group.add_argument(
        "--version",
        action="version",
        version=f"FlutLock v{__version__}",
        help="Show version information and exit",
    )

    # Add verbosity options
    verbosity_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    verbosity_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all non-error output",
    )

    # Add help command that shows additional info
    basic_group.add_argument(
        "--help-advanced",
        action="store_true",
        help="Show advanced help information and exit",
        dest="help_advanced",
    )

    args = parser.parse_args()

    # Handle custom help command
    if hasattr(args, "help_advanced") and args.help_advanced:
        print_advanced_help()
        sys.exit(0)

    return args


def print_advanced_help():
    """Print advanced help information."""
    print(
        """
FlutLock Advanced Help
======================

Configuration File Format
------------------------
FlutLock supports JSON configuration files with variable substitution.
Example:

{
  "keystore": {
    "path": "${PROJECT_DIR}/android/app/upload.keystore",
    "alias": "upload",
    "store_password": "${KEYSTORE_PASSWORD:-password123}",
    "key_password": "${KEY_PASSWORD:-password123}",
    "use_existing": false
  },
  "signer": {
    "name": "Your Name",
    "org_unit": "Development",
    "organization": "Your Company",
    "locality": "Your City",
    "state": "Your State",
    "country": "US"
  },
  "build": {
    "type": "apk",
    "verify": true,
    "skip_build": false,
    "update_gradle": true
  },
  "flutter": {
    "package": "com.example.${APP_NAME}",
    "flavors": {
      "dev": {"applicationId": "com.example.${APP_NAME}.dev"},
      "prod": {"applicationId": "com.example.${APP_NAME}"}
    }
  }
}

Special Variables
----------------
- ${PROJECT_DIR}: Absolute path to the Flutter project directory
- ${APP_NAME}: Name of the Flutter application (from directory name)

Environment Variables
-------------------
- KEYSTORE_PASSWORD: Password for the keystore
- KEY_PASSWORD: Password for the key (defaults to keystore password)

Workflow
-------
1. Checks dependencies (Flutter, keytool, apksigner)
2. Generates or uses existing keystore
3. Creates/updates key.properties file
4. Modifies build.gradle file (if --update-gradle)
5. Runs Flutter build (unless --skip-build)
6. Verifies signature (if --verify)

Troubleshooting
--------------
- Use --verbose for detailed logging
- Check paths and permissions
- Verify Android SDK and Flutter installations
- Ensure build.gradle follows standard format
- For more details: https://github.com/yourusername/flutlock/docs
"""
    )


def main():
    """Main function."""
    try:
        args = parse_args()

        # Configure logging based on verbosity flags
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        elif args.quiet:
            logger.setLevel(logging.ERROR)

        # Load and process configuration file if provided
        config = None
        if args.config:
            try:
                config_path = args.config

                # If --config is provided without a path, search for global config
                if config_path == "global" or config_path.lower() == "true":
                    global_config_path = find_global_config()
                    if global_config_path:
                        config_path = global_config_path
                        logger.info("Using global configuration file: %s", config_path)
                    else:
                        logger.error(
                            "No global configuration file found. Please create a flutlock_config.json file."
                        )
                        logger.info(
                            "Search locations include current directory, user's home directory, or system config directories."
                        )
                        return 1

                # Load raw config data
                raw_config = load_config_file(config_path)

                # Process the config (variable substitution)
                config = process_config(raw_config, project_path=args.path, env_vars=os.environ)
                logger.debug("Configuration processed with variable substitution")

                # Validate the configuration
                validate_config(config)
                logger.debug("Configuration validation successful")
            except ConfigError as e:
                logger.error("Error in configuration file: %s", e)
                # Add detailed traceback for debugging
                if args.verbose:
                    logger.debug("Traceback: %s", traceback.format_exc())
                return 1
            except Exception as e:
                logger.error("Unexpected error processing configuration: %s", e)
                if args.verbose:
                    logger.debug("Traceback: %s", traceback.format_exc())
                return 1

        # If only updating Gradle, skip other operations
        if args.only_update_gradle:
            try:
                # Pass the custom signing configuration name to the gradle updater
                success = update_app_build_gradle(
                    args.path, config=config, signing_config_name=args.signing_config_name
                )
                if success:
                    logger.info("build.gradle successfully updated with signing configuration")
                return 0
            except GradleError as e:
                logger.error("Failed to update build.gradle: %s", e)
                return 1

        # Check for non-interactive mode
        if args.non_interactive:
            logger.debug("Running in non-interactive mode")

            # Ensure required environment variables exist for non-interactive mode
            if not args.config:
                store_password_env = args.keystore_password_env
                key_password_env = args.key_password_env

                if store_password_env not in os.environ:
                    logger.error(
                        "Non-interactive mode requires %s environment variable", store_password_env
                    )
                    return 1

                if key_password_env not in os.environ and not os.environ.get(store_password_env):
                    logger.error(
                        "Non-interactive mode requires %s environment variable when %s is not set",
                        key_password_env,
                        store_password_env,
                    )
                    return 1

        # Check dependencies
        try:
            logger.debug("Checking dependencies...")
            if not args.skip_build:
                check_dependencies()
        except DependencyError as e:
            logger.error("Dependency error: %s", e)
            return 1

        # Set up the Flutter project path
        flutter_project_path = os.path.abspath(args.path)
        logger.debug("Using Flutter project path: %s", flutter_project_path)

        # Create or use existing keystore
        try:
            # Set up keystore parameters
            keystore_path = None
            alias = None
            use_existing = False

            # In non-interactive mode or with config, we use provided values
            if args.non_interactive:
                keystore_path = args.keystore_path
                alias = args.keystore_alias
                use_existing = args.use_existing_keystore
            elif config and "keystore" in config:
                keystore_config = config["keystore"]
                keystore_path = keystore_config.get("path")
                alias = keystore_config.get("alias")
                use_existing = keystore_config.get("use_existing", False)

            # If keystore path not provided, use default
            if not keystore_path:
                android_app_dir = os.path.join(flutter_project_path, "android", "app")
                os.makedirs(android_app_dir, exist_ok=True)
                keystore_path = os.path.join(android_app_dir, "upload.keystore")

            logger.debug("Generating keystore at %s...", keystore_path)
            keystore_result = generate_keystore(keystore_path, alias=alias, config=config)

            if keystore_result:
                logger.info("Keystore set up successfully: %s", keystore_path)

                logger.debug("Creating key.properties file...")
                key_props_path = create_key_properties(
                    flutter_project_path, keystore_path, alias=alias, config=config
                )
                logger.info("Created key.properties file")
            else:
                logger.error("Failed to set up keystore")
                return 1

        except KeystoreError as e:
            logger.error("Keystore error: %s", e)
            return 1

        # Update build.gradle if needed
        if args.update_gradle and not args.skip_build:
            try:
                # Pass the custom signing configuration name to the gradle updater
                success = update_app_build_gradle(
                    args.path, config=config, signing_config_name=args.signing_config_name
                )
                if success:
                    logger.info("build.gradle successfully updated with signing configuration")
            except GradleError as e:
                logger.error("Failed to update build.gradle: %s", e)
                return 1

        # Build Flutter app
        if not args.skip_build:
            try:
                logger.debug("Building Flutter app...")
                build_type = args.build_type
                if config and "build" in config and "type" in config["build"]:
                    build_type = config["build"]["type"]

                logger.info("Building %s...", build_type.upper())
                output_file = build_flutter_app(flutter_project_path, build_type)
                logger.info("Build successful: %s", output_file)

                # Verify signature if requested
                if args.verify:
                    logger.debug("Verifying app signature...")
                    if verify_signature(output_file):
                        logger.info(
                            "✅ Signature verification successful for %s",
                            os.path.basename(output_file),
                        )
                    else:
                        logger.error("❌ Signature verification failed")
                        return 1
            except BuildError as e:
                logger.error("Build error: %s", e)
                return 1
            except SignatureError as e:
                logger.error("Signature verification error: %s", e)
                return 1

        logger.info("✅ FlutLock completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.error("\nOperation canceled by user")
        return 130
    except FlutLockError as e:
        logger.error("Fatal error: %s", e)
        if args.verbose if "args" in locals() else False:
            logger.debug("Traceback: %s", traceback.format_exc())
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        if args.verbose if "args" in locals() else False:
            logger.debug("Traceback: %s", traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
