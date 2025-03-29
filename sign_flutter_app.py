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
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flutlock")


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
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.info(
            "Please install the missing dependencies and ensure they are in your PATH."
        )
        return False

    return True


def run_command(cmd, **kwargs):
    """Run a shell command and return the output."""
    try:
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            **kwargs,
        )

        if result.returncode != 0:
            logger.error(
                f"Command failed with code {result.returncode}: {result.stderr.strip()}"
            )
            return False, result.stderr.strip()

        return True, result.stdout.strip()
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return False, str(e)


def generate_keystore(keystore_path, alias=None, validity=25 * 365, config=None):
    """Generate a new keystore file."""
    if os.path.exists(keystore_path):
        logger.warning(f"Keystore already exists at {keystore_path}")
        overwrite = input("Overwrite existing keystore? (y/N): ").lower() == "y"
        if not overwrite:
            logger.info("Using existing keystore.")
            return True

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

    # Get signer information from config or user input
    signer_config = config.get("signer", {}) if config else {}

    # Get distinguished name components
    name = signer_config.get("name")
    if not name:
        name = input("Enter your name (CN): ")

    org_unit = signer_config.get("org_unit")
    if not org_unit:
        org_unit = (
            input("Enter organizational unit (OU) [Development]: ") or "Development"
        )

    org = signer_config.get("organization")
    if not org:
        org = input("Enter organization (O) [Your Company]: ") or "Your Company"

    locality = signer_config.get("locality")
    if not locality:
        locality = input("Enter locality/city (L): ")

    state = signer_config.get("state")
    if not state:
        state = input("Enter state/province (ST): ")

    country = signer_config.get("country")
    if not country:
        country = input("Enter country code (C) [US]: ") or "US"

    # Build DN string
    dname = f"CN={name}, OU={org_unit}, O={org}, L={locality}, ST={state}, C={country}"

    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(keystore_path)), exist_ok=True)

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
    ]

    # Pass passwords through environment to avoid shell history
    env = os.environ.copy()
    env["STOREPASS"] = store_password
    env["KEYPASS"] = key_password

    success, output = run_command(
        cmd, env=env, input=f"{store_password}\n{key_password}\n"
    )

    if success:
        logger.info(f"Keystore generated successfully at {keystore_path}")
        # Set appropriate permissions (if on Unix-like system)
        if os.name == "posix":
            os.chmod(keystore_path, 0o600)  # Owner read/write only
        return True
    else:
        logger.error(f"Failed to generate keystore: {output}")
        return False


def create_key_properties(flutter_project_path, keystore_path, alias=None, config=None):
    """Create or update the key.properties file in the Flutter project."""
    android_dir = os.path.join(flutter_project_path, "android")

    if not os.path.isdir(android_dir):
        logger.error(f"Android directory not found in {flutter_project_path}")
        return False

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

    # Create key.properties content
    properties_content = f"""storePassword={store_password}
keyPassword={key_password}
keyAlias={alias}
storeFile={keystore_rel_path.replace(os.sep, '/')}
"""

    # Write the key.properties file
    try:
        with open(key_properties_path, "w") as f:
            f.write(properties_content)
        # Set appropriate permissions (if on Unix-like system)
        if os.name == "posix":
            os.chmod(key_properties_path, 0o600)  # Owner read/write only
        logger.info(f"Created key.properties at {key_properties_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write key.properties: {e}")
        return False


def build_flutter_app(flutter_project_path, build_type="apk"):
    """Build the Flutter app with the specified build type."""
    cmd = ["flutter", "build", build_type, "--release"]

    logger.info(f"Building Flutter {build_type} in release mode")
    success, output = run_command(cmd, cwd=flutter_project_path)

    if not success:
        logger.error(f"Flutter build failed: {output}")
        return None

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
        logger.info(f"Build completed: {output_pattern}")
        return output_pattern
    else:
        logger.error(
            f"Build output file not found at expected location: {output_pattern}"
        )
        return None


