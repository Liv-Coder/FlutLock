#!/usr/bin/env python3
"""
FlutLock: Flutter Signing Automation Tool

A command-line tool to automate the Android app signing process for Flutter applications.
Handles keystore generation, key.properties file creation, and build commands.
"""

import argparse
import getpass
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback  # Import at the module level instead of in main()
from pathlib import Path

__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flutlock")


# Custom exceptions for better error handling
class FlutLockError(Exception):
    """Base exception for all FlutLock errors."""


class DependencyError(FlutLockError):
    """Exception raised for missing dependencies."""


class KeystoreError(FlutLockError):
    """Exception raised for issues with keystore operations."""


class ConfigError(FlutLockError):
    """Exception raised for issues with configuration files."""


class BuildError(FlutLockError):
    """Exception raised for Flutter build issues."""


class SignatureError(FlutLockError):
    """Exception raised for issues with signature verification."""


def check_dependencies():
    """Check if required external dependencies are installed."""
    dependencies = {
        "flutter": "Flutter SDK",
        "keytool": "Java Development Kit",
        "apksigner": "Android SDK Build Tools",
    }

    missing = []
    for cmd, name in dependencies.items():
        if not shutil.which(cmd):
            missing.append(f"{name} ({cmd})")

    if missing:
        missing_str = ", ".join(missing)
        logger.error("Missing dependencies: %s", missing_str)
        logger.info("Please install the missing dependencies and ensure they are in your PATH.")

        # Provide more specific guidance for each missing dependency
        for item in missing:
            if "Flutter SDK" in item:
                logger.info(
                    "Flutter installation guide: https://flutter.dev/docs/get-started/install"
                )
            elif "Java Development Kit" in item:
                logger.info("JDK installation guide: https://openjdk.java.net/install/")
            elif "Android SDK" in item:
                logger.info("Android SDK installation: https://developer.android.com/studio")

        raise DependencyError(f"Missing dependencies: {missing_str}")

    return True


def run_command(cmd, **kwargs):
    """Run a shell command and return the output."""
    try:
        logger.debug("Running command: %s", " ".join(cmd))
        # For security, mask password arguments in the log
        log_cmd = []
        skip_next = False
        for arg in cmd:
            if skip_next:
                log_cmd.append("***")
                skip_next = False
            elif arg in ["-storepass", "-keypass"]:
                log_cmd.append(arg)
                skip_next = True
            else:
                log_cmd.append(arg)
        logger.debug("Command (masked): %s", " ".join(log_cmd))

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            **kwargs,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            # Split long line for better readability
            logger.error(
                "Command failed with code %d: %s",
                result.returncode,
                error_msg,
            )

            # Improve error details for common issues
            if "keytool" in cmd[0] and "password was incorrect" in error_msg:
                error_msg = (
                    "Keystore password was incorrect. " "Please check your password and try again."
                )
            elif "flutter" in cmd[0] and "Target file" in error_msg and "not found" in error_msg:
                error_msg = (
                    "Flutter build failed: Missing target files. "
                    "Ensure your Flutter project is properly configured."
                )

            logger.debug("Command output: %s", result.stdout.strip())
            return False, error_msg

        return True, result.stdout.strip()
    except subprocess.SubprocessError as e:
        logger.error("Error executing command: %s", e)
        return False, str(e)
    except (OSError, IOError) as e:
        logger.error("IO error executing command: %s", e)
        return False, str(e)


