# FlutLock Commands and Usage

This document provides comprehensive information about all FlutLock commands, arguments, and usage patterns.

## Command Overview

FlutLock is primarily used as a single command with various options:

```
flutlock [options]
```

## Help Commands

FlutLock provides multiple levels of help:

```bash
# Basic help
flutlock -h
flutlock --help

# Advanced help with detailed information
flutlock --help-advanced
```

## Available Options

### Basic Options

| Option          | Description                       | Default                 |
| --------------- | --------------------------------- | ----------------------- |
| `--path PATH`   | Path to Flutter project           | Current directory (`.`) |
| `--config PATH` | Path to JSON configuration file   | None                    |
| `--version`     | Show version information and exit | N/A                     |

### Build Options

| Option                   | Description                                              | Default |
| ------------------------ | -------------------------------------------------------- | ------- |
| `--build-type {apk,aab}` | Build type: apk or Android App Bundle                    | `apk`   |
| `--verify`               | Verify app signature after build                         | `True`  |
| `--no-verify`            | Skip signature verification                              | N/A     |
| `--skip-build`           | Skip the build step (useful for testing keystores)       | `False` |
| `--update-gradle`        | Update app-level build.gradle with signing configuration | `True`  |
| `--no-update-gradle`     | Skip updating build.gradle file                          | N/A     |

### Keystore Options

| Option                       | Description                                               | Default   |
| ---------------------------- | --------------------------------------------------------- | --------- |
| `--keystore-path PATH`       | Path to existing keystore or where to create a new one    | None      |
| `--keystore-alias ALIAS`     | Keystore alias to use                                     | None      |
| `--use-existing-keystore`    | Use an existing keystore instead of generating a new one  | `False`   |
| `--signing-config-name NAME` | Custom name for the signing configuration in build.gradle | `release` |

### CI/CD Environment Options

| Option                            | Description                                          | Default             |
| --------------------------------- | ---------------------------------------------------- | ------------------- |
| `--non-interactive`               | Run in non-interactive mode (for CI/CD environments) | `False`             |
| `--keystore-password-env ENV_VAR` | Environment variable containing keystore password    | `KEYSTORE_PASSWORD` |
| `--key-password-env ENV_VAR`      | Environment variable containing key password         | `KEY_PASSWORD`      |

### Logging Options

| Option          | Description                   | Default |
| --------------- | ----------------------------- | ------- |
| `-v, --verbose` | Enable verbose output         | `False` |
| `-q, --quiet`   | Suppress all non-error output | `False` |

## Common Usage Patterns

### Basic Usage (Interactive)

The simplest way to use FlutLock is without any arguments. It will prompt for information as needed:

```bash
flutlock
```

### Using a Configuration File

For consistent settings and non-interactive usage, use a JSON configuration file:

```bash
flutlock --config config/flutlock_config.json
```

### Build an Android App Bundle

```bash
flutlock --build-type aab
```

### Only Set Up Signing (Skip Build)

```bash
flutlock --skip-build
```

### Non-Interactive Mode for CI/CD

```bash
flutlock --non-interactive --keystore-path android/app/keystore.jks
```

### Custom Signing Configuration

```bash
flutlock --signing-config-name production
```

### Run from Outside Project Directory

```bash
flutlock --path /path/to/flutter/project
```

### Verbose Output for Debugging

```bash
flutlock --verbose
```

## Environment Variables

FlutLock can use environment variables for sensitive information:

- `KEYSTORE_PASSWORD`: Password for the keystore
- `KEY_PASSWORD`: Password for the key (defaults to keystore password)

Example:

```bash
export KEYSTORE_PASSWORD="your_password"
export KEY_PASSWORD="your_key_password"
flutlock --non-interactive
```

## Configuration File

FlutLock supports JSON configuration files with variable substitution. See [configuration.md](configuration.md) for more details.

## Workflow

1. Checks dependencies (Flutter, keytool, apksigner)
2. Generates or uses existing keystore
3. Creates/updates key.properties file
4. Modifies build.gradle file (if --update-gradle)
5. Runs Flutter build (unless --skip-build)
6. Verifies signature (if --verify)

## Troubleshooting

- Use `--verbose` for detailed logging
- Check paths and permissions
- Verify Android SDK and Flutter installations
- Ensure build.gradle follows standard format
