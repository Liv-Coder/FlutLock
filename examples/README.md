# FlutLock Examples

This directory contains example scripts and configuration files to help you get started with FlutLock.

## Example Scripts

### sign_flutter_app.py

This is a backward compatibility script that forwards to the new package-based structure. It's designed for users who are used to running the original script directly.

```
python examples/sign_flutter_app.py --path ./project --build-type apk
```

### ci_cd_example.py

This example demonstrates how to use FlutLock in continuous integration/continuous deployment (CI/CD) environments
using non-interactive mode with environment variables. It shows how to:

- Set up environment variables for secure password handling
- Use command-line arguments to configure the signing process
- Run the tool in non-interactive mode suitable for automated builds

```python
# Set up environment variables for security
os.environ["KEYSTORE_PASSWORD"] = "ci_password"
os.environ["KEY_PASSWORD"] = "ci_password"

# Run with non-interactive arguments
args = [
    "--non-interactive",
    "--path", "./flutter_project",
    "--keystore-path", "./keystore/ci_keystore.jks",
    "--build-type", "aab",
    "--verify"
]
```

### config_file_example.py

This example shows how to use FlutLock with a JSON configuration file, which is useful for
projects with multiple build configurations or when you need to share configuration with team members.
The script demonstrates:

- Creating a JSON configuration file with keystore and signer information
- Running FlutLock with the configuration file
- Handling cleanup of temporary files

```python
# Example configuration
config = {
    "keystore": {
        "path": "./keystore/my_keystore.jks",
        "alias": "upload",
        "store_password": "store_password_here",
        "key_password": "key_password_here",
        "use_existing": False
    },
    "signer": {
        "name": "John Doe",
        "org_unit": "Development",
        "organization": "Example Company",
        "locality": "San Francisco",
        "state": "California",
        "country": "US"
    },
    "build": {
        "type": "apk",
        "verify": True,
    }
}
```

### optimized_config_example.py

This example demonstrates the enhanced configuration processing capabilities with variable substitution:

- Using environment variables in configuration with ${VAR_NAME} syntax
- Setting default values with ${VAR_NAME:-default} syntax
- Using special variables like ${PROJECT_DIR} for path handling
- Environment-specific configuration (dev/staging/prod)

### custom_signing_config_example.py

This example demonstrates how to use custom signing configuration names, which is useful for:

- Multiple flavor configurations in a single app
- Custom build variants
- Different signing configurations for debug/staging/production

```bash
python custom_signing_config_example.py --path=/path/to/flutter/project --signing-config-name=staging
```

The script shows how to:

- Create a configuration with variable substitution
- Specify a custom name for the signing configuration in build.gradle
- Pass command-line arguments through to the FlutLock tool
- Handle temporary files and cleanup

## Using the Examples

1. Copy the example script you want to use to your project directory
2. Modify the parameters as needed
3. Run the script:

```
python ci_cd_example.py
```

Or use the command-line tool directly:

```
flutlock --config=my_config.json
```

## Configuration Examples

The `../config/` directory contains sample configuration files that work with these examples.

For more detailed documentation, please refer to the [official documentation](../docs/).

## Getting Help

If you encounter any issues or have questions about these examples, please:

1. Check the troubleshooting section in the documentation
2. Open an issue on GitHub
3. Reach out to the community for support