def generate_keystore(keystore_path, alias=None, validity=25 * 365, config=None):
    """Generate a new keystore file."""
    try:
        if os.path.exists(keystore_path):
            logger.warning("Keystore already exists at %s", keystore_path)
            overwrite = input("Overwrite existing keystore? (y/N): ").lower() == "y"
            if not overwrite:
                logger.info("Using existing keystore.")
                return True
            else:
                # Delete the existing keystore to avoid alias conflict
                try:
                    os.remove(keystore_path)
                    logger.info("Deleted existing keystore at %s", keystore_path)
                except (OSError, IOError) as e:
                    error_msg = f"Failed to delete existing keystore: {e}"
                    logger.error(error_msg)
                    raise KeystoreError(error_msg) from e

        # Get keystore details from config, environment vars, or user input
        keystore_config = config.get("keystore", {}) if config else {}

        # Get store password
        store_password = keystore_config.get("store_password")
        if not store_password:
            store_password = os.environ.get("KEYSTORE_PASSWORD")
        if not store_password:
            store_password = getpass.getpass("Enter keystore password: ")

            # Validate password strength
            if len(store_password) < 6:
                logger.warning(
                    "Warning: Using a short keystore password. For better security, use at least 8 characters."
                )

        # Get key password
        key_password = keystore_config.get("key_password")
        if not key_password:
            key_password = os.environ.get("KEY_PASSWORD")
        if not key_password:
            key_password = getpass.getpass(
                "Enter key password (press Enter to use same as keystore): "
            )
            if not key_password:
                key_password = store_password

        # Get alias
        if not alias:
            alias = keystore_config.get("alias")
        if not alias:
            alias = os.environ.get("STORE_ALIAS") or "upload"

        # Get signer information from config or user input
        signer_config = config.get("signer", {}) if config else {}

        # Get distinguished name components
        name = signer_config.get("name")
        if not name:
            name = input("Enter your name (CN): ")
            if not name:
                error_msg = "Name (CN) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        org_unit = signer_config.get("org_unit")
        if not org_unit:
            org_unit = input("Enter organizational unit (OU) [Development]: ") or "Development"

        org = signer_config.get("organization")
        if not org:
            org = input("Enter organization (O) [Your Company]: ") or "Your Company"

        locality = signer_config.get("locality")
        if not locality:
            locality = input("Enter locality/city (L): ")
            if not locality:
                error_msg = "Locality (L) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        state = signer_config.get("state")
        if not state:
            state = input("Enter state/province (ST): ")
            if not state:
                error_msg = "State/province (ST) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        country = signer_config.get("country")
        if not country:
            country = input("Enter country code (C) [US]: ") or "US"

        # Build DN string - breaking up a long line for better readability
        dname = f"CN={name}, OU={org_unit}, O={org}, " f"L={locality}, ST={state}, C={country}"

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(os.path.abspath(keystore_path))
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except (OSError, IOError) as e:
            error_msg = f"Failed to create parent directory for keystore: {e}"
            logger.error(error_msg)
            raise KeystoreError(error_msg) from e

        # Generate keystore
        cmd = [
            "keytool",
            "-genkey",
            "-v",
            "-keystore",
            keystore_path,
            "-alias",
            alias,
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            str(validity),
            "-dname",
            dname,
            "-storepass",
            store_password,
            "-keypass",
            key_password,
        ]

        success, output = run_command(cmd)

        if success:
            logger.info("Keystore generated successfully at %s", keystore_path)
            # Set appropriate permissions (if on Unix-like system)
            if os.name == "posix":
                try:
                    os.chmod(keystore_path, 0o600)  # Owner read/write only
                    logger.debug("Set file permissions 0600 for %s", keystore_path)
                except (OSError, IOError) as e:
                    logger.warning("Failed to set permissions on keystore: %s", e)
            return True
        else:
            error_msg = f"Failed to generate keystore: {output}"
            logger.error(error_msg)
            raise KeystoreError(error_msg)
    except KeystoreError:
        # Just re-raise KeystoreError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error generating keystore: {e}"
        logger.error(error_msg)
        raise KeystoreError(error_msg) from e


