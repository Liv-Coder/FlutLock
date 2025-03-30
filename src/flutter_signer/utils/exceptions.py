"""Custom exceptions for the FlutLock tool."""


class FlutLockError(Exception):
    """
    Base exception for all FlutLock errors.

    Attributes:
        message (str): Error message
        details (str): Additional details about the error
        suggestions (list): List of troubleshooting suggestions
    """

    def __init__(self, message, details=None, suggestions=None):
        self.message = message
        self.details = details
        self.suggestions = suggestions or []
        super().__init__(self.format_message())

    def format_message(self):
        """Format the complete error message with details and suggestions."""
        msg = self.message
        if self.details:
            msg += f"\nDetails: {self.details}"
        if self.suggestions:
            msg += "\nTroubleshooting suggestions:"
            for suggestion in self.suggestions:
                msg += f"\n  - {suggestion}"
        return msg


class DependencyError(FlutLockError):
    """
    Exception raised for missing dependencies.

    This exception is raised when required external tools like Flutter, JDK,
    or Android SDK tools are missing or not properly configured.
    """

    def __init__(self, message, missing_dependency=None, details=None):
        suggestions = [
            (
                f"Install {missing_dependency} and make sure it's in your PATH"
                if missing_dependency
                else "Check that all required dependencies are installed and in your PATH"
            ),
            "Run 'flutter doctor' to verify your Flutter installation",
            "Ensure JDK is installed for keystore operations",
            "Verify Android SDK tools are accessible",
        ]
        super().__init__(message, details, suggestions)


class KeystoreError(FlutLockError):
    """
    Exception raised for issues with keystore operations.

    This exception is raised when there are problems creating, accessing,
    or using keystores and key.properties files.
    """

    def __init__(self, message, details=None):
        suggestions = [
            "Check if the keystore file exists and is readable",
            "Verify that you have correct permissions to read/write the keystore",
            "Ensure keystore passwords are correct",
            "Confirm that the keystore alias exists",
            "Check if keytool is available in your PATH",
        ]
        super().__init__(message, details, suggestions)


class ConfigError(FlutLockError):
    """
    Exception raised for issues with configuration files.

    This exception is raised when there are problems loading, parsing,
    or validating configuration files.
    """

    def __init__(self, message, details=None, config_file=None):
        suggestions = [
            (
                f"Verify that {config_file} is valid JSON"
                if config_file
                else "Verify that your configuration file is valid JSON"
            ),
            "Check that all required fields are present in the configuration",
            "Ensure environment variables used in the configuration are set",
            "Validate paths in the configuration file",
        ]
        super().__init__(message, details, suggestions)


class BuildError(FlutLockError):
    """
    Exception raised for Flutter build issues.

    This exception is raised when the Flutter build command fails or
    encounters errors during execution.
    """

    def __init__(self, message, details=None, build_type=None):
        suggestions = [
            (
                f"Run 'flutter build {build_type} --verbose' to see detailed errors"
                if build_type
                else "Run the Flutter build command with --verbose to see detailed errors"
            ),
            "Check your Flutter project's pubspec.yaml for errors",
            "Ensure your Android SDK is properly configured",
            "Verify that the signing configuration is correct",
            "Make sure you have internet connectivity for package downloads",
        ]
        super().__init__(message, details, suggestions)


class GradleError(FlutLockError):
    """
    Exception raised for Gradle file modification issues.

    This exception is raised when there are problems modifying
    build.gradle or build.gradle.kts files.
    """

    def __init__(self, message, details=None, file_path=None):
        suggestions = [
            (
                f"Check if {file_path} exists and is readable/writable"
                if file_path
                else "Check if the Gradle file exists and is readable/writable"
            ),
            "Ensure the Gradle file has a standard structure",
            "Verify that the android { } block exists in the file",
            "Consider manually adding the signing configuration if automatic modification fails",
        ]
        super().__init__(message, details, suggestions)


class SignatureError(FlutLockError):
    """
    Exception raised for issues with signature verification.

    This exception is raised when there are problems verifying
    the signature of built APK or AAB files.
    """

    def __init__(self, message, details=None, file_path=None):
        suggestions = [
            (
                f"Verify that {file_path} exists and is a valid APK/AAB file"
                if file_path
                else "Verify that the output file exists and is a valid APK/AAB file"
            ),
            "Check that apksigner tool is available in your PATH",
            "Ensure the keystore used for signing is valid",
            "Make sure the correct keystore was used for signing",
        ]
        super().__init__(message, details, suggestions)
