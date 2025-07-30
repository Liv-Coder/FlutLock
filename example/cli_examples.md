# FlutLock CLI Examples

This document provides comprehensive examples of using FlutLock from the command line.

## 🚀 Quick Start Examples

### Basic Project Setup

```bash
# Create a new Flutter project
flutter create my_awesome_app
cd my_awesome_app

# Setup project with default configuration
flutlock --setup-project

# Setup with specific architecture
flutlock --setup-project --architecture feature-clean

# Setup with force overwrite (be careful!)
flutlock --setup-project --architecture bloc --force
```

### Architecture Generation

```bash
# List all available architecture patterns
flutlock --list-architectures

# Generate project with different architectures
flutlock --setup-project --architecture flat
flutlock --setup-project --architecture layered
flutlock --setup-project --architecture feature
flutlock --setup-project --architecture bloc
flutlock --setup-project --architecture mvvm
flutlock --setup-project --architecture clean
flutlock --setup-project --architecture feature-clean  # Recommended for large apps
flutlock --setup-project --architecture redux
```

## 🔐 Keystore Management

### Generate New Keystore

```bash
# Interactive keystore generation
flutlock --keystore-path android/app/keystore.jks

# Non-interactive with all parameters
flutlock --keystore-path android/app/keystore.jks \
  --key-alias my-app-key \
  --store-password myStorePassword123 \
  --key-password myKeyPassword123 \
  --validity-years 25

# Generate keystore only (skip build)
flutlock --keystore-path android/app/keystore.jks --skip-build
```

### Use Existing Keystore

```bash
# Use existing keystore
flutlock --use-existing-keystore --keystore-path android/app/existing.jks

# With specific alias
flutlock --use-existing-keystore \
  --keystore-path android/app/existing.jks \
  --key-alias production-key
```

## 🏗️ Build Options

### APK Building

```bash
# Build APK only
flutlock --build-apk --keystore-path android/app/keystore.jks

# Build APK with specific output directory
flutlock --build-apk \
  --keystore-path android/app/keystore.jks \
  --output-dir build/signed-apks
```

### App Bundle (AAB) Building

```bash
# Build App Bundle
flutlock --build-aab --keystore-path android/app/keystore.jks

# Build both APK and AAB
flutlock --build-apk --build-aab --keystore-path android/app/keystore.jks
```

### Build Modes

```bash
# Release build (default)
flutlock --keystore-path android/app/keystore.jks

# Debug build
flutlock --build-mode debug --keystore-path android/app/keystore.jks

# Profile build
flutlock --build-mode profile --keystore-path android/app/keystore.jks
```

## 🔧 Configuration Management

### Configuration Templates

```bash
# Create basic configuration template
flutlock --create-config-template basic

# Create environment-based template
flutlock --create-config-template environment

# Create minimal template
flutlock --create-config-template minimal
```

### Using Configuration Files

```bash
# Use configuration file
flutlock --config flutlock_config.json

# Validate configuration
flutlock --validate-config flutlock_config.json

# Use configuration with overrides
flutlock --config flutlock_config.json --keystore-path android/app/override.jks
```

## 🔍 Project Analysis and Validation

### Structure Analysis

```bash
# Check project structure
flutlock --check-structure

# Check and fix structure issues
flutlock --fix-structure

# Preview fixes without applying
flutlock --fix-structure --dry-run

# Verbose structure analysis
flutlock --check-structure --verbose
```

### Dependency Checking

```bash
# Check system dependencies
flutlock --check-deps

# Check dependencies with verbose output
flutlock --check-deps --verbose
```

### Template Validation

```bash
# Validate all templates
flutlock --validate-templates

# Validate specific template
flutlock --validate-templates --template android_build_gradle
```

## 🚀 CI/CD Examples

### GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build and Sign APK
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      
      - name: Install FlutLock
        run: dart pub global activate flutlock
        
      - name: Setup project
        run: flutlock --setup-project --architecture feature-clean
        
      - name: Build and sign
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          flutlock --non-interactive \
            --keystore-path android/app/keystore.jks \
            --key-alias release-key \
            --build-apk
```

### GitLab CI

```yaml
# .gitlab-ci.yml
build_apk:
  stage: build
  image: cirrusci/flutter:stable
  script:
    - dart pub global activate flutlock
    - flutlock --setup-project --architecture bloc
    - flutlock --non-interactive --keystore-path android/app/keystore.jks --build-apk
  artifacts:
    paths:
      - build/app/outputs/flutter-apk/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    environment {
        KEYSTORE_PASSWORD = credentials('keystore-password')
        KEY_PASSWORD = credentials('key-password')
    }
    stages {
        stage('Setup') {
            steps {
                sh 'dart pub global activate flutlock'
                sh 'flutlock --setup-project --architecture clean'
            }
        }
        stage('Build') {
            steps {
                sh '''
                flutlock --non-interactive \
                  --keystore-path android/app/keystore.jks \
                  --key-alias production-key \
                  --build-aab
                '''
            }
        }
    }
}
```

## 🛠️ Advanced Usage

### Environment Variables

```bash
# Set environment variables for secure CI/CD
export KEYSTORE_PASSWORD="your-secure-password"
export KEY_PASSWORD="your-key-password"
export FLUTTER_BUILD_MODE="release"

# Run with environment variables
flutlock --non-interactive --keystore-path android/app/keystore.jks
```

### Batch Operations

```bash
# Setup multiple projects with the same architecture
for project in app1 app2 app3; do
  cd $project
  flutlock --setup-project --architecture feature-clean --force
  cd ..
done

# Build multiple variants
flutlock --build-apk --build-aab --keystore-path android/app/keystore.jks
```

### Custom Output Directories

```bash
# Organize builds by date
DATE=$(date +%Y%m%d)
flutlock --build-apk \
  --keystore-path android/app/keystore.jks \
  --output-dir "builds/$DATE"

# Organize by version
VERSION=$(grep version pubspec.yaml | cut -d' ' -f2)
flutlock --build-aab \
  --keystore-path android/app/keystore.jks \
  --output-dir "releases/v$VERSION"
```

## 🔍 Troubleshooting Commands

### Verbose Logging

```bash
# Enable verbose output for debugging
flutlock --verbose --keystore-path android/app/keystore.jks

# Maximum verbosity
flutlock --verbose --check-deps --check-structure
```

### Dry Run Mode

```bash
# Preview changes without applying them
flutlock --dry-run --setup-project --architecture bloc
flutlock --dry-run --fix-structure
```

### Help and Information

```bash
# Basic help
flutlock --help

# Advanced help with examples
flutlock --help-advanced

# Version information
flutlock --version

# List all available options
flutlock --help | grep -E "^\s*--"
```

## 📊 Performance Monitoring

```bash
# Time the execution
time flutlock --setup-project --architecture feature-clean

# Monitor memory usage (Linux/macOS)
/usr/bin/time -v flutlock --build-apk --keystore-path android/app/keystore.jks

# Profile with Dart tools
dart --observe flutlock --setup-project --architecture clean
```

---

For more examples and detailed documentation, visit the [FlutLock GitHub repository](https://github.com/Liv-Coder/FlutLock).
