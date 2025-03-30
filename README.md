# FlutLock: Flutter Signing Automator

A command-line tool to automate the Android app signing process for Flutter applications.

## Features

- Generates keystore files or uses existing ones
- Creates and manages `key.properties` file for Flutter projects
- Updates app-level build.gradle.kts/build.gradle with signing configurations
- Executes Flutter build commands for APK and App Bundle
- Verifies signatures using Android SDK tools
- Works across Windows, macOS, and Linux environments
- Supports non-interactive mode for CI/CD environments
- Comprehensive error handling with clear messages
- Modern Python package structure for easy integration

## Installation

### Prerequisites

- Python 3.7+
- Flutter SDK (in PATH)
- JDK 8+ (for keystore operations)
- Android SDK (for signature verification)

### Direct Installation

Install from PyPI:

```bash
pip install flutlock
```

### Development Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/flutlock.git
cd flutlock
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Project Structure

The FlutLock project follows a modern Python package structure:

```
flutlock/
├── config/                   # Example configuration files
├── docs/                     # Documentation
│   ├── configuration.md      # Configuration documentation
│   └── commands.md           # Command reference and usage patterns
├── example/                  # Sample Flutter app for testing
├── examples/                 # Example Python scripts demonstrating usage
│   ├── ci_cd_example.py      # CI/CD integration example
│   ├── config_file_example.py # Config-based usage example
│   ├── optimized_config_example.py # Advanced config example
│   └── sign_flutter_app.py   # Legacy compatibility script
├── src/                      # Source code package
│   └── flutter_signer/       # Main package
│       ├── core/             # Core functionality
│       ├── integrations/     # External integrations (future)
│       └── utils/            # Utility modules
├── tests/                    # Test suite
├── flutlock                  # Direct CLI entry point
├── pyproject.toml            # Project metadata
├── README.md                 # Project documentation
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── setup.py                  # Package setup script
└── sign_flutter_app.py       # Backward compatibility script
```

## Usage

### Basic Command

```bash
flutlock --path /path/to/flutter/project
```

For Python module usage:

```bash
python -m flutter_signer --path /path/to/flutter/project
```

### Comprehensive Help

FlutLock now includes enhanced help commands:

```bash
# Basic help with command options
flutlock --help

# Advanced help with detailed information and examples
flutlock --help-advanced
```

See the full [Commands Reference](docs/commands.md) for detailed documentation.

### Command Line Options

```
Basic Options:
  --path PATH             Path to Flutter project
  --config PATH           Path to JSON configuration file
  --version               Show version information and exit
  --help-advanced         Show advanced help information and exit

Build Options:
  --build-type {apk,aab}  Build type: apk or aab (Android App Bundle)
  --verify                Verify app signature after build
  --no-verify             Skip signature verification
  --skip-build            Skip the build step (useful for testing keystores)
  --update-gradle         Update app-level build.gradle with signing configuration
  --no-update-gradle      Skip updating build.gradle file

Keystore Options:
  --keystore-path PATH    Path to existing keystore or where to create a new one
  --keystore-alias ALIAS  Keystore alias to use
  --use-existing-keystore Use an existing keystore instead of generating a new one
  --signing-config-name NAME  Custom name for the signing configuration in build.gradle

CI/CD Environment Options:
  --non-interactive       Run in non-interactive mode (for CI/CD environments)
  --keystore-password-env ENV_VAR
                          Environment variable containing keystore password
  --key-password-env ENV_VAR
                          Environment variable containing key password

Logging Options:
  -v, --verbose           Enable verbose output
  -q, --quiet             Suppress all non-error output
```

### Environment Variables

You can use environment variables instead of entering passwords interactively:

- `KEYSTORE_PASSWORD`: Password for the keystore
- `KEY_PASSWORD`: Password for the key (optional if same as keystore password)

### JSON Configuration

You can use a JSON configuration file to specify all options and avoid interactive prompts:

```bash
flutlock --config config/flutlock_config.json
```

Sample JSON configuration file:

```json
{
  "keystore": {
    "use_existing": false,
    "path": "${PROJECT_DIR}/android/app/upload.keystore",
    "alias": "upload",
    "store_password": "${KEYSTORE_PASSWORD:-keystore123456}",
    "key_password": "${KEY_PASSWORD:-key123456}"
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
    "verify": true,
    "skip_build": false,
    "update_gradle": true
  },
  "flutter": {
    "package": "com.example.${APP_NAME}",
    "flavors": {
      "dev": { "applicationId": "com.example.${APP_NAME}.dev" },
      "prod": { "applicationId": "com.example.${APP_NAME}" }
    }
  }
}
```

See [Configuration Documentation](docs/configuration.md) for detailed information about configuration options and variable substitution.

## Common Usage Examples

### Basic Usage

Generate a new keystore and build an APK:

```bash
flutlock
```

Use an existing keystore and build an App Bundle:

```bash
flutlock --keystore-path /path/to/existing.keystore --keystore-alias upload --build-type aab
```

### CI/CD Integration

For CI/CD environments, use non-interactive mode with environment variables:

```bash
export KEYSTORE_PASSWORD="your_keystore_password"
export KEY_PASSWORD="your_key_password"

flutlock --non-interactive --keystore-alias upload
```

Or with a configuration file:

```bash
flutlock --non-interactive --config config/flutlock_config.json
```

## Development

### Running Tests

Run tests with pytest:

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=flutter_signer tests/
```

### Branching Strategy

This project follows a simple branching strategy:

- `main`: Production-ready code. All code in this branch should be thoroughly tested and stable.
- `development`: Active development branch where ongoing work happens.

When contributing:

1. Create feature branches from `development`
2. Submit pull requests to the `development` branch
3. After testing and review, changes will be merged to `main` for release

### Continuous Integration

GitHub Actions workflows are set up to:

- Run tests for all branches
- Perform additional deployment steps only on the `main` branch
- Ensure code quality through linting and testing

## License

MIT License - see the [LICENSE](LICENSE) file for details.
