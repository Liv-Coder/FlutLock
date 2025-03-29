#!/bin/bash
# Example script for using FlutLock in a CI environment
# This script demonstrates how to use FlutLock in a CI pipeline

# Set environment variables for keystore information
export KEYSTORE_PASSWORD="your-secure-password"
export KEY_PASSWORD="your-secure-key-password"
export STORE_ALIAS="upload"

# Clone your Flutter project (if needed)
# git clone https://github.com/yourusername/your-flutter-project.git
# cd your-flutter-project

# Assuming you're already in your Flutter project directory
# and FlutLock is in the parent directory

# Run FlutLock with non-interactive mode (using environment variables)
python ../flutter-signing-automator/sign_flutter_app.py \
  --path . \
  --build-type appbundle \
  --verify

# Now you can upload the generated AAB to the Play Store
# For example, using the Google Play Android Publisher API
# or a service like Fastlane 