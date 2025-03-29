"""Keystore generation and management functionality."""

import getpass
import logging
import os

from ..utils.commands import run_command
from ..utils.exceptions import KeystoreError

logger = logging.getLogger("flutlock")


def generate_keystore(keystore_path, alias=None, validity=25 * 365, config=None):
    """
    Generate a new keystore file.

    Args:
        keystore_path: Path where keystore will be created
        alias: Keystore alias (default: None)
        validity: Validity period in days (default: 25 years)
        config: Configuration dictionary (default: None)

    Returns:
        bool: True if keystore generation was successful

    Raises:
        KeystoreError: If keystore generation fails
    """
    try:
        if os.path.exists(keystore_path):
            logger.warning("Keystore already exists at %s", keystore_path)
            overwrite = input("Overwrite existing keystore? (y/N): ").lower() == "y"
            if not overwrite:
                logger.info("Using existing keystore.")
                return True
            else:
                # Delete the existing keystore to avoid alias conflict
                try:
                    os.remove(keystore_path)
                    logger.info("Deleted existing keystore at %s", keystore_path)
                except (OSError, IOError) as e:
                    error_msg = f"Failed to delete existing keystore: {e}"
                    logger.error(error_msg)
                    raise KeystoreError(error_msg) from e

        # Get keystore details from config, environment vars, or user input
        keystore_config = config.get("keystore", {}) if config else {}

        # Get store password
        store_password = keystore_config.get("store_password")
        if not store_password:
            store_password = os.environ.get("KEYSTORE_PASSWORD")
        if not store_password:
            store_password = getpass.getpass("Enter keystore password: ")

            # Validate password strength
            if len(store_password) < 6:
                logger.warning(
                    "Warning: Using a short keystore password. For better security, use at least 8 characters."
                )

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

        # Get signer information from config or user input
        signer_config = config.get("signer", {}) if config else {}

        # Get distinguished name components
        name = signer_config.get("name")
        if not name:
            name = input("Enter your name (CN): ")
            if not name:
                error_msg = "Name (CN) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        org_unit = signer_config.get("org_unit")
        if not org_unit:
            org_unit = (
                input("Enter organizational unit (OU) [Development]: ") or "Development"
            )

        org = signer_config.get("organization")
        if not org:
            org = input("Enter organization (O) [Your Company]: ") or "Your Company"

        locality = signer_config.get("locality")
        if not locality:
            locality = input("Enter locality/city (L): ")
            if not locality:
                error_msg = "Locality (L) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        state = signer_config.get("state")
        if not state:
            state = input("Enter state/province (ST): ")
            if not state:
                error_msg = "State/province (ST) is required for keystore generation"
                logger.error(error_msg)
                raise KeystoreError(error_msg)

        country = signer_config.get("country")
        if not country:
            country = input("Enter country code (C) [US]: ") or "US"

        # Build DN string - breaking up a long line for better readability
        dname = (
            f"CN={name}, OU={org_unit}, O={org}, "
            f"L={locality}, ST={state}, C={country}"
        )

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(os.path.abspath(keystore_path))
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except (OSError, IOError) as e:
            error_msg = f"Failed to create parent directory for keystore: {e}"
            logger.error(error_msg)
            raise KeystoreError(error_msg) from e

        # Generate keystore
        cmd = [
            "keytool",
            "-genkey",
            "-v",
            "-keystore",
            keystore_path,
            "-alias",
            alias,
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            str(validity),
            "-dname",
            dname,
            "-storepass",
            store_password,
            "-keypass",
            key_password,
        ]

        success, output = run_command(cmd)

        if success:
            logger.info("Keystore generated successfully at %s", keystore_path)
            # Set appropriate permissions (if on Unix-like system)
            if os.name == "posix":
                try:
                    os.chmod(keystore_path, 0o600)  # Owner read/write only
                    logger.debug("Set file permissions 0600 for %s", keystore_path)
                except (OSError, IOError) as e:
                    logger.warning("Failed to set permissions on keystore: %s", e)
            return True
        else:
            error_msg = f"Failed to generate keystore: {output}"
            logger.error(error_msg)
            raise KeystoreError(error_msg)
    except KeystoreError:
        # Just re-raise KeystoreError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error generating keystore: {e}"
        logger.error(error_msg)
        raise KeystoreError(error_msg) from e
