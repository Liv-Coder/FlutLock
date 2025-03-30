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
from .utils.config_processor import load_config_file, process_config, validate_config
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
    parser = argparse.ArgumentParser(
        description="Flutter Android App Signing Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Path to Flutter project",
    )
    parser.add_argument(
        "--build-type",
        choices=["apk", "aab"],
        default="apk",
        help="Build type: apk or aab (Android App Bundle)",
    )
    parser.add_argument(
        "--verify",
        dest="verify",
        action="store_true",
        default=True,
        help="Verify app signature after build",
    )
    parser.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        help="Skip signature verification",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the build step (useful for testing keystores)",
    )
    parser.add_argument(
        "--config",
        help="Path to JSON configuration file",
    )

    # Add non-interactive mode arguments for CI environments
    ci_group = parser.add_argument_group("CI/CD Environment Options")
    ci_group.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (for CI/CD environments)",
    )
    ci_group.add_argument(
        "--keystore-path",
        help="Path to existing keystore or where to create a new one",
    )
    ci_group.add_argument(
        "--keystore-alias",
        help="Keystore alias to use",
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
    ci_group.add_argument(
        "--use-existing-keystore",
        action="store_true",
        help="Use an existing keystore instead of generating a new one",
    )

    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version=f"FlutLock v{__version__}",
        help="Show version information and exit",
    )

    # Add verbosity options
    verbosity_group = parser.add_argument_group("Logging Options")
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

    # Add gradle configuration option
    parser.add_argument(
        "--update-gradle",
        action="store_true",
        default=True,
        help="Update app-level build.gradle with signing configuration",
    )
    parser.add_argument(
        "--no-update-gradle",
        dest="update_gradle",
        action="store_false",
        help="Skip updating build.gradle file",
    )

    # Add custom signing configuration name option
    parser.add_argument(
        "--signing-config-name",
        default="release",
        help="Custom name for the signing configuration in build.gradle",
    )

    return parser.parse_args()


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
                # Load raw config data
                raw_config = load_config_file(args.config)

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

        # Check for Flutter and other dependencies
        logger.debug("Checking dependencies...")
        try:
            check_dependencies()
        except DependencyError as e:
            logger.error("Dependency check failed: %s", e)
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
