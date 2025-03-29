@echo off
REM Example batch file for using FlutLock with an existing keystore on Windows
REM This demonstrates using a pre-existing keystore file

REM Set environment variables for keystore information
SET KEYSTORE_PASSWORD=your-secure-password
SET KEY_PASSWORD=your-secure-key-password
SET STORE_ALIAS=upload

REM Navigate to your Flutter project
REM cd C:\path\to\your\flutter\project

REM Run FlutLock with an existing keystore
python sign_flutter_app.py ^
  --path C:\path\to\your\flutter\project ^
  --keystore C:\path\to\your\existing.keystore ^
  --alias upload ^
  --build-type apk ^
  --verify

REM The script will use the existing keystore and create the key.properties file
REM It will then build the APK and verify the signature

echo FlutLock completed! 