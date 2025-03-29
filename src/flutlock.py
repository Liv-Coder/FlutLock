#!/usr/bin/env python3
"""
FlutLock: Flutter Signing Automation Tool.

Command-line entry point for the FlutLock tool.
"""

import sys
from flutter_signer.main import main

if __name__ == "__main__":
    sys.exit(main())
