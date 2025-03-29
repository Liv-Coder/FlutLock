# Project Brief: FlutLock - Flutter Signing Automation Tool

## Overview

FlutLock is a tool designed to automate the Android app signing process for Flutter applications. It aims to simplify and secure the signing workflow, making it easier for developers to generate release-ready APKs and App Bundles.

## Core Requirements

- Generate new RSA 2048 keystore if missing
- Use existing keystore when available
- Securely handle passwords and alias information
- Create/update `android/key.properties` with relative paths
- Execute Flutter build commands for APK and App Bundle releases
- Verify signatures using appropriate tools
- Check for dependencies (`flutter`, `keytool`, `apksigner`)
- Provide a clear command-line interface

## Project Goals

- Eliminate manual errors in the signing process
- Ensure security of keystore information
- Support both individual developers and CI/CD environments
- Start with a simple approach and evolve toward a comprehensive build and deployment utility
- Maintain cross-platform compatibility

## Target Users

- Flutter developers who need to sign Android applications
- CI/CD pipeline engineers integrating Flutter build processes
- Development teams looking to standardize their signing workflow
