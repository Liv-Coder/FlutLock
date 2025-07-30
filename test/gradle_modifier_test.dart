/// Tests for Gradle Modifier functionality
///
/// This test suite validates the build.gradle file modification module,
/// including signing configuration injection, backup functionality, and error handling.

import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import 'package:flutlock/flutlock.dart';

void main() {
  group('GradleModifier', () {
    late Directory tempDir;
    late String testProjectPath;
    late String androidAppDir;

    setUp(() async {
      // Create temporary directory for test projects
      tempDir = await Directory.systemTemp.createTemp('flutlock_gradle_test_');
      testProjectPath = tempDir.path;
      androidAppDir = path.join(testProjectPath, 'android', 'app');

      // Create android/app directory structure
      await Directory(androidAppDir).create(recursive: true);
    });

    tearDown(() async {
      // Clean up temporary directory
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    group('GradleModificationConfig', () {
      test('should create config with default values', () {
        const config = GradleModificationConfig();

        expect(config.signingConfigName, equals('release'));
        expect(config.updateGradle, isTrue);
        expect(config.createBackup, isTrue);
        expect(config.keyPropertiesPath, isNull);
      });

      test('should create config with custom values', () {
        const config = GradleModificationConfig(
          signingConfigName: 'custom',
          updateGradle: false,
          createBackup: false,
          keyPropertiesPath: '/custom/path',
        );

        expect(config.signingConfigName, equals('custom'));
        expect(config.updateGradle, isFalse);
        expect(config.createBackup, isFalse);
        expect(config.keyPropertiesPath, equals('/custom/path'));
      });

      test('should create config from build configuration map', () {
        final buildConfig = {
          'signing_config_name': 'production',
          'update_gradle': false,
        };

        final config = GradleModificationConfig.fromBuildConfig(buildConfig);

        expect(config.signingConfigName, equals('production'));
        expect(config.updateGradle, isFalse);
        expect(config.createBackup, isTrue); // always true
      });

      test('should use defaults for missing build configuration values', () {
        final buildConfig = <String, dynamic>{};

        final config = GradleModificationConfig.fromBuildConfig(buildConfig);

        expect(config.signingConfigName, equals('release'));
        expect(config.updateGradle, isTrue);
        expect(config.createBackup, isTrue);
      });
    });

    group('Build gradle file detection', () {
      test('should find build.gradle file', () async {
        // Create build.gradle file
        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString('android { }');

        final foundPath =
            await GradleModifier.getBuildGradlePath(testProjectPath);
        expect(foundPath, equals(buildGradleFile.path));
      });

      test('should find build.gradle.kts file', () async {
        // Create build.gradle.kts file
        final buildGradleFile =
            File(path.join(androidAppDir, 'build.gradle.kts'));
        await buildGradleFile.writeAsString('android { }');

        final foundPath =
            await GradleModifier.getBuildGradlePath(testProjectPath);
        expect(foundPath, equals(buildGradleFile.path));
      });

      test('should prefer build.gradle over build.gradle.kts', () async {
        // Create both files
        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        final buildGradleKtsFile =
            File(path.join(androidAppDir, 'build.gradle.kts'));

        await buildGradleFile.writeAsString('android { }');
        await buildGradleKtsFile.writeAsString('android { }');

        final foundPath =
            await GradleModifier.getBuildGradlePath(testProjectPath);
        expect(foundPath, equals(buildGradleFile.path));
      });

      test('should return null when no build.gradle file exists', () async {
        final foundPath =
            await GradleModifier.getBuildGradlePath(testProjectPath);
        expect(foundPath, isNull);
      });

      test('should check if build.gradle exists', () async {
        // Initially should not exist
        expect(
            await GradleModifier.buildGradleExists(testProjectPath), isFalse);

        // Create the file
        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString('android { }');

        // Now should exist
        expect(await GradleModifier.buildGradleExists(testProjectPath), isTrue);
      });
    });

    group('Signing configuration detection', () {
      test('should detect existing signing configuration', () async {
        final buildGradleContent = '''
android {
    signingConfigs {
        release {
            keyAlias 'upload'
        }
    }
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(buildGradleContent);

        const config = GradleModificationConfig();
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);
        // Should not modify file if signing config already exists
        final content = await buildGradleFile.readAsString();
        expect(content, equals(buildGradleContent));
      });

      test('should validate signing configuration exists', () async {
        final buildGradleContent = '''
android {
    signingConfigs {
        release {
            keyAlias 'upload'
        }
    }
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(buildGradleContent);

        final hasSigningConfig =
            await GradleModifier.validateSigningConfiguration(testProjectPath);
        expect(hasSigningConfig, isTrue);
      });

      test('should detect missing signing configuration', () async {
        final buildGradleContent = '''
android {
    compileSdkVersion 33
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(buildGradleContent);

        final hasSigningConfig =
            await GradleModifier.validateSigningConfiguration(testProjectPath);
        expect(hasSigningConfig, isFalse);
      });
    });

    group('Gradle file modification', () {
      test('should add signing configuration to Groovy build.gradle', () async {
        final originalContent = '''
android {
    compileSdkVersion 33
    
    buildTypes {
        release {
            minifyEnabled false
        }
    }
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(originalContent);

        const config = GradleModificationConfig();
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);
        expect(result.wasBackedUp, isTrue);

        // Verify content was modified
        final modifiedContent = await buildGradleFile.readAsString();
        expect(modifiedContent, contains('keystoreProperties'));
        expect(modifiedContent, contains('signingConfigs'));
        expect(modifiedContent, contains('release {'));
        expect(modifiedContent, contains('keyAlias'));
        expect(modifiedContent, contains('storeFile'));
      });

      test('should handle Kotlin DSL build.gradle.kts', () async {
        final originalContent = '''
android {
    compileSdk = 33
    
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
}
''';

        final buildGradleFile =
            File(path.join(androidAppDir, 'build.gradle.kts'));
        await buildGradleFile.writeAsString(originalContent);

        const config =
            GradleModificationConfig(signingConfigName: 'production');
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);

        // Verify Kotlin DSL syntax was used
        final modifiedContent = await buildGradleFile.readAsString();
        expect(modifiedContent, contains('create("production")'));
        expect(modifiedContent, contains('keyAlias = keystoreProperties'));
      });

      test('should create backup file', () async {
        final originalContent = '''
android {
    compileSdkVersion 33
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(originalContent);

        const config = GradleModificationConfig();
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);
        expect(result.wasBackedUp, isTrue);
        expect(result.backupPath, isNotNull);

        // Verify backup file exists and contains original content
        final backupFile = File(result.backupPath!);
        expect(await backupFile.exists(), isTrue);

        final backupContent = await backupFile.readAsString();
        expect(backupContent, equals(originalContent));
      });

      test('should skip backup when disabled', () async {
        final originalContent = '''
android {
    compileSdkVersion 33
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(originalContent);

        const config = GradleModificationConfig(createBackup: false);
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);
        expect(result.wasBackedUp, isFalse);
        expect(result.backupPath, isNull);
      });

      test('should fail when android block is missing', () async {
        final buildGradleContent = '''
dependencies {
    implementation 'androidx.core:core:1.0.0'
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(buildGradleContent);

        const config = GradleModificationConfig();

        expect(
          () => GradleModifier.updateAppBuildGradle(testProjectPath, config),
          throwsA(isA<FlutLockException>()),
        );
      });

      test('should fail when build.gradle file does not exist', () async {
        const config = GradleModificationConfig();

        expect(
          () => GradleModifier.updateAppBuildGradle(testProjectPath, config),
          throwsA(isA<FlutLockException>()),
        );
      });
    });

    group('Release build type modification', () {
      test('should add signingConfig to existing release block', () async {
        final originalContent = '''
android {
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(originalContent);

        const config = GradleModificationConfig();
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);

        final modifiedContent = await buildGradleFile.readAsString();
        expect(
            modifiedContent, contains('signingConfig signingConfigs.release'));
      });

      test('should update existing signingConfig in release block', () async {
        final originalContent = '''
android {
    buildTypes {
        release {
            signingConfig signingConfigs.debug
            minifyEnabled false
        }
    }
}
''';

        final buildGradleFile = File(path.join(androidAppDir, 'build.gradle'));
        await buildGradleFile.writeAsString(originalContent);

        const config =
            GradleModificationConfig(signingConfigName: 'production');
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);

        final modifiedContent = await buildGradleFile.readAsString();
        expect(modifiedContent,
            contains('signingConfig signingConfigs.production'));
        expect(modifiedContent,
            isNot(contains('signingConfig signingConfigs.debug')));
      });

      test('should handle getByName pattern in Kotlin DSL', () async {
        final originalContent = '''
android {
    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }
}
''';

        final buildGradleFile =
            File(path.join(androidAppDir, 'build.gradle.kts'));
        await buildGradleFile.writeAsString(originalContent);

        const config = GradleModificationConfig();
        final result =
            await GradleModifier.updateAppBuildGradle(testProjectPath, config);

        expect(result.success, isTrue);

        final modifiedContent = await buildGradleFile.readAsString();
        expect(modifiedContent,
            contains('signingConfig = signingConfigs.getByName("release")'));
      });
    });
  });
}
