"""Enhanced configuration processing for FlutLock."""

import json
import logging
import os
import re
from pathlib import Path

from .exceptions import ConfigError

logger = logging.getLogger("flutlock")

# Regular expression to match variables like ${VAR_NAME} or ${VAR_NAME:-default_value}
VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z0-9_]+)(?:\:-([^}]*))?\}")


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
        line_no = str(e).split("line", 1)[1].split()[0] if "line" in str(e) else "unknown"
        error_msg = f"Error parsing config file (line {line_no}): {e}"
        logger.error(error_msg)
        logger.info("Please verify your JSON syntax is correct")
        raise ConfigError(error_msg) from e
    except (OSError, IOError) as e:
        error_msg = f"Error reading config file: {e}"
        logger.error(error_msg)
        raise ConfigError(error_msg) from e


def process_config(config, project_path=".", env_vars=None):
    """
    Process configuration with variable substitution.

    Args:
        config: The configuration dictionary
        project_path: Path to the Flutter project
        env_vars: Dictionary of environment variables to use (default: os.environ)

    Returns:
        Processed configuration dictionary with variables substituted
    """
    if config is None:
        return {}

    # Create variables dictionary
    variables = {} if env_vars is None else dict(env_vars)

    # Add special variables
    abs_project_path = os.path.abspath(project_path)
    # Normalize path to use forward slashes for JSON compatibility
    abs_project_path = abs_project_path.replace("\\", "/")
    variables["PROJECT_DIR"] = abs_project_path
    variables["APP_NAME"] = os.path.basename(abs_project_path)

    # Log variables for debugging
    logger.debug("Available variables for substitution:")
    for key, value in variables.items():
        logger.debug("  %s = %s", key, value)

    # Process the configuration as a string for substitution
    config_str = json.dumps(config)
    logger.debug("Raw config before substitution: %s", config_str)

    # Perform variable substitution
    def replace_var(match):
        var_name = match.group(1)
        default_value = match.group(2)  # Will be None if no default provided

        if var_name in variables:
            value = str(variables[var_name])
            # Make sure backslashes are properly escaped for JSON
            value = value.replace("\\", "/")
            logger.debug("Substituting ${%s} with '%s'", var_name, value)
            return value
        elif default_value is not None:
            logger.debug("Using default value '%s' for ${%s}", default_value, var_name)
            return default_value
        else:
            # Leave the variable as is if not found and no default
            logger.debug("Variable ${%s} not found and no default, leaving as is", var_name)
            return match.group(0)

    # Replace all variables in the config string
    processed_str = VARIABLE_PATTERN.sub(replace_var, config_str)

    # Convert back to dictionary
    try:
        processed_config = json.loads(processed_str)
        logger.debug("Processed config after substitution: %s", json.dumps(processed_config))
        return processed_config
    except json.JSONDecodeError as e:
        error_msg = f"Error processing config after variable substitution: {e}"
        logger.error(error_msg)
        logger.debug("Processed string that caused error: %s", processed_str)
        raise ConfigError(error_msg) from e


def validate_config(config):
    """
    Validate configuration against expected schema.

    Args:
        config: The configuration dictionary to validate

    Returns:
        bool: True if valid, raises ConfigError otherwise

    Raises:
        ConfigError: If the configuration is invalid
    """
    # Basic validation for required sections
    if not isinstance(config, dict):
        raise ConfigError("Configuration must be a dictionary")

    # Validate keystore section if present
    if "keystore" in config:
        if not isinstance(config["keystore"], dict):
            raise ConfigError("'keystore' section must be a dictionary")

        # Validate required fields - for now just basic type checking
        keystore = config["keystore"]
        if "alias" in keystore and not isinstance(keystore["alias"], str):
            raise ConfigError("'keystore.alias' must be a string")
        if "path" in keystore and not isinstance(keystore["path"], str):
            raise ConfigError("'keystore.path' must be a string")
        if "use_existing" in keystore and not isinstance(keystore["use_existing"], bool):
            raise ConfigError("'keystore.use_existing' must be a boolean")

    # Validate build section if present
    if "build" in config:
        if not isinstance(config["build"], dict):
            raise ConfigError("'build' section must be a dictionary")

        build = config["build"]
        if "type" in build and build["type"] not in ["apk", "aab"]:
            raise ConfigError("'build.type' must be either 'apk' or 'aab'")
        if "verify" in build and not isinstance(build["verify"], bool):
            raise ConfigError("'build.verify' must be a boolean")

    # Validate signer section if present
    if "signer" in config:
        if not isinstance(config["signer"], dict):
            raise ConfigError("'signer' section must be a dictionary")

    # Validate flutter section if present
    if "flutter" in config:
        if not isinstance(config["flutter"], dict):
            raise ConfigError("'flutter' section must be a dictionary")

        # Validate flavors if present
        flutter = config["flutter"]
        if "flavors" in flutter and not isinstance(flutter["flavors"], dict):
            raise ConfigError("'flutter.flavors' must be a dictionary")

    return True