def create_key_properties(flutter_project_path, keystore_path, alias=None, config=None):
    """Create or update the key.properties file in the Flutter project."""
    try:
        android_dir = os.path.join(flutter_project_path, "android")

        if not os.path.isdir(android_dir):
            error_msg = f"Android directory not found in {flutter_project_path}"
            logger.error(error_msg)
            logger.info("Make sure this is a valid Flutter project with an android directory")
            raise FlutLockError(error_msg)

        key_properties_path = os.path.join(android_dir, "key.properties")

        # Get keystore details from config, environment vars, or user input
        keystore_config = config.get("keystore", {}) if config else {}

        # Get store password
        store_password = keystore_config.get("store_password")
        if not store_password:
            store_password = os.environ.get("KEYSTORE_PASSWORD")
        if not store_password:
            store_password = getpass.getpass("Enter keystore password: ")

        # Get key password
        key_password = keystore_config.get("key_password")
        if not key_password:
            key_password = os.environ.get("KEY_PASSWORD")
        if not key_password:
            key_password = getpass.getpass(
                "Enter key password (press Enter to use same as keystore): "
            )
            if not key_password:
                key_password = store_password

        # Get alias
        if not alias:
            alias = keystore_config.get("alias")
        if not alias:
            alias = os.environ.get("STORE_ALIAS") or "upload"

        # Make keystore path relative to android directory if possible
        android_path = Path(android_dir)
        keystore_full_path = Path(os.path.abspath(keystore_path))

        try:
            # Try to make the path relative to android directory
            keystore_rel_path = os.path.relpath(keystore_full_path, android_path)
        except ValueError:
            # If on different drives (Windows), use absolute path
            keystore_rel_path = str(keystore_full_path)
            logger.warning(
                "Using absolute path for keystore in key.properties (different drives detected)"
            )

        # Create key.properties content
        properties_content = f"""storePassword={store_password}
keyPassword={key_password}
keyAlias={alias}
storeFile={keystore_rel_path.replace(os.sep, '/')}
"""

        # Write the key.properties file
        try:
            with open(key_properties_path, "w", encoding="utf-8") as f:
                f.write(properties_content)
            # Set appropriate permissions (if on Unix-like system)
            if os.name == "posix":
                try:
                    os.chmod(key_properties_path, 0o600)  # Owner read/write only
                    logger.debug("Set file permissions 0600 for %s", key_properties_path)
                except (OSError, IOError) as e:
                    logger.warning("Failed to set permissions on key.properties: %s", e)
            logger.info("Created key.properties at %s", key_properties_path)
            return True
        except (OSError, IOError) as e:
            error_msg = f"Failed to write key.properties: {e}"
            logger.error(error_msg)
            raise FlutLockError(error_msg) from e
    except FlutLockError:
        # Just re-raise FlutLockError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating key.properties: {e}"
        logger.error(error_msg)
        raise FlutLockError(error_msg) from e


def build_flutter_app(flutter_project_path, build_type="apk"):
    """Build the Flutter app with the specified build type."""
    try:
        cmd = ["flutter", "build", build_type, "--release"]

        logger.info("Building Flutter %s in release mode", build_type)
        success, output = run_command(cmd, cwd=flutter_project_path)

        if not success:
            error_msg = f"Flutter build failed: {output}"
            logger.error(error_msg)

            # Add specific troubleshooting advice for common error patterns
            if "key.properties" in output and "not found" in output:
                logger.info(
                    "Troubleshooting: Make sure key.properties file is in the android/ directory"
                )
            elif "keystore" in output and "does not exist" in output:
                logger.info(
                    "Troubleshooting: The keystore file path specified in key.properties is incorrect"
                )
            elif "Gradle" in output and "failed" in output:
                logger.info("Troubleshooting: Check your Flutter project's Gradle configuration")

            raise BuildError(error_msg)

        # Determine the output file path based on build type
        if build_type == "apk":
            # For APK, the output is usually in build/app/outputs/flutter-apk/
            output_dir = os.path.join(
                flutter_project_path, "build", "app", "outputs", "flutter-apk"
            )
            output_pattern = os.path.join(output_dir, "app-release.apk")
        else:  # appbundle
            # For App Bundle, the output is in build/app/outputs/bundle/release/
            output_dir = os.path.join(
                flutter_project_path, "build", "app", "outputs", "bundle", "release"
            )
            output_pattern = os.path.join(output_dir, "app-release.aab")

        # Check if the output file exists
        if os.path.exists(output_pattern):
            logger.info("Build completed: %s", output_pattern)
            return output_pattern
        else:
            # Look for similarly named files if the expected file isn't found
            try:
                similar_files = []
                for file in os.listdir(output_dir):
                    if file.endswith(".apk" if build_type == "apk" else ".aab"):
                        similar_files.append(os.path.join(output_dir, file))

                if similar_files:
                    logger.warning("Expected output file not found at %s", output_pattern)
                    logger.info("Found similar files: %s", ", ".join(similar_files))
                    # Use the first similar file
                    return similar_files[0]
            except (FileNotFoundError, NotADirectoryError):
                pass

            error_msg = f"Build output file not found at expected location: {output_pattern}"
            logger.error(error_msg)
            raise BuildError(error_msg)
    except BuildError:
        # Just re-raise BuildError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during build: {e}"
        logger.error(error_msg)
        raise BuildError(error_msg) from e


