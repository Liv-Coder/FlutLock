# FlutLock Examples

This directory contains examples demonstrating how to use FlutLock both as a CLI tool and as a Dart library.

## 📁 Examples Overview

- **`basic_usage.dart`** - Basic programmatic usage of FlutLock library
- **`cli_examples.md`** - Comprehensive CLI usage examples
- **`flutter_project_setup/`** - Complete Flutter project setup example
- **`architecture_generation.dart`** - Architecture pattern generation examples

## 🚀 Quick Start

> **Note**: This example directory uses a local path dependency (`path: ../`) for development. After FlutLock is published to pub.dev, you can use `flutlock: ^1.0.0` instead.

### 1. CLI Usage

```bash
# Install FlutLock globally (after pub.dev publication)
dart pub global activate flutlock

# Create a new Flutter project
flutter create my_app
cd my_app

# Setup project with Feature Wise Clean Architecture
flutlock --setup-project --architecture feature-clean

# Generate keystore and sign the app
flutlock --keystore-path android/app/keystore.jks
```

### 2. Programmatic Usage

```dart
import 'package:flutlock/flutlock.dart';

void main() async {
  // Initialize FlutLock
  final flutlock = FlutLockCLI();

  // Setup project with architecture
  await flutlock.setupProject(
    architecture: 'feature-clean',
    projectPath: './my_flutter_app',
  );

  // Generate keystore
  await flutlock.generateKeystore(
    keystorePath: 'android/app/keystore.jks',
    keyAlias: 'my-app-key',
  );
}
```

## 📖 Detailed Examples

### Architecture Generation

FlutLock supports 8 different Flutter architecture patterns:

```bash
# List all available architectures
flutlock --list-architectures

# Generate with specific architecture
flutlock --setup-project --architecture feature-clean
flutlock --setup-project --architecture bloc
flutlock --setup-project --architecture clean
```

### CI/CD Integration

```bash
# Non-interactive mode for CI/CD
export KEYSTORE_PASSWORD="your-secure-password"
export KEY_PASSWORD="your-key-password"

flutlock --non-interactive \
  --keystore-path android/app/keystore.jks \
  --key-alias release-key \
  --build-apk
```

### Advanced Configuration

```bash
# Create configuration template
flutlock --create-config-template environment

# Use configuration file
flutlock --config flutlock_config.json

# Validate project structure
flutlock --check-structure --fix-structure
```

## 🔧 Development Setup

To run these examples:

1. **Install FlutLock**:

   ```bash
   dart pub global activate flutlock
   ```

2. **Clone or create a Flutter project**:

   ```bash
   flutter create example_app
   cd example_app
   ```

3. **Run the examples**:

   ```bash
   # Run Dart examples
   dart run example/basic_usage.dart
   dart run example/architecture_generation.dart

   # Follow CLI examples
   cat example/cli_examples.md
   ```

## 📚 Additional Resources

- [FlutLock Documentation](https://github.com/Liv-Coder/FlutLock#readme)
- [Architecture Patterns Guide](https://github.com/Liv-Coder/FlutLock/blob/main/docs/ARCHITECTURE_PATTERNS.md)
- [Template System Documentation](https://github.com/Liv-Coder/FlutLock/blob/main/docs/TEMPLATE_SYSTEM.md)

## 🤝 Contributing

Found an issue with these examples? Please [open an issue](https://github.com/Liv-Coder/FlutLock/issues) or submit a pull request!
