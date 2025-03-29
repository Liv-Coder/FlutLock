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
--path PATH             Path to Flutter project root
--keystore PATH         Path to existing keystore (optional)
--alias ALIAS           Keystore alias (optional)
--build-type TYPE       Build type: apk or appbundle (default: apk)
--verify                Verify the signature after building
```

### Environment Variables

You can use environment variables instead of entering passwords interactively:

- `KEYSTORE_PASSWORD`: Password for the keystore
- `KEY_PASSWORD`: Password for the key
- `STORE_ALIAS`: Alias for the key in the keystore

## Examples

Generate a new keystore and build an APK:

```bash
python sign_flutter_app.py --path /path/to/flutter/project --verify
```

Use an existing keystore and build an App Bundle:

```bash
python sign_flutter_app.py --path /path/to/flutter/project --keystore /path/to/existing.keystore --alias upload --build-type appbundle
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.
