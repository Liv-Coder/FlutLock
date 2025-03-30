# FlutLock Tests

This directory contains tests for the FlutLock tool. The tests are designed to validate the functionality of the tool across different platforms (Windows, macOS, Linux) and ensure it works correctly with different Flutter project configurations.

## Test Files

- `test_flutlock.py`: Main tests for the FlutLock tool functionality
- `test_cli.py`: Tests for the command-line interface
- `test_custom_signing_config.py`: Tests for the custom signing configuration feature

## Running Tests

### Prerequisites

Before running the tests, ensure you have the following dependencies installed:

- Python 3.7 or higher
- Flutter SDK
- Java Development Kit (JDK)
- Android SDK tools

### Running All Tests

To run all tests with coverage reporting:

```bash
pytest --cov=src/flutter_signer tests/
```

### Running Specific Tests

To run a specific test file:

```bash
pytest tests/test_custom_signing_config.py
```

To run a specific test class or method:

```bash
pytest tests/test_custom_signing_config.py::TestCustomSigningConfig::test_custom_signing_config_name_groovy
```

## Cross-Platform Testing

FlutLock is designed to work across different platforms. The GitHub Actions workflow in `.github/workflows/flutlock-test.yml` automatically runs the tests on Windows, macOS, and Linux environments.

To ensure the tests pass on all platforms when developing locally:

1. Test on your primary development platform first
2. If possible, test on other platforms before submitting changes
3. Use platform-independent path handling (use `os.path` functions)
4. Watch for platform-specific command execution differences

## Integration Testing

For more comprehensive testing, you can use the example scripts in the `examples/` directory:

```bash
# Set environment variables for testing
export KEYSTORE_PASSWORD="test_password"
export KEY_PASSWORD="test_password"

# Run examples with --skip-build to test without building Flutter app
python -m examples.custom_signing_config_example --path=/path/to/flutter/project --signing-config-name=testing --skip-build
```

## Troubleshooting Failed Tests

If tests fail:

1. Check that all dependencies are correctly installed
2. Verify Flutter, JDK, and Android SDK are in your PATH
3. Try running the tests with verbose output: `pytest -v tests/`
4. For CI failures, check the GitHub Actions logs for platform-specific issues
5. For path-related issues, check both Windows and Unix-style path separators
