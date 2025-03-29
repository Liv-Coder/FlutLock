"""build.gradle.kts file modification functionality."""

import logging
import os
import re
from pathlib import Path
from ..utils.exceptions import FlutLockError

logger = logging.getLogger("flutlock")


def update_app_build_gradle(flutter_project_path, config=None):
    """
    Update the app-level build.gradle.kts file to include signing configuration.

    Args:
        flutter_project_path: Path to the Flutter project
        config: Configuration dictionary (default: None)

    Returns:
        bool: True if build.gradle.kts modification was successful

    Raises:
        FlutLockError: If build.gradle.kts modification fails
    """
    try:
        android_dir = os.path.join(flutter_project_path, "android")
        app_dir = os.path.join(android_dir, "app")

        if not os.path.isdir(app_dir):
            error_msg = f"App directory not found in {android_dir}"
            logger.error(error_msg)
            logger.info("Make sure this is a valid Flutter project with an android/app directory")
            raise FlutLockError(error_msg)

        # Check if key.properties exists
        key_properties_path = os.path.join(android_dir, "key.properties")
        if not os.path.exists(key_properties_path):
            logger.warning("key.properties file not found. Skipping build.gradle.kts modification.")
            logger.info("Create key.properties first using create_key_properties function.")
            return False

        # Find build.gradle.kts or build.gradle
        gradle_kts_path = os.path.join(app_dir, "build.gradle.kts")
        gradle_path = os.path.join(app_dir, "build.gradle")

        if os.path.exists(gradle_kts_path):
            build_gradle_path = gradle_kts_path
            is_kotlin_dsl = True
        elif os.path.exists(gradle_path):
            build_gradle_path = gradle_path
            is_kotlin_dsl = False
        else:
            error_msg = f"Neither build.gradle.kts nor build.gradle found in {app_dir}"
            logger.error(error_msg)
            raise FlutLockError(error_msg)

        # Read the build.gradle file content
        with open(build_gradle_path, "r", encoding="utf-8") as f:
            build_gradle_content = f.read()

        # Check if the signing config is already added
        if "signingConfigs {" in build_gradle_content or "signingConfigs {" in build_gradle_content:
            logger.info(
                "Signing configuration already exists in build.gradle. Skipping modification."
            )
            return True

        # Create the signing configuration block
        if is_kotlin_dsl:
            # For Kotlin DSL (build.gradle.kts)
            key_properties_code = """
    // Load key.properties file
    val keystorePropertiesFile = rootProject.file("key.properties")
    val keystoreProperties = java.util.Properties()
    keystoreProperties.load(java.io.FileInputStream(keystorePropertiesFile))
    
    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }
"""
            release_config = """
            signingConfig = signingConfigs.getByName("release")
"""
        else:
            # For Groovy DSL (build.gradle)
            key_properties_code = """
    // Load key.properties file
    def keystorePropertiesFile = rootProject.file("key.properties")
    def keystoreProperties = new Properties()
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
"""
            release_config = """
            signingConfig signingConfigs.release
"""

        # Insert the signing config in the android block
        if is_kotlin_dsl:
            # For Kotlin DSL, find the android { block
            android_block_pattern = r"android\s*\{"
            match = re.search(android_block_pattern, build_gradle_content)
            if match:
                insert_pos = match.end()
                # Insert after the android block opening
                modified_content = (
                    build_gradle_content[:insert_pos]
                    + key_properties_code
                    + build_gradle_content[insert_pos:]
                )
            else:
                error_msg = "Could not find android { block in build.gradle.kts"
                logger.error(error_msg)
                raise FlutLockError(error_msg)
        else:
            # For Groovy DSL
            android_block_pattern = r"android\s*\{"
            match = re.search(android_block_pattern, build_gradle_content)
            if match:
                insert_pos = match.end()
                # Insert after the android block opening
                modified_content = (
                    build_gradle_content[:insert_pos]
                    + key_properties_code
                    + build_gradle_content[insert_pos:]
                )
            else:
                error_msg = "Could not find android { block in build.gradle"
                logger.error(error_msg)
                raise FlutLockError(error_msg)

        # Update the release buildType to use the signing config
        if is_kotlin_dsl:
            # For Kotlin DSL find the release { block within buildTypes
            release_block_pattern = r"release\s*\{([^}]*)\}"
            match = re.search(release_block_pattern, modified_content)
            if match:
                release_block = match.group(1)
                # Replace signingConfig if it exists, otherwise add it
                if "signingConfig" in release_block:
                    modified_release = re.sub(
                        r"signingConfig\s*=\s*signingConfigs\.getByName\([\"']debug[\"']\)",
                        'signingConfig = signingConfigs.getByName("release")',
                        release_block,
                    )
                else:
                    modified_release = release_block + release_config

                modified_content = modified_content.replace(release_block, modified_release)
            else:
                logger.warning("Could not find release { block in build.gradle.kts")
        else:
            # For Groovy DSL find the release { block within buildTypes
            release_block_pattern = r"release\s*\{([^}]*)\}"
            match = re.search(release_block_pattern, modified_content)
            if match:
                release_block = match.group(1)
                # Replace signingConfig if it exists, otherwise add it
                if "signingConfig" in release_block:
                    modified_release = re.sub(
                        r"signingConfig\s+signingConfigs\.debug",
                        "signingConfig signingConfigs.release",
                        release_block,
                    )
                else:
                    modified_release = release_block + release_config

                modified_content = modified_content.replace(release_block, modified_release)
            else:
                logger.warning("Could not find release { block in build.gradle")

        # Backup the original file
        backup_path = build_gradle_path + ".bak"
        try:
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(build_gradle_content)
            logger.debug("Created backup of build.gradle at %s", backup_path)
        except (OSError, IOError) as e:
            logger.warning("Failed to create backup of build.gradle: %s", e)

        # Write the modified content back to the file
        try:
            with open(build_gradle_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            logger.info("Updated %s with signing configuration", build_gradle_path)
            return True
        except (OSError, IOError) as e:
            error_msg = f"Failed to write to build.gradle: {e}"
            logger.error(error_msg)
            # Try to restore from backup
            try:
                if os.path.exists(backup_path):
                    with open(build_gradle_path, "w", encoding="utf-8") as f:
                        f.write(build_gradle_content)
                    logger.info("Restored original build.gradle from backup")
            except (OSError, IOError) as restore_error:
                logger.error("Failed to restore build.gradle from backup: %s", restore_error)
            raise FlutLockError(error_msg) from e

    except FlutLockError:
        # Just re-raise FlutLockError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error updating build.gradle: {e}"
        logger.error(error_msg)
        raise FlutLockError(error_msg) from e
