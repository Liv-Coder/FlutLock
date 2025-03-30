"""Tests for custom signing configuration name feature."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.flutter_signer.core.gradle import update_app_build_gradle
from src.flutter_signer.utils.exceptions import GradleError


class TestCustomSigningConfig(unittest.TestCase):
    """Test cases for custom signing configuration name feature."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory structure for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.flutter_project_path = self.temp_dir.name

        # Create android directory
        self.android_dir = os.path.join(self.flutter_project_path, "android")
        os.makedirs(self.android_dir, exist_ok=True)

        # Create app directory
        self.app_dir = os.path.join(self.android_dir, "app")
        os.makedirs(self.app_dir, exist_ok=True)

        # Create key.properties file
        self.key_props_file = os.path.join(self.android_dir, "key.properties")
        with open(self.key_props_file, "w", encoding="utf-8") as f:
            f.write("storePassword=test_password\n")
            f.write("keyPassword=test_password\n")
            f.write("keyAlias=upload\n")
            f.write("storeFile=../keystore.jks\n")

        # Sample Groovy build.gradle content
        self.groovy_build_gradle = """
plugins {
    id 'com.android.application'
}

android {
    compileSdkVersion 31
    
    defaultConfig {
        applicationId "com.example.flutterapp"
        minSdkVersion 21
        targetSdkVersion 31
        versionCode 1
        versionName "1.0.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.3.1'
    implementation 'com.google.android.material:material:1.4.0'
}
"""

        # Sample Kotlin build.gradle.kts content
        self.kotlin_build_gradle = """
plugins {
    id("com.android.application")
}

android {
    compileSdkVersion(31)
    
    defaultConfig {
        applicationId = "com.example.flutterapp"
        minSdkVersion(21)
        targetSdkVersion(31)
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.3.1")
    implementation("com.google.android.material:material:1.4.0")
}
"""

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_custom_signing_config_name_groovy(self):
        """Test custom signing configuration name with Groovy DSL."""
        # Create build.gradle file
        build_gradle_path = os.path.join(self.app_dir, "build.gradle")
        with open(build_gradle_path, "w", encoding="utf-8") as f:
            f.write(self.groovy_build_gradle)

        # Update with custom signing config name
        custom_name = "production"
        success = update_app_build_gradle(
            self.flutter_project_path, signing_config_name=custom_name
        )

        # Verify success
        self.assertTrue(success)

        # Read the modified file
        with open(build_gradle_path, "r", encoding="utf-8") as f:
            modified_content = f.read()

        # Check if custom name is used
        self.assertIn(f"signingConfigs {{\n        {custom_name} {{", modified_content)
        self.assertIn(f"signingConfig signingConfigs.{custom_name}", modified_content)

    def test_custom_signing_config_name_kotlin(self):
        """Test custom signing configuration name with Kotlin DSL."""
        # Create build.gradle.kts file
        build_gradle_path = os.path.join(self.app_dir, "build.gradle.kts")
        with open(build_gradle_path, "w", encoding="utf-8") as f:
            f.write(self.kotlin_build_gradle)

        # Update with custom signing config name
        custom_name = "staging"
        success = update_app_build_gradle(
            self.flutter_project_path, signing_config_name=custom_name
        )

        # Verify success
        self.assertTrue(success)

        # Read the modified file
        with open(build_gradle_path, "r", encoding="utf-8") as f:
            modified_content = f.read()

        # Check if custom name is used
        self.assertIn(f'create("{custom_name}") {{', modified_content)
        self.assertIn(
            f'signingConfig = signingConfigs.getByName("{custom_name}")', modified_content
        )

    def test_multiple_signing_configs(self):
        """Test using different custom signing config names sequentially."""
        # Create build.gradle file
        build_gradle_path = os.path.join(self.app_dir, "build.gradle")
        with open(build_gradle_path, "w", encoding="utf-8") as f:
            f.write(self.groovy_build_gradle)

        # First update with staging config
        success1 = update_app_build_gradle(self.flutter_project_path, signing_config_name="staging")
        self.assertTrue(success1)

        # Create a new temporary project for the second config
        second_temp_dir = tempfile.TemporaryDirectory()
        second_project_path = second_temp_dir.name

        # Set up necessary directories and files
        second_android_dir = os.path.join(second_project_path, "android")
        os.makedirs(second_android_dir, exist_ok=True)

        second_app_dir = os.path.join(second_android_dir, "app")
        os.makedirs(second_app_dir, exist_ok=True)

        # Create key.properties
        second_key_props_file = os.path.join(second_android_dir, "key.properties")
        with open(second_key_props_file, "w", encoding="utf-8") as f:
            f.write("storePassword=test_password\n")
            f.write("keyPassword=test_password\n")
            f.write("keyAlias=upload\n")
            f.write("storeFile=../keystore.jks\n")

        # Create build.gradle for second project
        second_build_gradle_path = os.path.join(second_app_dir, "build.gradle")
        with open(second_build_gradle_path, "w", encoding="utf-8") as f:
            f.write(self.groovy_build_gradle)

        # Second update with production config
        success2 = update_app_build_gradle(second_project_path, signing_config_name="production")
        self.assertTrue(success2)

        # Read both modified files
        with open(build_gradle_path, "r", encoding="utf-8") as f:
            first_content = f.read()

        with open(second_build_gradle_path, "r", encoding="utf-8") as f:
            second_content = f.read()

        # Verify each has the correct config name
        self.assertIn("signingConfigs {\n        staging {", first_content)
        self.assertIn("signingConfigs {\n        production {", second_content)

        # Clean up
        second_temp_dir.cleanup()

    @patch("src.flutter_signer.core.gradle.logger")
    def test_error_handling(self, mock_logger):
        """Test error handling with invalid project structure."""
        # Remove android/app directory to cause an error
        os.rmdir(self.app_dir)

        # Should raise GradleError
        with self.assertRaises(GradleError):
            update_app_build_gradle(self.flutter_project_path, signing_config_name="debug")

        # Verify appropriate error logging
        mock_logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
