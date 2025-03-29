#!/usr/bin/env python3
"""
Backward compatibility script for FlutLock.
This script provides backward compatibility with the original sign_flutter_app.py
by importing and using the functionality from the new flutter_signer package.
"""

import os
import sys
import warnings

# Add parent directory to system path to find flutter_signer package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Show deprecation warning
warnings.warn(
    "This script is deprecated and will be removed in a future version. "
    "Please use 'python -m flutter_signer' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from the new package structure
from flutter_signer import main

if __name__ == "__main__":
    sys.exit(main())
