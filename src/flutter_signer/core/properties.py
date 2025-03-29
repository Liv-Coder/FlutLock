"""Key.properties file handling functionality."""

import getpass
import logging
import os
from pathlib import Path

from ..utils.exceptions import FlutLockError

logger = logging.getLogger("flutlock")


def create_key_properties(flutter_project_path, keystore_path, alias=None, config=None):
    """
    Create or update the key.properties file in the Flutter project.

    Args:
        flutter_project_path: Path to the Flutter project
        keystore_path: Path to the keystore file
        alias: Keystore alias (default: None)
        config: Configuration dictionary (default: None)

    Returns:
        bool: True if key.properties creation was successful

    Raises:
        FlutLockError: If key.properties creation fails
    """
    try:
        android_dir = os.path.join(flutter_project_path, "android")

        if not os.path.isdir(android_dir):
            error_msg = f"Android directory not found in {flutter_project_path}"
            logger.error(error_msg)
            logger.info(
                "Make sure this is a valid Flutter project with an android directory"
            )
            raise FlutLockError(error_msg)

        key_properties_path = os.path.join(android_dir, "key.properties")

        # Get keystore details from config, environment vars, or user input
        keystore_config = config.get("keystore", {}) if config else {}

        # Get store password
        store_password = keystore_config.get("store_password")
        if not store_password:
            store_password = os.environ.get("KEYSTORE_PASSWORD")
        if not store_password:
            store_password = getpass.getpass("Enter keystore password: ")

        # Get key password
        key_password = keystore_config.get("key_password")
        if not key_password:
            key_password = os.environ.get("KEY_PASSWORD")
        if not key_password:
            key_password = getpass.getpass(
                "Enter key password (press Enter to use same as keystore): "
            )
            if not key_password:
                key_password = store_password

        # Get alias
        if not alias:
            alias = keystore_config.get("alias")
        if not alias:
            alias = os.environ.get("STORE_ALIAS") or "upload"

        # Make keystore path relative to android directory if possible
        android_path = Path(android_dir)
        keystore_full_path = Path(os.path.abspath(keystore_path))

        try:
            # Try to make the path relative to android directory
            keystore_rel_path = os.path.relpath(keystore_full_path, android_path)
        except ValueError:
            # If on different drives (Windows), use absolute path
            keystore_rel_path = str(keystore_full_path)
            logger.warning(
                "Using absolute path for keystore in key.properties (different drives detected)"
            )

        # Create key.properties content
        properties_content = f"""storePassword={store_password}
keyPassword={key_password}
keyAlias={alias}
storeFile={keystore_rel_path.replace(os.sep, '/')}
"""

        # Write the key.properties file
        try:
            with open(key_properties_path, "w", encoding="utf-8") as f:
                f.write(properties_content)
            # Set appropriate permissions (if on Unix-like system)
            if os.name == "posix":
                try:
                    os.chmod(key_properties_path, 0o600)  # Owner read/write only
                    logger.debug(
                        "Set file permissions 0600 for %s", key_properties_path
                    )
                except (OSError, IOError) as e:
                    logger.warning("Failed to set permissions on key.properties: %s", e)
            logger.info("Created key.properties at %s", key_properties_path)
            return True
        except (OSError, IOError) as e:
            error_msg = f"Failed to write key.properties: {e}"
            logger.error(error_msg)
            raise FlutLockError(error_msg) from e
    except FlutLockError:
        # Just re-raise FlutLockError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error creating key.properties: {e}"
        logger.error(error_msg)
        raise FlutLockError(error_msg) from e
