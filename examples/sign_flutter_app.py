#!/usr/bin/env python3
"""
FlutLock: Flutter Signing Automation Tool

A command-line tool to automate the Android app signing process for Flutter applications.
This script is provided for backward compatibility with existing workflows.
It uses the newer flutter_signer package internally.
"""

import os
import sys
import warnings

# Add parent directory to system path to find flutter_signer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Show deprecation warning
warnings.warn(
    "This script is maintained for backward compatibility. "
    "Please use 'flutlock' or 'python -m flutter_signer' for new projects.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from the new package structure
from flutter_signer import main

if __name__ == "__main__":
    sys.exit(main())