def verify_signature(output_file):
    """Verify the signature of the APK or AAB file."""
    try:
        if not output_file or not os.path.exists(output_file):
            error_msg = f"Output file not found: {output_file}"
            logger.error(error_msg)
            raise SignatureError(error_msg)

        # Try apksigner first (preferred)
        if shutil.which("apksigner"):
            cmd = ["apksigner", "verify", "--verbose", output_file]
            success, output = run_command(cmd)

            if success and "verified" in output.lower():
                logger.info("Signature verification successful with apksigner")
                return True

            # Provide more detailed error information
            error_details = ""
            if "DOES NOT VERIFY" in output:
                error_details = (
                    "The APK signature is invalid. This could indicate "
                    "a problem with the keystore or signing process."
                )
            elif "failed to parse" in output.lower():
                error_details = (
                    "The file could not be parsed. It may be corrupted or "
                    "not a valid APK/AAB file."
                )

            if error_details:
                logger.error(error_details)
        else:
            logger.warning("apksigner not found, trying jarsigner instead")

            # Fall back to jarsigner
            if shutil.which("jarsigner"):
                cmd = ["jarsigner", "-verify", "-verbose", "-certs", output_file]
                success, output = run_command(cmd)

                if success and "jar verified" in output.lower():
                    logger.info("Signature verification successful with jarsigner")
                    return True
                elif success:
                    logger.warning("Signature verification with jarsigner returned: %s", output)
                    error_msg = "Signature verification failed with jarsigner"
                    logger.error(error_msg)
                    raise SignatureError(error_msg)
            else:
                error_msg = "Neither apksigner nor jarsigner found for verification"
                logger.error(error_msg)
                logger.info(
                    "Install Android SDK Build Tools for apksigner or Java JDK for jarsigner"
                )
                raise SignatureError(error_msg)

        error_msg = f"Signature verification failed: {output}"
        logger.error(error_msg)
        raise SignatureError(error_msg)
    except SignatureError:
        # Just re-raise SignatureError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during signature verification: {e}"
        logger.error(error_msg)
        raise SignatureError(error_msg) from e


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

    return parser.parse_args()


