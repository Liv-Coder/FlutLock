#!/usr/bin/env python3
"""
Tests for the CLI module of FlutLock.
"""

import os
import sys
import unittest
from unittest import mock
import importlib

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


class TestCLIModule(unittest.TestCase):
    """Test the CLI module functionality."""

    def setUp(self):
        """Set up test environment."""
        # Save original argv
        self.original_argv = sys.argv.copy()
        # Save original exit function
        self.original_exit = sys.exit

    def tearDown(self):
        """Clean up after tests."""
        # Restore original argv
        sys.argv = self.original_argv
        # Restore original exit function
        sys.exit = self.original_exit

    @mock.patch("flutter_signer.main")
    def test_cli_import(self, mock_main):
        """Test importing the CLI module."""
        # Configure mock to return 0
        mock_main.return_value = 0

        # Import the CLI module
        from flutter_signer import cli

        importlib.reload(cli)  # Reload to ensure fresh state

        # Verify main wasn't called (should only happen when __name__ == "__main__")
        mock_main.assert_not_called()

    @mock.patch("flutter_signer.main")
    @mock.patch("sys.exit")
    def test_cli_execution(self, mock_exit, mock_main):
        """Test executing the CLI module as __main__."""
        # Configure mocks
        mock_main.return_value = 0

        # Set up the __name__ to simulate being run as a script
        from flutter_signer import cli

        importlib.reload(cli)  # Reload to ensure fresh state

        # Simulate running as __main__
        cli_globals = {"__name__": "__main__", "main": mock_main, "sys": sys}
        exec(
            open(
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "src", "flutter_signer", "cli.py")
                )
            ).read(),
            cli_globals,
        )

        # Verify main was called
        mock_main.assert_called_once()
        # Verify sys.exit was called with the return value from main
        mock_exit.assert_called_once_with(0)

    @mock.patch("flutter_signer.main")
    @mock.patch("sys.exit")
    def test_cli_execution_with_error(self, mock_exit, mock_main):
        """Test executing the CLI module with an error return code."""
        # Configure mocks
        mock_main.return_value = 1

        # Set up the __name__ to simulate being run as a script
        from flutter_signer import cli

        importlib.reload(cli)  # Reload to ensure fresh state

        # Simulate running as __main__
        cli_globals = {"__name__": "__main__", "main": mock_main, "sys": sys}
        exec(
            open(
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "src", "flutter_signer", "cli.py")
                )
            ).read(),
            cli_globals,
        )

        # Verify main was called
        mock_main.assert_called_once()
        # Verify sys.exit was called with the error code
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
