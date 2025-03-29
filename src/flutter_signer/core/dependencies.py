"""Dependency checking functionality for FlutLock."""

import logging
import shutil

from ..utils.exceptions import DependencyError

logger = logging.getLogger("flutlock")


def check_dependencies():
    """
    Check if required external dependencies are installed.

    Returns:
        bool: True if all dependencies are present

    Raises:
        DependencyError: If any dependencies are missing
    """
    dependencies = {
        "flutter": "Flutter SDK",
        "keytool": "Java Development Kit",
        "apksigner": "Android SDK Build Tools",
    }

    missing = []
    for cmd, name in dependencies.items():
        if not shutil.which(cmd):
            missing.append(f"{name} ({cmd})")

    if missing:
        missing_str = ", ".join(missing)
        logger.error("Missing dependencies: %s", missing_str)
        logger.info(
            "Please install the missing dependencies and ensure they are in your PATH."
        )

        # Provide more specific guidance for each missing dependency
        for item in missing:
            if "Flutter SDK" in item:
                logger.info(
                    "Flutter installation guide: https://flutter.dev/docs/get-started/install"
                )
            elif "Java Development Kit" in item:
                logger.info("JDK installation guide: https://openjdk.java.net/install/")
            elif "Android SDK" in item:
                logger.info(
                    "Android SDK installation: https://developer.android.com/studio"
                )

        raise DependencyError(f"Missing dependencies: {missing_str}")

    return True
