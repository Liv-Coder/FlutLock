"""Custom exceptions for the FlutLock tool."""


class FlutLockError(Exception):
    """Base exception for all FlutLock errors."""


class DependencyError(FlutLockError):
    """Exception raised for missing dependencies."""


class KeystoreError(FlutLockError):
    """Exception raised for issues with keystore operations."""


class ConfigError(FlutLockError):
    """Exception raised for issues with configuration files."""


class BuildError(FlutLockError):
    """Exception raised for Flutter build issues."""


class SignatureError(FlutLockError):
    """Exception raised for issues with signature verification."""
