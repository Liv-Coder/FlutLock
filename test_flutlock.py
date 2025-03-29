#!/usr/bin/env python3
"""
Test script for FlutLock tool.
This script demonstrates how to use the FlutLock tool with a sample Flutter project.
"""

import os
import subprocess
import sys
import tempfile
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flutlock_test")


def run_command(cmd, **kwargs):
    """Run a shell command and return the output."""
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
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


def create_test_flutter_project(target_dir):
    """Create a simple Flutter test project."""

    # Check if Flutter is available
    if not shutil.which("flutter"):
        logger.error("Flutter is not installed or not in the PATH")
        return False

    # Create Flutter project
    cmd = ["flutter", "create", "--org", "com.flutlock.test", "flutlock_test_app"]

    logger.info(f"Creating test Flutter project in {target_dir}")
    success, output = run_command(cmd, cwd=target_dir)

    if not success:
        logger.error(f"Failed to create Flutter project: {output}")
        return False

    logger.info("Flutter test project created successfully")
    return os.path.join(target_dir, "flutlock_test_app")


def test_flutlock(test_project_path):
    """Test the FlutLock tool with the test project."""

    # Run FlutLock with the test project
    cmd = [
        sys.executable,
        "sign_flutter_app.py",
        "--path",
        test_project_path,
        "--verify",
        "--verbose",
    ]

    # Set environment variables for non-interactive testing
    # Note: In a real test, you would use more secure methods to handle these credentials
    test_env = os.environ.copy()
    test_env["KEYSTORE_PASSWORD"] = "test_password"
    test_env["KEY_PASSWORD"] = "test_password"
    test_env["STORE_ALIAS"] = "upload"

    logger.info("Running FlutLock with test project")
    success, output = run_command(cmd, env=test_env)

    if not success:
        logger.error(f"FlutLock failed: {output}")
        return False

    logger.info("FlutLock completed successfully")
    logger.info(output)

    # Check if key.properties was created
    key_properties_path = os.path.join(test_project_path, "android", "key.properties")
    if os.path.exists(key_properties_path):
        logger.info(f"key.properties created at {key_properties_path}")
    else:
        logger.error(f"key.properties not found at {key_properties_path}")
        return False

    # Check if keystore was created
    keystore_path = os.path.join(test_project_path, "android", "app", "upload.keystore")
    if os.path.exists(keystore_path):
        logger.info(f"Keystore created at {keystore_path}")
    else:
        logger.error(f"Keystore not found at {keystore_path}")
        return False

    return True


def main():
    """Main test function."""

    logger.info("Starting FlutLock test")

    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary directory at {temp_dir}")

        # Create test Flutter project
        test_project_path = create_test_flutter_project(temp_dir)
        if not test_project_path:
            logger.error("Failed to create test Flutter project")
            return 1

        # Test FlutLock
        if not test_flutlock(test_project_path):
            logger.error("FlutLock test failed")
            return 1

        logger.info("FlutLock test completed successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
