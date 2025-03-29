#!/usr/bin/env python3
"""
Unit tests for FlutLock tool.
"""

import os
import sys
import tempfile
import unittest
from unittest import mock
import json
from pathlib import Path

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from flutter_signer.core.dependencies import check_dependencies, DependencyError
from flutter_signer.core.keystore import generate_keystore, KeystoreError
from flutter_signer.core.properties import create_key_properties
from flutter_signer.utils.config import load_config_file, ConfigError
from flutter_signer.utils.exceptions import FlutLockError
from flutter_signer.main import parse_args


class TestDependencyCheck(unittest.TestCase):
    """Test the dependency checking functionality."""

    @mock.patch("shutil.which")
    def test_all_dependencies_present(self, mock_which):
        """Test when all dependencies are present."""
        # Configure mock to return True for all dependencies
        mock_which.return_value = "/usr/bin/mock"
        self.assertTrue(check_dependencies())

    @mock.patch("shutil.which")
    def test_missing_dependencies(self, mock_which):
        """Test when dependencies are missing."""

        # Configure mock to return None for flutter
        def mock_which_side_effect(cmd):
            if cmd == "flutter":
                return None
            return "/usr/bin/mock"

        mock_which.side_effect = mock_which_side_effect

        with self.assertRaises(DependencyError):
            check_dependencies()


class TestKeystoreGeneration(unittest.TestCase):
    """Test keystore generation functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.keystore_path = os.path.join(self.test_dir.name, "test.keystore")

        # Mock environment variables
        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                "KEYSTORE_PASSWORD": "test_password",
                "KEY_PASSWORD": "test_password",
                "STORE_ALIAS": "upload",
            },
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.test_dir.cleanup()
        self.env_patcher.stop()

    @mock.patch("flutter_signer.utils.commands.run_command")
    def test_generate_keystore_success(self, mock_run_command):
        """Test successful keystore generation."""
        # Configure mock to return success
        mock_run_command.return_value = (True, "Keystore generated successfully")

        # Call generate_keystore
        result = generate_keystore(self.keystore_path, "upload")

        # Assert that run_command was called
        mock_run_command.assert_called()
        self.assertTrue(result)

    @mock.patch("flutter_signer.utils.commands.run_command")
    def test_generate_keystore_failure(self, mock_run_command):
        """Test failed keystore generation."""
        # Configure mock to return failure
        mock_run_command.return_value = (False, "Failed to generate keystore")

        # Call generate_keystore and expect an exception
        with self.assertRaises(KeystoreError):
            generate_keystore(self.keystore_path, "upload")


class TestKeyPropertiesCreation(unittest.TestCase):
    """Test key.properties file creation."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.flutter_project_path = self.test_dir.name
        self.android_dir = os.path.join(self.flutter_project_path, "android")
        os.makedirs(self.android_dir, exist_ok=True)

        # Create a mock keystore
        self.keystore_path = os.path.join(self.test_dir.name, "test.keystore")
        with open(self.keystore_path, "w") as f:
            f.write("MOCK KEYSTORE")

        # Mock environment variables
        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                "KEYSTORE_PASSWORD": "test_password",
                "KEY_PASSWORD": "test_password",
                "STORE_ALIAS": "upload",
            },
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.test_dir.cleanup()
        self.env_patcher.stop()

    def test_create_key_properties(self):
        """Test creating key.properties file."""
        # Call create_key_properties
        result = create_key_properties(self.flutter_project_path, self.keystore_path, "upload")

        # Check that the key.properties file was created
        key_properties_path = os.path.join(self.android_dir, "key.properties")
        self.assertTrue(os.path.exists(key_properties_path))
        self.assertTrue(result)

        # Check content of key.properties
        with open(key_properties_path, "r") as f:
            content = f.read()
            self.assertIn("storePassword=test_password", content)
            self.assertIn("keyPassword=test_password", content)
            self.assertIn("keyAlias=upload", content)
            self.assertIn("storeFile=", content)


class TestConfigFileHandling(unittest.TestCase):
    """Test configuration file handling."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.test_dir.name, "test_config.json")

    def tearDown(self):
        """Clean up after tests."""
        self.test_dir.cleanup()

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        # Create a valid config file
        valid_config = {
            "keystore": {
                "use_existing": False,
                "path": "path/to/keystore.jks",
                "alias": "upload",
                "store_password": "store_password",
                "key_password": "key_password",
            },
            "build": {"type": "apk", "verify": True},
        }

        with open(self.config_path, "w") as f:
            json.dump(valid_config, f)

        # Load the config
        config = load_config_file(self.config_path)

        # Verify the config
        self.assertEqual(config["keystore"]["alias"], "upload")
        self.assertEqual(config["build"]["type"], "apk")

    def test_load_invalid_config(self):
        """Test loading an invalid configuration file."""
        # Create an invalid JSON file
        with open(self.config_path, "w") as f:
            f.write("invalid json")

        # Attempt to load the config and expect an exception
        with self.assertRaises(ConfigError):
            load_config_file(self.config_path)


class TestArgumentParsing(unittest.TestCase):
    """Test argument parsing."""

    def test_default_args(self):
        """Test default arguments."""
        # Mock sys.argv
        with mock.patch("sys.argv", ["sign_flutter_app.py"]):
            args = parse_args()

            # Check default values
            self.assertEqual(args.path, ".")
            self.assertEqual(args.build_type, "apk")
            self.assertTrue(args.verify)
            self.assertFalse(args.skip_build)
            self.assertIsNone(args.config)

    def test_custom_args(self):
        """Test custom arguments."""
        # Mock sys.argv
        with mock.patch(
            "sys.argv",
            [
                "sign_flutter_app.py",
                "--path",
                "/mock/path",
                "--build-type",
                "aab",
                "--no-verify",
                "--skip-build",
                "--config",
                "config.json",
            ],
        ):
            args = parse_args()

            # Check parsed values
            self.assertEqual(args.path, "/mock/path")
            self.assertEqual(args.build_type, "aab")
            self.assertFalse(args.verify)
            self.assertTrue(args.skip_build)
            self.assertEqual(args.config, "config.json")


if __name__ == "__main__":
    unittest.main()
