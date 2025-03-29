# FlutLock Examples

This directory contains example scripts and configuration files to help you get started with FlutLock.

## Example Scripts

### sign_flutter_app_example.py

A simplified example showing how to use the FlutLock library to sign a Flutter Android app.

```python
from flutter_signer import FlutterSigner

# Initialize the signer
signer = FlutterSigner(
    keystore_path="path/to/keystore.jks",
    keystore_password="your_keystore_password",
    key_alias="your_key_alias",
    key_password="your_key_password",
    android_app_path="path/to/your/android/app"
)

# Sign the app
result = signer.sign()
print(f"App signed successfully: {result.success}")
if result.success:
    print(f"Signed APK location: {result.signed_apk_path}")
else:
    print(f"Error: {result.error_message}")
```

### sign_flutter_app.py

This is the legacy script from previous versions of FlutLock. It is included for backward compatibility and reference.
We recommend using the new `flutlock` command-line tool or importing the library as shown in the `sign_flutter_app_example.py`
for new projects.

```
flutlock sign --keystore path/to/keystore.jks --app path/to/android/app
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

### legacy_sign_flutter_app.py

This script provides backward compatibility with older versions of FlutLock. It imports the
new package structure while maintaining the original interface.

## Using the Examples

1. Copy the example script you want to use to your project directory
2. Modify the parameters as needed
3. Run the script:

```
python sign_flutter_app_example.py
```

Or use the new command-line tool:

```
flutlock sign --config=my_config.yaml
```

## Configuration Examples

The `../config/` directory contains sample configuration files that work with these examples.

For more detailed documentation, please refer to the [official documentation](../docs/).

## Getting Help

If you encounter any issues or have questions about these examples, please:

1. Check the troubleshooting section in the documentation
2. Open an issue on GitHub
3. Reach out to the community for support
