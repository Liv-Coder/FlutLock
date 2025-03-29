#!/usr/bin/env python3
"""
FlutLock: Flutter Signing Automation Tool

A command-line tool to automate the Android app signing process for Flutter applications.
Handles keystore generation, key.properties file creation, and build commands.
"""

import argparse
import getpass
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


def generate_keystore(keystore_path, alias=None, validity=25 * 365):
    """Generate a new keystore file."""
    if os.path.exists(keystore_path):
        logger.warning(f"Keystore already exists at {keystore_path}")
        overwrite = input("Overwrite existing keystore? (y/N): ").lower() == "y"
        if not overwrite:
            logger.info("Using existing keystore.")
            return True

    # Get keystore details
    store_password = os.environ.get("KEYSTORE_PASSWORD")
    key_password = os.environ.get("KEY_PASSWORD")

    if not store_password:
        store_password = getpass.getpass("Enter keystore password: ")

    if not key_password:
        key_password = getpass.getpass(
            "Enter key password (press Enter to use same as keystore): "
        )
        if not key_password:
            key_password = store_password

    if not alias:
        alias = os.environ.get("STORE_ALIAS") or "upload"

    # Get distinguished name components
    name = input("Enter your name (CN): ")
    org_unit = input("Enter organizational unit (OU) [Development]: ") or "Development"
    org = input("Enter organization (O) [Your Company]: ") or "Your Company"
    locality = input("Enter locality/city (L): ")
    state = input("Enter state/province (ST): ")
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


def create_key_properties(flutter_project_path, keystore_path, alias=None):
    """Create or update the key.properties file in the Flutter project."""
    android_dir = os.path.join(flutter_project_path, "android")

    if not os.path.isdir(android_dir):
        logger.error(f"Android directory not found in {flutter_project_path}")
        return False

    key_properties_path = os.path.join(android_dir, "key.properties")

    # Get passwords
    store_password = os.environ.get("KEYSTORE_PASSWORD")
    key_password = os.environ.get("KEY_PASSWORD")

    if not store_password:
        store_password = getpass.getpass("Enter keystore password: ")

    if not key_password:
        key_password = getpass.getpass(
            "Enter key password (press Enter to use same as keystore): "
        )
        if not key_password:
            key_password = store_password

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

    try:
        with open(key_properties_path, "w") as f:
            f.write(properties_content)

        # Set appropriate permissions (if on Unix-like system)
        if os.name == "posix":
            os.chmod(key_properties_path, 0o600)  # Owner read/write only

        logger.info(f"Created key.properties at {key_properties_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create key.properties: {e}")
        return False


def build_flutter_app(flutter_project_path, build_type="apk"):
    """Build the Flutter app with the specified build type."""
    if build_type not in ["apk", "appbundle"]:
        logger.error(f"Invalid build type: {build_type}")
        return False

    cmd = ["flutter", "build", build_type, "--release"]

    logger.info(f"Building Flutter {build_type}...")
    success, output = run_command(cmd, cwd=flutter_project_path)

    if success:
        logger.info(f"Flutter {build_type} built successfully")

        # Extract the output file path from Flutter's output
        output_pattern = (
            r"Built (.+?)(?:$|\s+\(|\()" if build_type == "apk" else r"Built (.+\.aab)"
        )
        match = re.search(output_pattern, output)

        if match:
            return True, match.group(1)
        else:
            logger.warning(f"Could not determine output file path from Flutter output")
            return True, None
    else:
        logger.error(f"Failed to build Flutter {build_type}: {output}")
        return False, None


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
        description="FlutLock: Automate Android app signing for Flutter applications",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--path", required=True, help="Path to the Flutter project root"
    )

    parser.add_argument(
        "--keystore", help="Path to existing keystore (will generate if not provided)"
    )

    parser.add_argument(
        "--alias", help='Keystore alias (default: from env var or "upload")'
    )

    parser.add_argument(
        "--build-type",
        choices=["apk", "appbundle"],
        default="apk",
        help="Type of build to generate",
    )

    parser.add_argument(
        "--verify", action="store_true", help="Verify the signature after building"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main():
    """Main entry point of the script."""
    args = parse_args()

    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate Flutter project path
    if not os.path.isdir(args.path):
        logger.error(f"Flutter project directory not found: {args.path}")
        return 1

    # Check dependencies
    if not check_dependencies():
        return 1

    # Determine keystore path
    if args.keystore:
        keystore_path = args.keystore
    else:
        # Default to android/app/upload.keystore in the Flutter project
        keystore_path = os.path.join(args.path, "android", "app", "upload.keystore")

    # Handle keystore
    if not args.keystore or not os.path.exists(args.keystore):
        logger.info(f"Keystore not found, generating new one at: {keystore_path}")
        if not generate_keystore(keystore_path, args.alias):
            return 1
    else:
        logger.info(f"Using existing keystore: {keystore_path}")

    # Create key.properties
    if not create_key_properties(args.path, keystore_path, args.alias):
        return 1

    # Build the app
    success, output_file = build_flutter_app(args.path, args.build_type)
    if not success:
        return 1

    # Verify signature if requested
    if args.verify and output_file:
        if not verify_signature(output_file):
            logger.warning("Signature verification failed, but build was successful")

    logger.info("Flutter app signing and build completed successfully")
    if output_file:
        logger.info(f"Output file: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
