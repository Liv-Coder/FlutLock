"""Signature verification functionality."""

import logging
import os
import shutil

from ..utils.commands import run_command
from ..utils.exceptions import SignatureError

logger = logging.getLogger("flutlock")


def verify_signature(output_file):
    """
    Verify the signature of the APK or AAB file.

    Args:
        output_file: Path to the output file to verify

    Returns:
        bool: True if verification was successful

    Raises:
        SignatureError: If verification fails
    """
    try:
        if not output_file or not os.path.exists(output_file):
            error_msg = f"Output file not found: {output_file}"
            logger.error(error_msg)
            raise SignatureError(error_msg)

        # Try apksigner first (preferred)
        if shutil.which("apksigner"):
            cmd = ["apksigner", "verify", "--verbose", output_file]
            success, output = run_command(cmd)

            if success and "verified" in output.lower():
                logger.info("Signature verification successful with apksigner")
                return True

            # Provide more detailed error information
            error_details = ""
            if "DOES NOT VERIFY" in output:
                error_details = (
                    "The APK signature is invalid. This could indicate "
                    "a problem with the keystore or signing process."
                )
            elif "failed to parse" in output.lower():
                error_details = (
                    "The file could not be parsed. It may be corrupted or "
                    "not a valid APK/AAB file."
                )

            if error_details:
                logger.error(error_details)
        else:
            logger.warning("apksigner not found, trying jarsigner instead")

            # Fall back to jarsigner
            if shutil.which("jarsigner"):
                cmd = ["jarsigner", "-verify", "-verbose", "-certs", output_file]
                success, output = run_command(cmd)

                if success and "jar verified" in output.lower():
                    logger.info("Signature verification successful with jarsigner")
                    return True
                elif success:
                    logger.warning(
                        "Signature verification with jarsigner returned: %s", output
                    )
                    error_msg = "Signature verification failed with jarsigner"
                    logger.error(error_msg)
                    raise SignatureError(error_msg)
            else:
                error_msg = "Neither apksigner nor jarsigner found for verification"
                logger.error(error_msg)
                logger.info(
                    "Install Android SDK Build Tools for apksigner or Java JDK for jarsigner"
                )
                raise SignatureError(error_msg)

        error_msg = f"Signature verification failed: {output}"
        logger.error(error_msg)
        raise SignatureError(error_msg)
    except SignatureError:
        # Just re-raise SignatureError exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during signature verification: {e}"
        logger.error(error_msg)
        raise SignatureError(error_msg) from e