def load_config_file(config_path):
    """
    Load configuration from a JSON file.

    Returns a dictionary with configuration values or empty dict if file doesn't exist.
    """
    if not config_path:
        return {}

    if not os.path.exists(config_path):
        logger.warning("Config file not found at: %s", config_path)
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.info("Configuration loaded from: %s", config_path)
            return config
    except json.JSONDecodeError as e:
        line_no = str(e).split("line", 1)[1].split()[0] if "line" in str(e) else "unknown"
        error_msg = f"Error parsing config file (line {line_no}): {e}"
        logger.error(error_msg)
        logger.info("Please verify your JSON syntax is correct")
        raise ConfigError(error_msg) from e
    except (OSError, IOError) as e:
        error_msg = f"Error reading config file: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def validate_config(config):
    """Validate the configuration and return issues found."""
    issues = []

    # Check for required sections
    if not config:
        issues.append("Configuration is empty")
        return issues

    # Validate keystore section
    keystore = config.get("keystore", {})
    if not keystore:
        issues.append("Missing 'keystore' section")
    else:
        # Check for path if using existing keystore
        if keystore.get("use_existing", False) and not keystore.get("path"):
            issues.append("'keystore.path' is required when 'use_existing' is true")

        # Check for alias
        if not keystore.get("alias"):
            issues.append("Missing 'keystore.alias'")

        # Check for passwords
        if not keystore.get("store_password"):
            issues.append("Missing 'keystore.store_password'")

        if not keystore.get("key_password"):
            issues.append("Missing 'keystore.key_password'")

    # Validate signer section if present
    signer = config.get("signer", {})
    if signer:
        name = signer.get("name")
        if not name:
            issues.append("Missing 'signer.name'")

        # Check other signer fields
        if not signer.get("org_unit"):
            issues.append("Missing 'signer.org_unit'")

        if not signer.get("organization"):
            issues.append("Missing 'signer.organization'")

        if not signer.get("locality"):
            issues.append("Missing 'signer.locality'")

        if not signer.get("state"):
            issues.append("Missing 'signer.state'")

        if not signer.get("country"):
            issues.append("Missing 'signer.country'")

    return issues


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

        # Load configuration file if provided
        config = None
        if args.config:
            try:
                config = load_config_file(args.config)
                logger.debug("Configuration loaded from %s", args.config)
            except ConfigError as e:
                logger.error("Error in configuration file: %s", e)
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
                        "Non-interactive mode requires %s environment variable",
                        store_password_env,
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
            check_dependencies()
        except DependencyError as e:
            logger.error("Dependency check failed: %s", e)
            return 1

        # Set up paths
        flutter_project_path = os.path.abspath(args.path)
        logger.debug("Flutter project path: %s", flutter_project_path)

        if not os.path.isdir(flutter_project_path):
            logger.error("Flutter project directory not found: %s", flutter_project_path)
            return 1

        # Handle keystore
        try:
            if args.keystore_path:
                # Use existing keystore path from argument
                keystore_path = os.path.abspath(args.keystore_path)
                logger.debug("Using keystore path from argument: %s", keystore_path)

                if args.use_existing_keystore:
                    if not os.path.isfile(keystore_path):
                        logger.error("Existing keystore not found: %s", keystore_path)
                        return 1
                    logger.info("Using existing keystore: %s", keystore_path)
                else:
                    # Generate new keystore at specified path
                    logger.debug("Generating new keystore at: %s", keystore_path)
                    generate_keystore(keystore_path, args.keystore_alias, config=config)
            else:
                # Default keystore path
                android_app_dir = os.path.join(flutter_project_path, "android", "app")
                os.makedirs(android_app_dir, exist_ok=True)
                keystore_path = os.path.join(android_app_dir, "upload.keystore")
                logger.debug("Using default keystore path: %s", keystore_path)

                if os.path.exists(keystore_path) and args.use_existing_keystore:
                    logger.info("Using existing keystore at default location: %s", keystore_path)
                else:
                    # Generate new keystore
                    logger.debug("Generating new keystore at default location")
                    generate_keystore(keystore_path, args.keystore_alias, config=config)

        except KeystoreError as e:
            logger.error("Keystore error: %s", e)
            return 1

        # Create key.properties
        try:
            create_key_properties(
                flutter_project_path, keystore_path, args.keystore_alias, config=config
            )
        except FlutLockError as e:
            logger.error("Error creating key.properties: %s", e)
            return 1

        # Build Flutter app
        if not args.skip_build:
            try:
                # If appbundle was specified in older versions of the tool, convert it to aab
                build_type = args.build_type
                if build_type == "appbundle":
                    build_type = "aab"
                    logger.warning("'appbundle' option is deprecated, using 'aab' instead")

                output_file = build_flutter_app(flutter_project_path, build_type)

                # Verify signature
                if args.verify:
                    if output_file:
                        verify_signature(output_file)
                    else:
                        logger.warning("No output file found, skipping signature verification")
            except BuildError as e:
                logger.error("Build error: %s", e)
                return 1
            except SignatureError as e:
                logger.error("Signature verification error: %s", e)
                return 1

        logger.info("FlutLock completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.error("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.debug("Stack trace: %s", traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
