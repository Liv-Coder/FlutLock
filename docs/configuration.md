# FlutLock Configuration Options

FlutLock supports various configuration options to customize its behavior. These options can be specified through command-line arguments or a JSON configuration file.

## Configuration File Format

FlutLock uses JSON configuration files with support for variable substitution. Configuration files should be structured as follows:

```json
{
  "keystore": {
    "path": "path/to/keystore.jks",
    "alias": "upload",
    "store_password": "your_store_password",
    "key_password": "your_key_password",
    "use_existing": false
  },
  "signer": {
    "name": "Your Name",
    "org_unit": "Development",
    "organization": "Your Company",
    "locality": "Your City",
    "state": "Your State",
    "country": "US"
  },
  "build": {
    "type": "apk",
    "verify": true
  },
  "flutter": {
    "path": "/path/to/flutter/sdk",
    "additional_args": ["--release", "--split-debug-info=build/debug-info"]
  }
}
```

## Variable Substitution

FlutLock supports variable substitution in configuration files using the `${VAR_NAME}` syntax. You can also specify default values using `${VAR_NAME:-default_value}`.

```json
{
  "keystore": {
    "path": "${PROJECT_DIR}/android/app/keystore.jks",
    "alias": "${KEYSTORE_ALIAS:-upload}",
    "store_password": "${KEYSTORE_PASSWORD}"
  }
}
```

### Special Variables

- `${PROJECT_DIR}`: Absolute path to the Flutter project directory
- `${APP_NAME}`: Name of the Flutter application (derived from project directory name)

## Configuration Sections

### Keystore Section

The `keystore` section configures keystore generation and usage:

| Option           | Type    | Description                         | Default                                |
| ---------------- | ------- | ----------------------------------- | -------------------------------------- |
| `path`           | String  | Path to the keystore file           | `android/app/upload.keystore`          |
| `alias`          | String  | Keystore alias                      | `upload`                               |
| `store_password` | String  | Keystore password                   | Prompted if not provided               |
| `key_password`   | String  | Key password                        | Same as store_password if not provided |
| `use_existing`   | Boolean | Whether to use an existing keystore | `false`                                |

### Signer Section

The `signer` section contains information about the certificate signer (used when generating a new keystore):

| Option         | Type   | Description              | Default                  |
| -------------- | ------ | ------------------------ | ------------------------ |
| `name`         | String | Common Name (CN)         | Prompted if not provided |
| `org_unit`     | String | Organizational Unit (OU) | `Development`            |
| `organization` | String | Organization (O)         | `Your Company`           |
| `locality`     | String | Locality/City (L)        | Prompted if not provided |
| `state`        | String | State/Province (ST)      | Prompted if not provided |
| `country`      | String | Country Code (C)         | `US`                     |

### Build Section

The `build` section configures the Flutter build process:

| Option   | Type    | Description                                    | Default |
| -------- | ------- | ---------------------------------------------- | ------- |
| `type`   | String  | Build type (`apk` or `aab`)                    | `apk`   |
| `verify` | Boolean | Whether to verify the signature after building | `true`  |

### Flutter Section

The `flutter` section configures Flutter-specific options:

| Option            | Type   | Description                                               | Default     |
| ----------------- | ------ | --------------------------------------------------------- | ----------- |
| `path`            | String | Path to the Flutter SDK                                   | System PATH |
| `additional_args` | Array  | Additional arguments to pass to the Flutter build command | `[]`        |

## Command-Line Arguments

Many configuration options can also be specified via command-line arguments:

| Argument                                 | Description                                               | Default                 |
| ---------------------------------------- | --------------------------------------------------------- | ----------------------- |
| `--path`                                 | Path to Flutter project                                   | Current directory (`.`) |
| `--build-type`                           | Build type (`apk` or `aab`)                               | `apk`                   |
| `--verify` / `--no-verify`               | Whether to verify app signature after build               | `--verify`              |
| `--skip-build`                           | Skip the build step                                       | `false`                 |
| `--config`                               | Path to JSON configuration file                           | None                    |
| `--signing-config-name`                  | Custom name for the signing configuration in build.gradle | `release`               |
| `--update-gradle` / `--no-update-gradle` | Whether to update app-level build.gradle                  | `--update-gradle`       |

### CI/CD Environment Options

| Argument                  | Description                                              | Default             |
| ------------------------- | -------------------------------------------------------- | ------------------- |
| `--non-interactive`       | Run in non-interactive mode for CI/CD                    | `false`             |
| `--keystore-path`         | Path to existing keystore or where to create a new one   | None                |
| `--keystore-alias`        | Keystore alias to use                                    | None                |
| `--keystore-password-env` | Environment variable containing keystore password        | `KEYSTORE_PASSWORD` |
| `--key-password-env`      | Environment variable containing key password             | `KEY_PASSWORD`      |
| `--use-existing-keystore` | Use an existing keystore instead of generating a new one | `false`             |

### Logging Options

| Argument           | Description                   | Default |
| ------------------ | ----------------------------- | ------- |
| `--verbose` / `-v` | Enable verbose output         | `false` |
| `--quiet` / `-q`   | Suppress all non-error output | `false` |

## Examples

### Basic Configuration

```json
{
  "keystore": {
    "alias": "upload",
    "path": "android/app/upload.keystore"
  },
  "build": {
    "type": "apk"
  }
}
```

### Environment-Specific Configuration

```json
{
  "keystore": {
    "path": "${PROJECT_DIR}/android/app/keystore.jks",
    "alias": "${KEYSTORE_ALIAS:-upload}",
    "store_password": "${KEYSTORE_PASSWORD}",
    "key_password": "${KEY_PASSWORD:-${KEYSTORE_PASSWORD}}"
  },
  "build": {
    "type": "${BUILD_TYPE:-apk}"
  }
}
```

### Custom Signing Configuration

```json
{
  "keystore": {
    "path": "${PROJECT_DIR}/android/app/keystore.jks",
    "alias": "custom_alias",
    "use_existing": true
  },
  "flutter": {
    "additional_args": ["--flavor", "production"]
  }
}
```

Then use with:

```
flutlock --config=config.json --signing-config-name=production
```

## Troubleshooting Configuration Issues

If you encounter issues with your configuration:

1. Use the `--verbose` flag to see detailed information about configuration processing
2. Check for syntax errors in your JSON file
3. Verify that all required environment variables are set
4. Ensure paths are valid and accessible
5. Check that the Flutter project structure is correct
