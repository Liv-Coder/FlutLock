# Technical Context: FlutLock

## Technologies Used

- **Python 3**: Core implementation language
- **Flutter SDK**: Required for build commands
- **JDK**: Required for `keytool` and other Java-based utilities
- **Android SDK**: Required for `apksigner` and build verification
- **argparse**: For command-line interface implementation
- **getpass**: For secure password input
- **os/subprocess**: For executing system commands
- **logging**: For structured logging

## Development Setup

- Python 3.6+ required
- Flutter SDK must be in PATH
- JDK 8+ required for keystore operations
- Android SDK tools must be accessible

## Technical Constraints

- Must work on multiple operating systems (Windows, macOS, Linux)
- Must handle sensitive data securely (passwords, keystores)
- Cannot modify Flutter SDK or Android SDK
- Must be compatible with standard Flutter project structures
- Should work in both interactive and non-interactive environments

## Dependencies

- **Direct Dependencies**:
  - Python standard library
  - Flutter SDK (external)
  - JDK (external)
  - Android SDK (external)
- **Optional Future Dependencies**:
  - PyYAML for configuration files
  - Google API client libraries for Play Store integration
  - Python-dotenv for .env file support
  - Fastlane (external) for additional deployment options

## Security Considerations

- Never store keystores or passwords in version control
- Use secure input methods for passwords
- Support environment variables for CI/CD environments
- Verify signatures after builds
- Proper file permissions for generated keystores
