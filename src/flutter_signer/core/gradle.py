"""build.gradle.kts file modification functionality."""

import logging
import os
import re
from pathlib import Path
from ..utils.exceptions import GradleError, FlutLockError

logger = logging.getLogger("flutlock")


def update_app_build_gradle(flutter_project_path, config=None, signing_config_name="release"):
    """
    Update the app-level build.gradle.kts file to include signing configuration.

    Args:
        flutter_project_path: Path to the Flutter project
        config: Configuration dictionary (default: None)
        signing_config_name: Name for the signing configuration (default: "release")

    Returns:
        bool: True if build.gradle.kts modification was successful

    Raises:
        GradleError: If build.gradle.kts modification fails
    """
    try:
        android_dir = os.path.join(flutter_project_path, "android")
        app_dir = os.path.join(android_dir, "app")

        if not os.path.isdir(app_dir):
            error_msg = f"App directory not found in {android_dir}"
            logger.error(error_msg)
            logger.info("Make sure this is a valid Flutter project with an android/app directory")
            raise GradleError(
                message=error_msg,
                details="The android/app directory structure is required for Flutter Android projects.",
                file_path=app_dir,
            )

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
            raise GradleError(
                message=error_msg,
                details="A valid build.gradle or build.gradle.kts file is required for Android Gradle projects.",
                file_path=app_dir,
            )

        # Read the build.gradle file content
        try:
            with open(build_gradle_path, "r", encoding="utf-8") as f:
                build_gradle_content = f.read()
        except (OSError, IOError) as e:
            error_msg = f"Could not read {build_gradle_path}"
            logger.error(error_msg)
            raise GradleError(message=error_msg, details=str(e), file_path=build_gradle_path)

        # Check if the signing config is already added
        if "signingConfigs {" in build_gradle_content or "signingConfigs {" in build_gradle_content:
            logger.info(
                "Signing configuration already exists in build.gradle. Skipping modification."
            )
            return True

        # Create the signing configuration block
        if is_kotlin_dsl:
            # For .kts files, we need to determine if they're using Kotlin DSL or Groovy syntax
            # Since some Flutter projects use Groovy syntax even in .kts files

            # Better detection of hybrid syntax vs pure Kotlin DSL
            # Rather than assuming all .kts files with some Groovy patterns are hybrid,
            # look for specific Kotlin patterns first

            # Check for Kotlin DSL markers - these would indicate pure Kotlin DSL
            kotlin_patterns = [
                "val ",  # Variable declarations
                "import kotlin.",  # Kotlin imports
                "= listOf",  # Kotlin collection initialization
                ": String",  # Type declarations
                "buildTypes {",  # Kotlin-style blocks
                "plugins {",  # Modern plugins block
                "android {",  # Android block in Kotlin style
                "implementation(platform",  # Kotlin dependency notation
            ]

            is_pure_kotlin = any(pattern in build_gradle_content for pattern in kotlin_patterns)

            # If it's a .kts file and we've found Kotlin patterns, use pure Kotlin DSL
            # Otherwise, assume it's a hybrid file using Groovy syntax
            if is_pure_kotlin:
                # For pure Kotlin DSL (build.gradle.kts) - modern implementation with better error handling
                key_properties_code = f"""
    // Load key.properties file
    import java.util.Properties
    import java.io.FileInputStream

    // Function to safely load properties
    fun loadProperties(file: java.io.File): Properties {{
        val properties = Properties()
        if (file.isFile) {{ // Check if it's a file and exists
            try {{
                FileInputStream(file).use {{ fis ->
                    properties.load(fis)
                }}
            }} catch (e: Exception) {{
                // Log the exception or handle it as needed
                logger.warn("Could not load properties file ${{file.name}}: ${{e.message}}")
            }}
        }} else {{
            logger.warn("Properties file not found: ${{file.absolutePath}}")
        }}
        return properties
    }}

    // Load keystore properties
    val keystorePropertiesFile = rootProject.file("key.properties")
    val keystoreProperties = loadProperties(keystorePropertiesFile)

    // Define signing configurations
    signingConfigs {{
        // Creates a signing configuration named '{signing_config_name}'
        create("{signing_config_name}") {{
            // Use getProperty which returns null if key doesn't exist
            val storeFilePath = keystoreProperties.getProperty("storeFile")
            val storePass = keystoreProperties.getProperty("storePassword")
            val alias = keystoreProperties.getProperty("keyAlias")
            val keyPass = keystoreProperties.getProperty("keyPassword")

            // Only configure if all properties were found
            if (storeFilePath != null && storePass != null && alias != null && keyPass != null) {{
                // Use project.file to resolve the path relative to the project
                storeFile = project.file(storeFilePath)
                storePassword = storePass
                keyAlias = alias
                keyPassword = keyPass
            }} else {{
                logger.warn("Release signing configuration in build.gradle.kts is missing details from key.properties. Release builds may fail or use debug signing.")
            }}
        }}
    }}
"""
                # Updated release config with null checking for extra safety
                release_config = f"""
            // Apply the '{signing_config_name}' signing configuration defined above
            // Make sure 'signingConfigs.{signing_config_name}' actually exists and is configured
            if (signingConfigs.findByName("{signing_config_name}")?.storeFile != null) {{
                signingConfig = signingConfigs.getByName("{signing_config_name}")
            }} else {{
                logger.warn("Signing config '{signing_config_name}' not fully configured (check key.properties). Release build may use debug signing.")
                // Fallback to debug signing explicitly if desired/needed
                // signingConfig = signingConfigs.getByName("debug")
            }}
"""
            else:
                # For hybrid Kotlin DSL (build.gradle.kts with Groovy syntax)
                key_properties_code = f"""
    // Load key.properties file
    def keystoreProperties = new Properties()
    def keystorePropertiesFile = rootProject.file('key.properties')
    if (keystorePropertiesFile.exists()) {{
        keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    }}
    
    signingConfigs {{
        {signing_config_name} {{
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }}
    }}
"""
                release_config = f"""
            signingConfig signingConfigs.{signing_config_name}
"""
        else:
            # For Groovy DSL (build.gradle)
            key_properties_code = f"""
    // Load key.properties file
    def keystoreProperties = new Properties()
    def keystorePropertiesFile = rootProject.file('key.properties')
    if (keystorePropertiesFile.exists()) {{
        keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    }}
    
    signingConfigs {{
        {signing_config_name} {{
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }}
    }}
"""
            release_config = f"""
            signingConfig signingConfigs.{signing_config_name}
"""

        # Insert the signing config in the android block
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
            error_msg = f"Could not find android {{ block in {build_gradle_path}"
            logger.error(error_msg)
            raise GradleError(
                message=error_msg,
                details="The android { } block is required in the build.gradle file.",
                file_path=build_gradle_path,
            )

        # Update the release buildType to use the signing config
        release_block_pattern = r"release\s*\{([^}]*)\}"
        match = re.search(release_block_pattern, modified_content)
        if match:
            release_block = match.group(1)

            # Check if signingConfig is already in the release block
            if "signingConfig" in release_block:
                # There might be multiple signingConfig lines, handle both cases
                if is_kotlin_dsl and is_pure_kotlin:
                    # For pure Kotlin DSL
                    modified_release = re.sub(
                        r"signingConfig\s*=\s*signingConfigs\.getByName\([\"']debug[\"']\)",
                        f'signingConfig = signingConfigs.getByName("{signing_config_name}")',
                        release_block,
                    )
                else:
                    # For Groovy or hybrid Kotlin DSL
                    modified_release = re.sub(
                        r"signingConfig\s+signingConfigs\.debug",
                        f"signingConfig signingConfigs.{signing_config_name}",
                        release_block,
                    )

                # If there are comments suggesting to add signing config, remove them
                modified_release = re.sub(r"//\s*TODO:.*signing config.*\n", "", modified_release)
            else:
                # If no signingConfig line exists, add it
                modified_release = release_block + release_config

            modified_content = modified_content.replace(release_block, modified_release)
        else:
            # Handle the getByName pattern commonly used in modern Kotlin DSL
            release_block_pattern = r"getByName\s*\(\s*[\"']release[\"']\s*\)\s*\{([^}]*)\}"
            match = re.search(release_block_pattern, modified_content)

            if match:
                release_block = match.group(1)

                # Check if signingConfig is already in the release block
                if "signingConfig" in release_block:
                    if is_kotlin_dsl and is_pure_kotlin:
                        # For pure Kotlin DSL with getByName pattern
                        modified_release = re.sub(
                            r"signingConfig\s*=\s*signingConfigs\.getByName\([\"']debug[\"']\)",
                            f'signingConfig = signingConfigs.getByName("{signing_config_name}")',
                            release_block,
                        )
                    else:
                        # For Groovy or hybrid Kotlin DSL
                        modified_release = re.sub(
                            r"signingConfig\s+signingConfigs\.debug",
                            f"signingConfig signingConfigs.{signing_config_name}",
                            release_block,
                        )

                    # Remove TODO comments
                    modified_release = re.sub(
                        r"//\s*TODO:.*signing config.*\n", "", modified_release
                    )
                else:
                    # If no signingConfig line exists, add it
                    modified_release = release_block + release_config

                modified_content = modified_content.replace(release_block, modified_release)
            else:
                logger.warning(f"Could not find release {{ block in {build_gradle_path}")
                logger.info(
                    f"Created signing config but couldn't automatically apply it to release build type"
                )

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
            logger.info(
                "Updated %s with %s signing configuration", build_gradle_path, signing_config_name
            )
            return True
        except (OSError, IOError) as e:
            error_msg = f"Failed to write to {build_gradle_path}"
            logger.error(error_msg)
            raise GradleError(message=error_msg, details=str(e), file_path=build_gradle_path)

    except FlutLockError:
        # Re-raise any existing FlutLockError
        raise
    except Exception as e:
        error_msg = "Unexpected error during build.gradle modification"
        logger.error(error_msg)
        if hasattr(e, "__str__"):
            logger.error("Error details: %s", str(e))
        raise GradleError(
            message=error_msg,
            details=str(e) if hasattr(e, "__str__") else None,
            file_path=build_gradle_path if "build_gradle_path" in locals() else None,
        )
