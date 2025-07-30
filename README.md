# FlutLock: Flutter Signing Automator

A high-performance command-line tool to automate the Android app signing process for Flutter applications. Built with Dart for superior performance and native compilation.

[![pub package](https://img.shields.io/pub/v/flutlock.svg)](https://pub.dev/packages/flutlock)
[![pub points](https://img.shields.io/pub/points/flutlock)](https://pub.dev/packages/flutlock/score)
[![popularity](https://img.shields.io/pub/popularity/flutlock)](https://pub.dev/packages/flutlock/score)
[![Tests](https://img.shields.io/badge/tests-164%20passing-green.svg)](https://github.com/Liv-Coder/flutlock)
[![Performance](https://img.shields.io/badge/startup-70x%20faster-orange.svg)](https://github.com/Liv-Coder/flutlock)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📦 Installation

### Global Installation (Recommended)

```bash
# Install FlutLock globally using pub
dart pub global activate flutlock

# Verify installation
flutlock --version
```

### Local Installation

Add FlutLock to your `pubspec.yaml`:

```yaml
dev_dependencies:
  flutlock: ^1.0.0
```

Then run:

```bash
dart pub get
dart run flutlock --version
```

### Requirements

- **Dart SDK**: >=2.17.0 <4.0.0
- **Flutter SDK**: Latest stable version (for Flutter projects)
- **JDK**: 8+ (for keystore operations)
- **Android SDK**: Optional (for signature verification)

## 🚀 Quick Start

```bash
# Create a new Flutter project
flutter create my_app
cd my_app

# Setup project with Feature Wise Clean Architecture
flutlock --setup-project --architecture feature-clean

# Generate keystore and build signed APK
flutlock --keystore-path android/app/keystore.jks --build-apk
```

## Features

### 🚀 Core Signing Features

- **Keystore Management**: Generate new keystores or use existing ones with full validation
- **Key Properties**: Automatically create and manage `key.properties` files for Flutter projects
- **Gradle Integration**: Update app-level build.gradle/build.gradle.kts with signing configurations
- **Build Automation**: Execute Flutter build commands for APK and App Bundle (AAB)
- **Signature Verification**: Verify app signatures using Android SDK tools
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **CI/CD Ready**: Full support for non-interactive mode and environment variables

### 🏗️ Architecture Generation Features

- **8 Architecture Patterns**: Generate complete Flutter project structures with predefined patterns
  - **Flat/Simple**: Basic lib/ organization with minimal folder structure
  - **Layered**: Organized by technical layers (models, views, controllers) with GetX
  - **Feature-First**: Vertical slicing by features with Provider and HTTP
  - **BLoC**: Business Logic Component pattern with state management
  - **MVVM**: Model-View-ViewModel pattern with Provider
  - **Clean**: Domain-driven design with clear layer separation
  - **Feature Wise Clean**: Hybrid approach combining Feature-First with Clean Architecture
  - **Redux**: Redux pattern with actions, reducers, and store
- **Automatic Dependency Management**: Add architecture-specific dependencies to `pubspec.yaml`
- **Template System**: Generate boilerplate files with proper imports and structure
- **CLI Integration**: Seamlessly integrated with existing project setup workflow

### 🔧 Project Setup & Analysis

- **Automatic Setup**: Initialize Flutter projects for Android signing with interactive guidance
- **Structure Analysis**: Detect missing directories and files required for Android signing
- **Template System**: Generate Android project files using 5 built-in templates
- **Safety Features**: Automatic backup of existing files before modifications
- **Validation**: Comprehensive project structure validation and reporting
- **Fix Automation**: Automatically repair missing or incorrect project components

### ⚡ Performance & Developer Experience

- **70x faster startup** compared to Python implementation (7ms cold start)
- **40% less memory usage** with native Dart compilation (~15MB memory footprint)
- **164 comprehensive tests** ensuring reliability and stability
- **Strong type safety** with Dart's advanced type system
- **Rich CLI interface** with 25+ command-line options
- **JSON schema validation** for configuration files
- **Comprehensive error handling** with clear, actionable messages
- **Template management** with CLI commands for file generation

## 📁 Project Structure

FlutLock follows a clean, modular architecture:

```text
flutlock/
├── bin/                      # Executable entry point
│   └── flutlock.dart         # Main CLI application
├── lib/                      # Dart source code
│   ├── src/
│   │   ├── cli/              # Command-line interface
│   │   ├── core/             # Core functionality modules
│   │   └── utils/            # Utility classes and helpers
│   └── flutlock.dart         # Public API exports
├── test/                     # Comprehensive test suite (164 tests)
├── docs/                     # Documentation and guides
├── flutlock.exe              # Pre-compiled Windows binary
├── pubspec.yaml              # Dart dependencies and metadata
├── LICENSE                   # Project license
└── README.md                 # This documentation
```

## 📖 Complete Command Reference

### Basic Usage

The simplest way to use FlutLock:

```bash
# Basic usage - interactive mode in current directory
flutlock

# Specify Flutter project path
flutlock --path /path/to/flutter/project

# Use configuration file
flutlock --config flutlock_config.json
```

### Help and Information

Get help and version information:

```bash
# Basic help with all command options
flutlock --help

# Advanced help with detailed examples
flutlock --help-advanced

# Show version information
flutlock --version

# Check system dependencies
flutlock --check-deps
```

## 🛠️ Command Line Options

### Basic Options

| Option            | Type   | Default | Description                                                              |
| ----------------- | ------ | ------- | ------------------------------------------------------------------------ |
| `--path`          | String | `.`     | Path to Flutter project directory                                        |
| `--config`        | String | -       | Path to JSON configuration file. Use `global` to auto-find global config |
| `--version`       | Flag   | -       | Show version information and exit                                        |
| `--help`          | Flag   | -       | Show basic help message and exit                                         |
| `--help-advanced` | Flag   | -       | Show advanced help with examples and exit                                |

**Examples:**

```bash
# Work in current directory
flutlock

# Specify project path
flutlock --path /home/user/my_flutter_app

# Use configuration file
flutlock --config config/production.json

# Auto-find global configuration
flutlock --config global
```

### Build Options

| Option                                   | Type   | Default | Description                                              |
| ---------------------------------------- | ------ | ------- | -------------------------------------------------------- |
| `--build-type`                           | Choice | `apk`   | Build type: `apk` or `aab` (Android App Bundle)          |
| `--verify` / `--no-verify`               | Flag   | `true`  | Verify app signature after build                         |
| `--skip-build`                           | Flag   | `false` | Skip the build step (useful for testing keystores)       |
| `--update-gradle` / `--no-update-gradle` | Flag   | `true`  | Update app-level build.gradle with signing configuration |
| `--only-update-gradle`                   | Flag   | `false` | Only update build.gradle without other operations        |

**Examples:**

```bash
# Build APK (default)
flutlock --build-type apk

# Build App Bundle for Play Store
flutlock --build-type aab

# Generate keystore only, skip build
flutlock --skip-build

# Build without signature verification
flutlock --no-verify

# Only update Gradle configuration
flutlock --only-update-gradle
```

### Keystore Options

| Option                    | Type   | Default   | Description                                           |
| ------------------------- | ------ | --------- | ----------------------------------------------------- |
| `--keystore-path`         | String | -         | Path to existing keystore or where to create new one  |
| `--keystore-alias`        | String | -         | Keystore alias to use                                 |
| `--use-existing-keystore` | Flag   | `false`   | Use existing keystore instead of generating new one   |
| `--signing-config-name`   | String | `release` | Custom name for signing configuration in build.gradle |

**Examples:**

```bash
# Use existing keystore
flutlock --use-existing-keystore --keystore-path android/app/release.keystore --keystore-alias upload

# Create keystore at specific path
flutlock --keystore-path /secure/location/keystore.jks --keystore-alias production

# Custom signing configuration name
flutlock --signing-config-name production
```

### CI/CD and Environment Options

| Option                    | Type   | Default             | Description                                          |
| ------------------------- | ------ | ------------------- | ---------------------------------------------------- |
| `--non-interactive`       | Flag   | `false`             | Run in non-interactive mode (for CI/CD environments) |
| `--keystore-password-env` | String | `KEYSTORE_PASSWORD` | Environment variable containing keystore password    |
| `--key-password-env`      | String | `KEY_PASSWORD`      | Environment variable containing key password         |

**Examples:**

```bash
# Non-interactive mode with default env vars
flutlock --non-interactive

# Custom environment variable names
flutlock --non-interactive --keystore-password-env MY_KEYSTORE_PASS --key-password-env MY_KEY_PASS

# CI/CD pipeline usage
export KEYSTORE_PASSWORD="secure_password"
export KEY_PASSWORD="secure_key_password"
flutlock --non-interactive --build-type aab
```

### Project Setup Options

| Option              | Type | Default | Description                                                  |
| ------------------- | ---- | ------- | ------------------------------------------------------------ |
| `--setup-project`   | Flag | `false` | Initialize Flutter project for Android signing (interactive) |
| `--check-structure` | Flag | `false` | Check project structure and report missing components        |
| `--fix-structure`   | Flag | `false` | Automatically fix missing project structure components       |
| `--dry-run`         | Flag | `false` | Show what would be done without making changes               |
| `--force`           | Flag | `false` | Force overwrite existing files during setup                  |
| `--no-backup`       | Flag | `false` | Skip creating backups of existing files during setup         |

**Examples:**

```bash
# Interactive project setup
flutlock --setup-project

# Check what's missing
flutlock --check-structure

# Preview fixes without applying
flutlock --fix-structure --dry-run

# Apply fixes with backups (default)
flutlock --fix-structure

# Force overwrite without backups
flutlock --fix-structure --force --no-backup
```

### Template Management Options

| Option                 | Type   | Default | Description                                                     |
| ---------------------- | ------ | ------- | --------------------------------------------------------------- |
| `--list-templates`     | Flag   | `false` | List all available templates and exit                           |
| `--create-template`    | String | -       | Create file from template (format: `template_name:output_path`) |
| `--validate-templates` | Flag   | `false` | Validate all embedded templates and exit                        |

**Examples:**

```bash
# List available templates
flutlock --list-templates

# Create Android build.gradle from template
flutlock --create-template android_build_gradle:android/build.gradle

# Create app build.gradle with project context
flutlock --path /my/project --create-template android_app_build_gradle:android/app/build.gradle

# Force overwrite existing file
flutlock --create-template android_manifest:android/app/src/main/AndroidManifest.xml --force

# Validate all templates
flutlock --validate-templates
```

### Architecture Generation Options

| Option                 | Type   | Default | Description                                                         |
| ---------------------- | ------ | ------- | ------------------------------------------------------------------- |
| `--architecture`       | String | -       | Flutter architecture pattern to generate (use with --setup-project) |
| `--list-architectures` | Flag   | `false` | List all available Flutter architecture patterns and exit           |

**Available Architecture Patterns:**

- `flat` - Flat/Simple Structure: Basic lib/ organization with minimal folder structure
- `layered` - Layered (By Type) Architecture: Organized by technical layers with GetX
- `feature` - Feature-First (Vertical) Architecture: Organized by features with Provider
- `bloc` - BLoC-Based Architecture: Business Logic Component pattern with state management
- `mvvm` - MVVM (Model-View-ViewModel): Model-View-ViewModel pattern with Provider
- `clean` - Clean Architecture: Domain-driven design with clear layer separation
- `feature-clean` - Feature Wise Clean: Hybrid approach combining Feature-First with Clean Architecture
- `redux` - Redux-Style (Flutter_Redux): Redux pattern with actions, reducers, and store

**Examples:**

```bash
# List available architecture patterns
flutlock --list-architectures

# Generate project with flat architecture
flutlock --setup-project --architecture flat

# Generate project with layered architecture (includes GetX dependency)
flutlock --setup-project --architecture layered

# Generate project with clean architecture
flutlock --setup-project --architecture clean

# Generate project with feature-wise clean architecture (recommended for large apps)
flutlock --setup-project --architecture feature-clean

# Interactive architecture selection
flutlock --setup-project --architecture
```

## 🏗️ Architecture Patterns Deep Dive

### Feature Wise Clean Architecture (Recommended)

The **Feature Wise Clean Architecture** (`feature-clean`) is FlutLock's most comprehensive architecture pattern, combining the benefits of Feature-First organization with Clean Architecture principles. This hybrid approach is ideal for medium to large-scale Flutter applications.

#### 🎯 Key Benefits

- **Scalability**: Each feature is self-contained and can be developed independently
- **Maintainability**: Clear separation of concerns with domain-driven design
- **Testability**: Each layer can be tested in isolation with proper dependency injection
- **Team Collaboration**: Multiple developers can work on different features simultaneously
- **Code Reusability**: Shared components and core utilities are centralized

#### 📁 Generated Structure

```text
lib/
├── core/                           # Shared utilities and base classes
│   ├── constants/                  # App-wide constants
│   ├── errors/                     # Custom exceptions and failures
│   ├── network/                    # HTTP client and network utilities
│   ├── usecases/                   # Base usecase classes
│   └── utils/                      # Helper functions and utilities
├── shared/                         # Reusable components across features
│   ├── services/                   # Shared services (storage, etc.)
│   └── widgets/                    # Common UI components
├── features/                       # Feature-based organization
│   ├── auth/                       # Authentication feature
│   │   ├── data/                   # Data layer
│   │   │   ├── datasources/        # Remote/local data sources
│   │   │   ├── models/             # Data models with JSON serialization
│   │   │   └── repositories/       # Repository implementations
│   │   ├── domain/                 # Business logic layer
│   │   │   ├── entities/           # Business entities
│   │   │   ├── repositories/       # Repository interfaces
│   │   │   └── usecases/           # Business use cases
│   │   └── presentation/           # UI layer
│   │       ├── bloc/               # BLoC state management
│   │       ├── pages/              # Screen widgets
│   │       └── widgets/            # Feature-specific widgets
│   ├── home/                       # Home feature (similar structure)
│   └── profile/                    # Profile feature (similar structure)
├── injection_container.dart        # Dependency injection setup
└── main.dart                       # App entry point
```

#### 🔧 Generated Dependencies

The architecture automatically adds these dependencies to your `pubspec.yaml`:

```yaml
dependencies:
  # State Management
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5

  # Dependency Injection
  get_it: ^7.6.4
  injectable: ^2.3.2

  # Functional Programming
  dartz: ^0.10.1

  # HTTP Client
  http: ^1.1.0

  # Local Storage
  shared_preferences: ^2.2.2

dev_dependencies:
  # Code Generation
  injectable_generator: ^2.4.1
  build_runner: ^2.4.7

  # Testing
  bloc_test: ^9.1.5
```

#### 🚀 Usage Example

```bash
# Create a new Flutter project with Feature Wise Clean Architecture
flutter create my_app
cd my_app

# Generate the complete architecture
flutlock --setup-project --architecture feature-clean

# Install dependencies
flutter pub get

# Generate dependency injection
flutter packages pub run build_runner build

# Run the app
flutter run
```

### 📊 Architecture Comparison Guide

Choose the right architecture pattern for your project:

| Architecture      | Best For              | Team Size | Complexity | State Management | Dependencies   |
| ----------------- | --------------------- | --------- | ---------- | ---------------- | -------------- |
| **Flat**          | Learning, prototypes  | 1-2       | Low        | setState         | Minimal        |
| **Layered**       | Small-medium apps     | 2-4       | Medium     | GetX             | GetX, HTTP     |
| **Feature**       | Medium apps           | 3-6       | Medium     | Provider         | Provider, HTTP |
| **BLoC**          | Medium-large apps     | 4-8       | High       | BLoC             | flutter_bloc   |
| **MVVM**          | Medium apps           | 3-6       | Medium     | Provider         | Provider       |
| **Clean**         | Large enterprise apps | 5+        | High       | Manual           | dartz, http    |
| **Feature-Clean** | Large scalable apps   | 5+        | High       | BLoC             | Complete stack |
| **Redux**         | Complex state apps    | 4-8       | High       | Redux            | flutter_redux  |

#### 🎯 Recommendations

- **New to Flutter?** Start with `flat` or `layered`
- **Building an MVP?** Use `feature` or `bloc`
- **Enterprise application?** Choose `feature-clean` or `clean`
- **Complex state management?** Consider `redux` or `bloc`
- **Team of 5+ developers?** Use `feature-clean` for best collaboration

### Validation and Utility Options

| Option                     | Type   | Default | Description                                                       |
| -------------------------- | ------ | ------- | ----------------------------------------------------------------- |
| `--validate-config`        | String | -       | Validate configuration file against JSON schema                   |
| `--create-config-template` | Choice | -       | Create configuration template (`basic`, `environment`, `minimal`) |
| `--check-deps`             | Flag   | `false` | Check if required dependencies are installed and exit             |

**Examples:**

```bash
# Validate configuration file
flutlock --validate-config config/flutlock_config.json

# Create basic configuration template
flutlock --create-config-template basic

# Create environment-based template
flutlock --create-config-template environment

# Check system dependencies
flutlock --check-deps
```

### Logging Options

| Option          | Type | Default | Description                                     |
| --------------- | ---- | ------- | ----------------------------------------------- |
| `-v, --verbose` | Flag | `false` | Enable verbose output with detailed information |
| `--debug`       | Flag | `false` | Enable debug output with maximum detail         |
| `-q, --quiet`   | Flag | `false` | Suppress all non-error output                   |

**Examples:**

```bash
# Verbose output
flutlock --verbose

# Debug output (maximum detail)
flutlock --debug

# Quiet mode (errors only)
flutlock --quiet

# Combine with other options
flutlock --build-type aab --verbose
```

FlutLock supports several environment variables for secure, non-interactive operation:

| Variable            | Default | Description                                                     |
| ------------------- | ------- | --------------------------------------------------------------- |
| `KEYSTORE_PASSWORD` | -       | Password for the keystore file                                  |
| `KEY_PASSWORD`      | -       | Password for the key (defaults to keystore password if not set) |
| `FLUTLOCK_CONFIG`   | -       | Path to default configuration file                              |
| `PROJECT_DIR`       | -       | Base project directory for variable substitution                |
| `APP_NAME`          | -       | Application name for variable substitution                      |

**Examples:**

```bash
# Set environment variables
export KEYSTORE_PASSWORD="my_secure_keystore_password"
export KEY_PASSWORD="my_secure_key_password"

# Run in non-interactive mode
flutlock --non-interactive --build-type aab

# Use custom environment variable names
flutlock --non-interactive --keystore-password-env MY_STORE_PASS --key-password-env MY_KEY_PASS
```

## ⚙️ JSON Configuration

FlutLock supports comprehensive JSON configuration files to avoid interactive prompts and standardize builds:

### Basic Configuration

```bash
# Use configuration file
flutlock --config flutlock_config.json

# Auto-find global configuration
flutlock --config global

# Validate configuration before use
flutlock --validate-config flutlock_config.json
```

### Configuration File Structure

```json
{
  "keystore": {
    "use_existing": false,
    "path": "${PROJECT_DIR}/android/app/upload.keystore",
    "alias": "upload",
    "store_password": "${KEYSTORE_PASSWORD:-defaultPassword123}",
    "key_password": "${KEY_PASSWORD:-defaultKeyPassword123}"
  },
  "signer": {
    "name": "Your Name",
    "org_unit": "Development Team",
    "organization": "Your Company Ltd",
    "locality": "Your City",
    "state": "Your State",
    "country": "US"
  },
  "build": {
    "type": "apk",
    "verify": true,
    "skip_build": false,
    "update_gradle": true,
    "signing_config_name": "release"
  },
  "flutter": {
    "package": "com.example.${APP_NAME}",
    "flavors": {
      "dev": {
        "applicationId": "com.example.${APP_NAME}.dev",
        "versionNameSuffix": "-dev"
      },
      "staging": {
        "applicationId": "com.example.${APP_NAME}.staging",
        "versionNameSuffix": "-staging"
      },
      "prod": {
        "applicationId": "com.example.${APP_NAME}"
      }
    }
  },
  "project": {
    "path": ".",
    "force_overwrite": false,
    "create_backups": true
  },
  "logging": {
    "level": "info",
    "verbose": false,
    "quiet": false
  }
}
```

### Variable Substitution

FlutLock supports powerful variable substitution in configuration files:

**Supported Formats:**

- `${VARIABLE_NAME}` - Shell-style substitution
- `${VARIABLE_NAME:-default_value}` - With default value
- `{{VARIABLE_NAME}}` - Mustache-style substitution

**Built-in Variables:**

- `${PROJECT_DIR}` - Current project directory
- `${APP_NAME}` - Application name from pubspec.yaml
- `${PACKAGE_NAME}` - Flutter package name
- `${HOME}` - User home directory

**Examples:**

```json
{
  "keystore": {
    "path": "${HOME}/.flutlock/keystores/${APP_NAME}.keystore",
    "store_password": "${KEYSTORE_PASSWORD:-changeme123}"
  },
  "flutter": {
    "package": "com.${COMPANY:-example}.${APP_NAME}"
  }
}
```

### Configuration Templates

Generate configuration templates for different use cases:

```bash
# Basic template with common options
flutlock --create-config-template basic

# Environment-focused template with variable substitution
flutlock --create-config-template environment

# Minimal template with essential options only
flutlock --create-config-template minimal
```

## 📚 Template System Documentation

FlutLock includes a powerful template system with 5 built-in templates for Android project files:

### Available Templates

| Template Name              | Description                                       | Output File                                |
| -------------------------- | ------------------------------------------------- | ------------------------------------------ |
| `android_build_gradle`     | Root-level build.gradle with Flutter integration  | `android/build.gradle`                     |
| `android_app_build_gradle` | App-level build.gradle with signing configuration | `android/app/build.gradle`                 |
| `android_manifest`         | AndroidManifest.xml with Flutter activity setup   | `android/app/src/main/AndroidManifest.xml` |
| `gradle_properties`        | Gradle properties with AndroidX and JVM settings  | `android/gradle.properties`                |
| `settings_gradle`          | Settings.gradle with app module inclusion         | `android/settings.gradle`                  |

### Template Usage

```bash
# List all available templates
flutlock --list-templates

# Create specific template file
flutlock --create-template android_build_gradle:android/build.gradle

# Create with project context (recommended)
flutlock --path /my/flutter/project --create-template android_app_build_gradle:android/app/build.gradle

# Force overwrite existing files
flutlock --create-template android_manifest:android/app/src/main/AndroidManifest.xml --force

# Skip backup creation
flutlock --create-template gradle_properties:android/gradle.properties --no-backup

# Validate all templates
flutlock --validate-templates
```

### Template Context Variables

Templates support variable substitution with project-specific values:

- `${PROJECT_NAME}` - Flutter project name
- `${PACKAGE_NAME}` - Android package name
- `${KEYSTORE_PATH}` - Relative path to keystore
- `${KEY_ALIAS}` - Keystore alias
- `${MIN_SDK_VERSION}` - Minimum Android SDK version
- `${TARGET_SDK_VERSION}` - Target Android SDK version

## 🎯 Practical Usage Examples

### New Project Setup

Complete setup for a new Flutter project:

```bash
# Navigate to your Flutter project
cd my_flutter_app

# Interactive setup with guidance
flutlock --setup-project

# Build signed APK
flutlock --build-type apk

# Verify the signature
flutlock --verify
```

### Existing Project Integration

Integrate FlutLock into an existing Flutter project:

```bash
# Check current project structure
flutlock --check-structure --path /path/to/flutter/project

# Preview what will be fixed
flutlock --fix-structure --dry-run --path /path/to/flutter/project

# Apply fixes with backups
flutlock --fix-structure --path /path/to/flutter/project

# Build with existing setup
flutlock --path /path/to/flutter/project --build-type aab
```

### Production Builds

Professional production build workflow:

```bash
# Use production keystore
flutlock --use-existing-keystore \
         --keystore-path /secure/production.keystore \
         --keystore-alias production \
         --build-type aab \
         --verify

# With configuration file
flutlock --config config/production.json --build-type aab

# Non-interactive for automation
export KEYSTORE_PASSWORD="$PRODUCTION_KEYSTORE_PASSWORD"
export KEY_PASSWORD="$PRODUCTION_KEY_PASSWORD"
flutlock --non-interactive --config config/production.json
```

### CI/CD Integration

Complete CI/CD pipeline integration:

```bash
# GitHub Actions / GitLab CI example
export KEYSTORE_PASSWORD="${{ secrets.KEYSTORE_PASSWORD }}"
export KEY_PASSWORD="${{ secrets.KEY_PASSWORD }}"

# Check dependencies first
flutlock --check-deps

# Build and verify
flutlock --non-interactive \
         --keystore-path android/app/release.keystore \
         --keystore-alias release \
         --build-type aab \
         --verify \
         --verbose

# Upload artifacts (build outputs in build/app/outputs/)
```

### Development Workflow

Daily development workflow examples:

```bash
# Quick development build
flutlock --skip-build  # Generate keystore only

# Test keystore without building
flutlock --skip-build --verify

# Update only Gradle configuration
flutlock --only-update-gradle

# Verbose output for debugging
flutlock --verbose --build-type apk

# Quiet mode for scripts
flutlock --quiet --non-interactive --config dev.json
```

### Template Management

Working with the template system:

```bash
# Setup project using templates
flutlock --setup-project  # Uses templates automatically

# Manual template usage
flutlock --create-template android_build_gradle:android/build.gradle
flutlock --create-template android_app_build_gradle:android/app/build.gradle
flutlock --create-template android_manifest:android/app/src/main/AndroidManifest.xml

# Validate templates before use
flutlock --validate-templates

# List available templates with descriptions
flutlock --list-templates
```

## ⚡ Performance Information

FlutLock delivers exceptional performance compared to the original Python implementation:

### Performance Metrics (v1.0.0)

| Metric                  | Dart Implementation | Python Implementation | Improvement         |
| ----------------------- | ------------------- | --------------------- | ------------------- |
| **Cold Start Time**     | 7ms                 | 490ms                 | **70x faster**      |
| **Memory Usage**        | ~15MB               | ~25MB                 | **40% less memory** |
| **Dependency Check**    | 317ms               | 1.2s                  | **3.8x faster**     |
| **Keystore Generation** | 732ms               | 1.1s                  | **1.5x faster**     |
| **Binary Size**         | ~8MB                | ~45MB (with deps)     | **82% smaller**     |

### Performance Features

- **Native Compilation**: Compiled to native machine code with `dart compile exe`
- **Zero Startup Overhead**: No interpreter or virtual machine startup time
- **Efficient Memory Management**: Dart's garbage collector optimized for CLI applications
- **Fast I/O Operations**: Native file system operations without Python overhead
- **Optimized Dependencies**: Minimal dependency tree with only essential packages

### Benchmarking

Run performance benchmarks on your system:

```bash
# Run built-in performance tests
dart test test/performance_test.dart

# Compare with Python version (if available)
flutlock --check-deps --verbose  # Shows timing information
```

## 🚨 Error Handling and Troubleshooting

FlutLock provides comprehensive error handling with clear, actionable messages:

### Common Issues and Solutions

#### 1. Flutter SDK Not Found

```
Error: Flutter SDK not found in PATH
```

**Solution:**

```bash
# Add Flutter to your PATH
export PATH="$PATH:/path/to/flutter/bin"

# Verify Flutter installation
flutter doctor

# Check with FlutLock
flutlock --check-deps
```

#### 2. JDK Not Available

```
Error: JDK not found. Keystore operations require JDK 8+
```

**Solution:**

```bash
# Install JDK (Ubuntu/Debian)
sudo apt install openjdk-11-jdk

# Install JDK (macOS with Homebrew)
brew install openjdk@11

# Verify installation
java -version
javac -version
```

#### 3. Android SDK Missing

```
Warning: Android SDK not found. Signature verification will be skipped
```

**Solution:**

```bash
# Install Android SDK via Android Studio or command line tools
# Set ANDROID_HOME environment variable
export ANDROID_HOME=/path/to/android/sdk
export PATH="$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools"
```

#### 4. Project Structure Issues

```
Error: Invalid Flutter project structure
```

**Solution:**

```bash
# Check project structure
flutlock --check-structure

# Automatically fix issues
flutlock --fix-structure

# Preview fixes first
flutlock --fix-structure --dry-run
```

#### 5. Keystore Password Issues

```
Error: Invalid keystore password
```

**Solution:**

```bash
# Use environment variables
export KEYSTORE_PASSWORD="your_password"
export KEY_PASSWORD="your_key_password"

# Or use configuration file
flutlock --config config.json

# Verify keystore manually
keytool -list -keystore android/app/keystore.jks
```

#### 6. Gradle Build Failures

```
Error: Gradle build failed
```

**Solution:**

```bash
# Update only Gradle configuration
flutlock --only-update-gradle

# Check Gradle wrapper
cd android && ./gradlew --version

# Clean and rebuild
cd android && ./gradlew clean
flutlock --build-type apk
```

### Debug Mode

Enable detailed debugging information:

```bash
# Maximum debug output
flutlock --debug --verbose

# Check system dependencies
flutlock --check-deps --verbose

# Validate configuration
flutlock --validate-config config.json --verbose
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Use `--verbose` or `--debug` flags
2. **Validate your setup**: Run `flutlock --check-deps`
3. **Test configuration**: Use `flutlock --validate-config`
4. **Check project structure**: Run `flutlock --check-structure`
5. **Review documentation**: Use `flutlock --help-advanced`

## 🧪 Development and Testing

### Running Tests

FlutLock includes a comprehensive test suite with 164 tests covering all functionality:

```bash
# Run all tests
dart test

# Run tests with coverage
dart test --coverage=coverage

# Run specific test categories
dart test test/cli_test.dart          # CLI interface tests
dart test test/core_test.dart         # Core functionality tests
dart test test/template_test.dart     # Template system tests
dart test test/performance_test.dart  # Performance benchmarks

# Generate coverage report
dart pub global activate coverage
dart pub global run coverage:format_coverage --lcov --in=coverage --out=coverage/lcov.info --report-on=lib
```

### Test Categories

| Category              | Tests | Coverage | Description                                 |
| --------------------- | ----- | -------- | ------------------------------------------- |
| **CLI Tests**         | 45    | 98%      | Command-line interface and argument parsing |
| **Core Tests**        | 52    | 96%      | Keystore generation, project setup, builds  |
| **Template Tests**    | 25    | 100%     | Template system and file generation         |
| **Integration Tests** | 15    | 94%      | End-to-end workflow testing                 |

### Development Workflow

```bash
# Setup development environment
git clone https://github.com/Liv-Coder/flutlock.git
cd flutlock
dart pub get

# Run tests before making changes
dart test

# Make your changes...

# Format and analyze code
dart format .
dart analyze

# Run tests again
dart test

# Compile and test binary
dart compile exe bin/flutlock.dart -o flutlock_dev
./flutlock_dev --version --check-deps
```

### Branching Strategy

This project follows a clean Git workflow:

- **`main`**: Production-ready code with stable releases and tags
- **`development`**: Active development branch for ongoing work
- **`feature/*`**: Feature branches created from `development`
- **`hotfix/*`**: Critical fixes that need immediate release

### Contributing Guidelines

We welcome contributions! Please follow these steps:

1. **Fork the repository** and create a feature branch from `development`
2. **Write comprehensive tests** for new functionality
3. **Follow Dart conventions** and use `dart format`
4. **Update documentation** for user-facing changes
5. **Ensure all tests pass** with `dart test`
6. **Submit a pull request** to the `development` branch

### Code Quality Standards

- **Test Coverage**: Maintain >95% test coverage for new code
- **Documentation**: Document all public APIs and CLI options
- **Performance**: Ensure changes don't degrade startup time or memory usage
- **Compatibility**: Maintain backward compatibility with existing configurations

## 📚 Additional Documentation

### Comprehensive Guides

- **[Template System Guide](docs/TEMPLATE_SYSTEM.md)** - Complete template engine documentation
- **[Implementation Report](docs/IMPLEMENTATION_REPORT.md)** - Technical migration details
- **[Performance Validation](docs/POC_VALIDATION_RESULTS.md)** - Benchmark results and analysis
- **[Configuration Schema](docs/configuration_schema.json)** - JSON schema for validation

### API Documentation

Generate API documentation:

```bash
# Generate documentation
dart doc

# View documentation
open doc/api/index.html
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flutter Team**: For the excellent cross-platform framework and tooling
- **Dart Team**: For the powerful language, native compilation, and performance
- **Android Development Community**: For signing best practices and security guidelines
- **Contributors**: Everyone who provided feedback, bug reports, and improvements
- **Original Python Implementation**: Foundation and inspiration for the Dart version

## 📞 Support and Community

- **📖 Documentation**: Complete guides available in the `docs/` directory
- **🐛 Issues**: Report bugs and request features on [GitHub Issues](https://github.com/Liv-Coder/flutlock/issues)
- **💬 Discussions**: Join community discussions on [GitHub Discussions](https://github.com/Liv-Coder/flutlock/discussions)
- **❓ Help**: Use `flutlock --help-advanced` for detailed examples and troubleshooting

---

<div align="center">

**FlutLock v1.0.0** - Making Flutter Android app signing simple, fast, and reliable.

_Built with ❤️ using Dart for maximum performance and developer experience._

🆕 **New in v1.0.0**: Feature Wise Clean Architecture - The ultimate Flutter project structure for scalable applications!

[![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)](https://dart.dev)
[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![Performance](https://img.shields.io/badge/Performance-70x%20Faster-brightgreen?style=for-the-badge)](https://github.com/Liv-Coder/flutlock)

</div>
