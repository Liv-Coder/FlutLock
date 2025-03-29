# Configuration Files

This directory contains example configuration files for FlutLock.

## flutlock_config_sample.json

This is a sample configuration file that demonstrates all available options for FlutLock. You can use this as a template for creating your own configuration files.

## test_config.json

This configuration file is used for automated testing and contains minimal test settings.

## Creating Your Own Configuration

Copy `flutlock_config_sample.json` to a new file (e.g., `my_config.json`) and modify it according to your needs. Then use it with:

```bash
python -m flutter_signer --config path/to/my_config.json
```

## Configuration File Structure

```json
{
  "keystore": {
    "use_existing": false,
    "path": "path/to/your/keystore.jks",
    "alias": "upload",
    "store_password": "your_keystore_password",
    "key_password": "your_key_password"
  },
  "signer": {
    "name": "Your Name",
    "org_unit": "Development",
    "organization": "Your Company",
    "locality": "Your City",
    "state": "Your State",
    "country": "US"
  },
  "build": {
    "type": "apk",
    "verify": true
  }
}
```

## Security Note

Configuration files containing passwords should be kept secure and not committed to version control. Consider using environment variables for sensitive information instead.