def verify_signature(output_file):
    """Verify the signature of the APK or AAB file."""
    if not output_file or not os.path.exists(output_file):
        logger.error(f"Output file not found: {output_file}")
        return False

    # Try apksigner first (preferred)
    if shutil.which("apksigner"):
        cmd = ["apksigner", "verify", "--verbose", output_file]
        success, output = run_command(cmd)

        if success and "verified" in output.lower():
            logger.info(f"Signature verification successful with apksigner")
            return True
    else:
        logger.warning("apksigner not found, trying jarsigner instead")

        # Fall back to jarsigner
        if shutil.which("jarsigner"):
            cmd = ["jarsigner", "-verify", "-verbose", "-certs", output_file]
            success, output = run_command(cmd)

            if success and "jar verified" in output.lower():
                logger.info(f"Signature verification successful with jarsigner")
                return True
            elif success:
                logger.warning(
                    f"Signature verification with jarsigner returned: {output}"
                )
                return False
        else:
            logger.error("Neither apksigner nor jarsigner found for verification")
            return False

    logger.error(f"Signature verification failed: {output}")
    return False


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Automate Flutter app signing process.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to Flutter project root directory",
    )

    parser.add_argument(
        "--keystore", type=str, help="Path to existing keystore file (optional)"
    )

    parser.add_argument("--alias", type=str, help="Alias for the keystore (optional)")

    parser.add_argument(
        "--build-type",
        type=str,
        choices=["apk", "appbundle"],
        default="apk",
        help="Flutter build output type (apk or appbundle)",
    )

    parser.add_argument(
        "--verify", action="store_true", help="Verify the signature after building"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building the app (useful for testing key generation)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file with signing information",
    )

    return parser.parse_args()


def load_config_file(config_path):
    """
    Load configuration from a JSON file.

    Returns a dictionary with configuration values or empty dict if file doesn't exist.
    """
    if not config_path or not os.path.exists(config_path):
        logger.debug(f"Config file not found at: {config_path}")
        return {}

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from: {config_path}")
            return config
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return {}


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
    args = parse_args()

    # Set log level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Load configuration if specified
    config = None
    if args.config:
        config = load_config_file(args.config)

        # Validate configuration
        if config:
            issues = validate_config(config)
            if issues:
                logger.warning("Configuration validation issues found:")
                for issue in issues:
                    logger.warning(f"- {issue}")
                logger.info("Will prompt for missing or invalid values")

    # Check dependencies
    if not check_dependencies():
        if args.skip_build:
            logger.warning(
                "Dependency check failed but continuing due to --skip-build flag"
            )
        else:
            return 1

    # Prepare paths
    flutter_project_path = os.path.abspath(args.path)

    if not os.path.isdir(flutter_project_path):
        logger.error(f"Flutter project directory not found: {flutter_project_path}")
        return 1

    # Use keystore from config if specified and --keystore arg not provided
    keystore_config = config.get("keystore", {}) if config else {}
    use_existing_keystore = keystore_config.get("use_existing", False)

    # Handle keystore
    if args.keystore:
        # Use existing keystore from argument
        keystore_path = os.path.abspath(args.keystore)
        if not os.path.isfile(keystore_path):
            logger.error(f"Keystore file not found: {keystore_path}")
            return 1
        logger.info(f"Using existing keystore: {keystore_path}")
    elif use_existing_keystore and keystore_config.get("path"):
        # Use existing keystore from config
        keystore_path = os.path.abspath(keystore_config.get("path"))
        if not os.path.isfile(keystore_path):
            logger.error(f"Keystore file from config not found: {keystore_path}")
            return 1
        logger.info(f"Using existing keystore from config: {keystore_path}")
    else:
        # Generate new keystore
        keystore_path = os.path.join(
            flutter_project_path, "android", "app", "upload.keystore"
        )
        logger.info(f"Generating new keystore at: {keystore_path}")
        if not generate_keystore(keystore_path, args.alias, config=config):
            return 1

    # Create key.properties
    if not create_key_properties(
        flutter_project_path, keystore_path, args.alias, config=config
    ):
        return 1

    # Skip build if requested
    if args.skip_build:
        logger.info("Skipping build step (--skip-build flag used)")
        return 0

    # Build the app
    output_file = build_flutter_app(flutter_project_path, args.build_type)
    if not output_file:
        return 1

    # Verify signature if requested
    if args.verify:
        if not verify_signature(output_file):
            return 1

    logger.info(f"Flutter app successfully built and signed: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
