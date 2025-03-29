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

## Usage

### Basic Command

```bash
python -m flutter_signer --path /path/to/flutter/project
```

For backward compatibility, you can also use:

```bash
flutlock --path /path/to/flutter/project
```

### Command Line Options

```
Basic Options:
  --path PATH             Path to Flutter project (default: current directory)
  --build-type {apk,aab}  Build type: apk or aab (Android App Bundle) (default: apk)
  --verify                Verify app signature after build (default: True)
  --no-verify             Skip signature verification
  --skip-build            Skip the build step (useful for testing keystores)
  --update-gradle         Update app-level build.gradle with signing configuration (default: True)
  --no-update-gradle      Skip updating build.gradle file
  --config PATH           Path to JSON configuration file
  --version               Show version information and exit

CI/CD Environment Options:
  --non-interactive       Run in non-interactive mode (for CI/CD environments)
  --keystore-path PATH    Path to existing keystore or where to create a new one
  --keystore-alias ALIAS  Keystore alias to use
  --keystore-password-env ENV_VAR
                          Environment variable containing keystore password (default: KEYSTORE_PASSWORD)
  --key-password-env ENV_VAR
                          Environment variable containing key password (default: KEY_PASSWORD)
  --use-existing-keystore Use an existing keystore instead of generating a new one

Logging Options:
  -v, --verbose           Enable verbose output
  -q, --quiet             Suppress all non-error output
```

### Environment Variables

You can use environment variables instead of entering passwords interactively:

- `KEYSTORE_PASSWORD`: Password for the keystore
- `KEY_PASSWORD`: Password for the key (optional if same as keystore password)
- `STORE_ALIAS`: Alias for the key in the keystore

### JSON Configuration

You can use a JSON configuration file to specify all options and avoid interactive prompts:

```bash
python -m flutter_signer --path /path/to/flutter/project --config config.json
```

Sample JSON configuration file (placed in the `config` directory):

```json
{
  "keystore": {
    "use_existing": false,
    "path": "path/to/your/keystore.jks",
    "alias": "upload",
    "store_password": "your_keystore_password",
    "key_password": "your_key_password"
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
  }
}
```

If any values are missing in the JSON file, you will be prompted to enter them interactively (unless running in non-interactive mode).

## Examples

### Basic Usage

Generate a new keystore and build an APK:

```bash
python -m flutter_signer --path /path/to/flutter/project
```

Use an existing keystore and build an App Bundle:

```bash
python -m flutter_signer --path /path/to/flutter/project --keystore-path /path/to/existing.keystore --keystore-alias upload --build-type aab
```

### CI/CD Integration

For CI/CD environments, use non-interactive mode with environment variables:

```bash
export KEYSTORE_PASSWORD="your_keystore_password"
export KEY_PASSWORD="your_key_password"

python -m flutter_signer --path /path/to/flutter/project --non-interactive --keystore-alias upload
```

Or with a configuration file:

```bash
python -m flutter_signer --path /path/to/flutter/project --non-interactive --config config.json
```

### GitHub Actions Example

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install FlutLock
        run: pip install flutlock
      - name: Build and Sign App
        run: python -m flutter_signer --path . --non-interactive --keystore-alias upload
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
```

#### Updating build.gradle with signing configuration

By default, FlutLock will update your app-level build.gradle.kts (or build.gradle) file to include the signing configuration. This saves you from manually editing the Gradle file:

```bash
python -m flutter_signer --path /path/to/flutter/project
```

You can skip this step if you prefer to manage your Gradle files manually:

```bash
python -m flutter_signer --path /path/to/flutter/project --no-update-gradle
```

## Project Structure

FlutLock is organized as a modern Python package:

```
flutlock/
├── config/                  # Configuration examples
├── docs/                    # Documentation
├── examples/                # Example scripts
├── src/
│   └── flutter_signer/      # Main package
│       ├── __init__.py
│       ├── cli.py           # Command-line interface
│       ├── core/            # Core functionality
│       │   ├── __init__.py
│       │   ├── exceptions.py # Exception classes
│       │   └── keystore.py  # Keystore management
│       ├── utils/           # Utility modules
│       │   ├── __init__.py
│       │   ├── config.py    # Configuration handling
│       │   ├── dependencies.py # Dependency checking
│       │   └── build.py     # Flutter build commands
│       └── integrations/    # External integrations
│           └── __init__.py
├── tests/                   # Test suite
├── .gitignore
├── LICENSE
├── MANIFEST.in              # Package manifest
├── README.md                # Project documentation
├── pyproject.toml           # Project metadata
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Development dependencies
└── setup.py                 # Package setup script
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
