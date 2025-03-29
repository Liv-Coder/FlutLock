"""Flutter build functionality."""

import logging
import os

from ..utils.commands import run_command
from ..utils.exceptions import BuildError

logger = logging.getLogger("flutlock")


def build_flutter_app(flutter_project_path, build_type="apk"):
    """
    Build the Flutter app with the specified build type.

    Args:
        flutter_project_path: Path to the Flutter project
        build_type: Build type, either 'apk' or 'aab' (default: 'apk')

    Returns:
        str: Path to the output file

    Raises:
        BuildError: If build fails
    """
    try:
        cmd = ["flutter", "build", build_type, "--release"]

        logger.info("Building Flutter %s in release mode", build_type)
        success, output = run_command(cmd, cwd=flutter_project_path)

        if not success:
            error_msg = f"Flutter build failed: {output}"
            logger.error(error_msg)

            # Add specific troubleshooting advice for common error patterns
            if "key.properties" in output and "not found" in output:
                logger.info(
                    "Troubleshooting: Make sure key.properties file is in the android/ directory"
                )
            elif "keystore" in output and "does not exist" in output:
                logger.info(
                    "Troubleshooting: The keystore file path specified in key.properties is incorrect"
                )
            elif "Gradle" in output and "failed" in output:
                logger.info(
                    "Troubleshooting: Check your Flutter project's Gradle configuration"
                )

            raise BuildError(error_msg)

        # Determine the output file path based on build type
        if build_type == "apk":
            # For APK, the output is usually in build/app/outputs/flutter-apk/
            output_dir = os.path.join(
                flutter_project_path, "build", "app", "outputs", "flutter-apk"
            )
            output_pattern = os.path.join(output_dir, "app-release.apk")
        else:  # appbundle
            # For App Bundle, the output is in build/app/outputs/bundle/release/
            output_dir = os.path.join(
                flutter_project_path, "build", "app", "outputs", "bundle", "release"
            )
            output_pattern = os.path.join(output_dir, "app-release.aab")

        # Check if the output file exists
        if os.path.exists(output_pattern):
            logger.info("Build completed: %s", output_pattern)
            return output_pattern
        else:
            # Look for similarly named files if the expected file isn't found
            try:
                similar_files = []
                for file in os.listdir(output_dir):
                    if file.endswith(".apk" if build_type == "apk" else ".aab"):
                        similar_files.append(os.path.join(output_dir, file))

                if similar_files:
                    logger.warning(
                        "Expected output file not found at %s", output_pattern
                    )
                    logger.info("Found similar files: %s", ", ".join(similar_files))
                    # Use the first similar file
                    return similar_files[0]
            except (FileNotFoundError, NotADirectoryError):
                pass

            error_msg = (
                f"Build output file not found at expected location: {output_pattern}"
            )
            logger.error(error_msg)
            raise BuildError(error_msg)
    except BuildError:
        # Just re-raise BuildError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during build: {e}"
        logger.error(error_msg)
        raise BuildError(error_msg) from e
