"""Configuration file handling for FlutLock."""

import json
import logging
import os

from .exceptions import ConfigError

logger = logging.getLogger("flutlock")


def load_config_file(config_path):
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary with configuration values or empty dict if file doesn't exist.

    Raises:
        ConfigError: If the configuration file is invalid or unreadable
    """
    if not config_path:
        return {}

    if not os.path.exists(config_path):
        logger.warning("Config file not found at: %s", config_path)
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.info("Configuration loaded from: %s", config_path)
            return config
    except json.JSONDecodeError as e:
        line_no = (
            str(e).split("line", 1)[1].split()[0] if "line" in str(e) else "unknown"
        )
        error_msg = f"Error parsing config file (line {line_no}): {e}"
        logger.error(error_msg)
        logger.info("Please verify your JSON syntax is correct")
        raise ConfigError(error_msg) from e
    except (OSError, IOError) as e:
        error_msg = f"Error reading config file: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def validate_config(config):
    """
    Validate the configuration and return issues found.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation issues found
    """
    issues = []

    # Check for required sections
    if not config:
        issues.append("Configuration is empty")
        return issues

    # Validate keystore section
    keystore = config.get("keystore", {})
    if not keystore:
        issues.append("Missing 'keystore' section")
    else:
        # Check for path if using existing keystore
        if keystore.get("use_existing", False) and not keystore.get("path"):
            issues.append("'keystore.path' is required when 'use_existing' is true")

        # Check for alias
        if not keystore.get("alias"):
            issues.append("Missing 'keystore.alias'")

        # Check for passwords
        if not keystore.get("store_password"):
            issues.append("Missing 'keystore.store_password'")

        if not keystore.get("key_password"):
            issues.append("Missing 'keystore.key_password'")

    # Validate signer section if present
    signer = config.get("signer", {})
    if signer:
        name = signer.get("name")
        if not name:
            issues.append("Missing 'signer.name'")

        # Check other signer fields
        if not signer.get("org_unit"):
            issues.append("Missing 'signer.org_unit'")

        if not signer.get("organization"):
            issues.append("Missing 'signer.organization'")

        if not signer.get("locality"):
            issues.append("Missing 'signer.locality'")

        if not signer.get("state"):
            issues.append("Missing 'signer.state'")

        if not signer.get("country"):
            issues.append("Missing 'signer.country'")

    return issues
