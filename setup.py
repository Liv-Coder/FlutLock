#!/usr/bin/env python3
"""
FlutLock: Flutter Signing Automation Tool
Setup script for distribution
"""

import os
from setuptools import setup, find_packages

# Get version from the package
with open(os.path.join("src", "flutter_signer", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            VERSION = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        VERSION = "0.0.1"

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="flutlock",
    version=VERSION,
    description="Flutter Android App Signing Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/flutlock",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="flutter, android, signing, build, keystore",
    entry_points={
        "console_scripts": [
            "flutlock=flutter_signer:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/flutlock/issues",
        "Source": "https://github.com/yourusername/flutlock",
    },
)
