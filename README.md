# FlutLock: Flutter Signing Automator

A command-line tool to automate the Android app signing process for Flutter applications.

## Features

- Generates keystore files or uses existing ones
- Creates and manages `key.properties` file for Flutter projects
- Executes Flutter build commands for APK and App Bundle
- Verifies signatures using Android SDK tools
- Works across Windows, macOS, and Linux environments

## Installation

### Prerequisites

- Python 3.6+
- Flutter SDK (in PATH)
- JDK 8+ (for keystore operations)
- Android SDK (for signature verification)

### Setup

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/flutlock.git
cd flutlock
```

No external Python dependencies are required for the base version.

## Usage

### Basic Command

```bash
python sign_flutter_app.py --path /path/to/flutter/project
```

### Options

```
--path PATH             Path to Flutter project root directory
--keystore PATH         Path to existing keystore file (optional)
--alias ALIAS           Alias for the keystore (optional)
--build-type TYPE       Build type: apk or appbundle (default: apk)
--verify                Verify the signature after building
--config PATH           Path to JSON configuration file
```

### Environment Variables

You can use environment variables instead of entering passwords interactively:

- `KEYSTORE_PASSWORD`: Password for the keystore
- `KEY_PASSWORD`: Password for the key
- `STORE_ALIAS`: Alias for the key in the keystore

### JSON Configuration

You can use a JSON configuration file to specify all options and avoid interactive prompts:

```bash
python sign_flutter_app.py --path /path/to/flutter/project --config config.json
```

Sample JSON configuration file:

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

If any values are missing in the JSON file, you will be prompted to enter them interactively.

## Examples

Generate a new keystore and build an APK:

```bash
python sign_flutter_app.py --path /path/to/flutter/project --verify
```

Use an existing keystore and build an App Bundle:

```bash
python sign_flutter_app.py --path /path/to/flutter/project --keystore /path/to/existing.keystore --alias upload --build-type appbundle
```

## Development

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
