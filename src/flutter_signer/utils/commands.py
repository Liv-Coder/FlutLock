"""Command execution utilities."""

import logging
import subprocess

logger = logging.getLogger("flutlock")


def run_command(cmd, **kwargs):
    """Run a shell command and return the output.

    Args:
        cmd: Command to execute as a list of strings
        **kwargs: Additional keyword arguments for subprocess.run

    Returns:
        Tuple of (success, output/error_message)
    """
    try:
        logger.debug("Running command: %s", " ".join(cmd))
        # For security, mask password arguments in the log
        log_cmd = []
        skip_next = False
        for arg in cmd:
            if skip_next:
                log_cmd.append("***")
                skip_next = False
            elif arg in ["-storepass", "-keypass"]:
                log_cmd.append(arg)
                skip_next = True
            else:
                log_cmd.append(arg)
        logger.debug("Command (masked): %s", " ".join(log_cmd))

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            **kwargs,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            # Split long line for better readability
            logger.error(
                "Command failed with code %d: %s",
                result.returncode,
                error_msg,
            )

            # Improve error details for common issues
            if "keytool" in cmd[0] and "password was incorrect" in error_msg:
                error_msg = (
                    "Keystore password was incorrect. "
                    "Please check your password and try again."
                )
            elif (
                "flutter" in cmd[0]
                and "Target file" in error_msg
                and "not found" in error_msg
            ):
                error_msg = (
                    "Flutter build failed: Missing target files. "
                    "Ensure your Flutter project is properly configured."
                )

            logger.debug("Command output: %s", result.stdout.strip())
            return False, error_msg

        return True, result.stdout.strip()
    except subprocess.SubprocessError as e:
        logger.error("Error executing command: %s", e)
        return False, str(e)
    except (OSError, IOError) as e:
        logger.error("IO error executing command: %s", e)
        return False, str(e)
