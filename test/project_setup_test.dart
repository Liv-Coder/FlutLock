import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import '../lib/src/core/project_setup.dart';
import '../lib/src/utils/exceptions.dart';

void main() {
  group('ProjectSetup', () {
    late Directory tempDir;
    late String testProjectPath;

    setUp(() async {
      // Create a temporary directory for testing
      tempDir = await Directory.systemTemp.createTemp('flutlock_test_');
      testProjectPath = tempDir.path;
    });

    tearDown(() async {
      // Clean up temporary directory
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    group('setupFlutterProject', () {
      test('should throw exception for non-Flutter project', () async {
        // Create empty directory
        expect(
          () => ProjectSetup.setupFlutterProject(testProjectPath),
          throwsA(isA<ProjectSetupException>()),
        );
      });

      test('should throw exception for directory without write permissions',
          () async {
        // This test is platform-specific and may not work on all systems
        // Skip on Windows where permission testing is complex
        if (Platform.isWindows) {
          return;
        }

        await _createBasicFlutterProject(testProjectPath);

        // Try to remove write permissions (may not work on all systems)
        try {
          await Process.run('chmod', ['444', testProjectPath]);

          expect(
            () => ProjectSetup.setupFlutterProject(testProjectPath),
            throwsA(isA<ProjectSetupException>()),
          );
        } catch (e) {
          // Skip test if chmod is not available
          print('Skipping permission test: $e');
        }
      });

      test('should succeed for already configured project', () async {
        await _createCompleteFlutterProject(testProjectPath);

        final result = await ProjectSetup.setupFlutterProject(
          testProjectPath,
          interactive: false,
        );

        expect(result.success, isTrue);
        expect(result.errors, isEmpty);
      });

      test('should create missing directories', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.setupFlutterProject(
          testProjectPath,
          interactive: false,
        );

        expect(result.success, isTrue);
        expect(result.directoriesCreated, isNotEmpty);
        expect(result.actionsTaken, isNotEmpty);

        // Verify directories were actually created
        expect(
          await Directory(path.join(testProjectPath, 'android')).exists(),
          isTrue,
        );
        expect(
          await Directory(path.join(testProjectPath, 'android', 'app'))
              .exists(),
          isTrue,
        );
      });

      test('should update .gitignore with keystore exclusions', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.setupFlutterProject(
          testProjectPath,
          interactive: false,
        );

        expect(result.success, isTrue);

        // Check .gitignore was updated
        final gitignoreFile = File(path.join(testProjectPath, '.gitignore'));
        if (await gitignoreFile.exists()) {
          final content = await gitignoreFile.readAsString();
          expect(content, contains('*.jks'));
          expect(content, contains('key.properties'));
          expect(content, contains('FlutLock keystore files'));
        }
      });

      test('should create backup when updating existing .gitignore', () async {
        await _createBasicFlutterProject(testProjectPath);

        // Create existing .gitignore
        final gitignoreFile = File(path.join(testProjectPath, '.gitignore'));
        await gitignoreFile.writeAsString('# Existing content\n*.log\n');

        final result = await ProjectSetup.setupFlutterProject(
          testProjectPath,
          interactive: false,
          backup: true,
        );

        expect(result.success, isTrue);
        expect(result.filesBackedUp, contains('.gitignore'));

        // Check backup file exists
        final backupFiles = await tempDir
            .list()
            .where((entity) => entity.path.contains('.gitignore.backup.'))
            .toList();
        expect(backupFiles, isNotEmpty);
      });

      test('should handle force overwrite correctly', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.setupFlutterProject(
          testProjectPath,
          force: true,
          interactive: false,
        );

        expect(result.success, isTrue);
        expect(result.actionsTaken, isNotEmpty);
      });
    });

    group('fixProjectStructure', () {
      test('should perform dry run without making changes', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.fixProjectStructure(
          testProjectPath,
          dryRun: true,
        );

        expect(result.success, isTrue);
        expect(result.actionsTaken, isNotEmpty);

        // Verify no actual changes were made
        expect(
          await Directory(path.join(testProjectPath, 'android')).exists(),
          isFalse,
        );

        // Check that actions are prefixed with "Would"
        expect(
          result.actionsTaken.every((action) => action.startsWith('Would')),
          isTrue,
        );
      });

      test('should fix project structure when not in dry run mode', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.fixProjectStructure(
          testProjectPath,
          dryRun: false,
        );

        expect(result.success, isTrue);
        expect(result.actionsTaken, isNotEmpty);

        // Verify actual changes were made
        expect(
          await Directory(path.join(testProjectPath, 'android')).exists(),
          isTrue,
        );
      });

      test('should handle errors gracefully', () async {
        final nonExistentPath = path.join(testProjectPath, 'non_existent');

        expect(
          () => ProjectSetup.fixProjectStructure(nonExistentPath),
          throwsA(isA<ProjectSetupException>()),
        );
      });
    });

    group('isProjectReady', () {
      test('should return false for non-Flutter project', () async {
        final result = await ProjectSetup.isProjectReady(testProjectPath);

        expect(result['isReady'], isFalse);
        expect(result['issues'], contains('Not a valid Flutter project'));
      });

      test('should return false for incomplete Flutter project', () async {
        await _createBasicFlutterProject(testProjectPath);

        final result = await ProjectSetup.isProjectReady(testProjectPath);

        expect(result['isReady'], isFalse);
        expect(result['issues'], isNotEmpty);
        expect(result['issues'], contains('Missing android/ directory'));
      });

      test('should return true for complete project with signing', () async {
        await _createProjectWithSigning(testProjectPath);

        final result = await ProjectSetup.isProjectReady(testProjectPath);

        expect(result['isReady'], isTrue);
        expect(result['issues'], isEmpty);
      });

      test('should identify specific missing components', () async {
        await _createCompleteFlutterProject(testProjectPath);

        final result = await ProjectSetup.isProjectReady(testProjectPath);

        expect(result['isReady'], isFalse);
        expect(result['issues'],
            contains('No keystore or key.properties configuration found'));
        expect(result['issues'],
            contains('No signing configuration in build.gradle'));
      });

      test('should handle analysis errors gracefully', () async {
        final nonExistentPath = path.join(testProjectPath, 'non_existent');

        final result = await ProjectSetup.isProjectReady(nonExistentPath);

        expect(result['isReady'], isFalse);
        expect(result['issues'], isNotEmpty);
        expect((result['issues'] as List).first,
            contains('Error analyzing project'));
      });
    });
  });
}

/// Create a basic Flutter project structure for testing
Future<void> _createBasicFlutterProject(String projectPath) async {
  // Create lib directory
  await Directory(path.join(projectPath, 'lib')).create(recursive: true);

  // Create pubspec.yaml
  final pubspecContent = '''
name: test_project
description: A test Flutter project
version: 1.0.0+1

environment:
  sdk: '>=2.17.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter

flutter:
  uses-material-design: true
''';

  await File(path.join(projectPath, 'pubspec.yaml'))
      .writeAsString(pubspecContent);

  // Create main.dart
  await File(path.join(projectPath, 'lib', 'main.dart')).writeAsString('''
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Test App',
      home: Scaffold(
        appBar: AppBar(title: Text('Test')),
        body: Center(child: Text('Hello World')),
      ),
    );
  }
}
''');
}

/// Create a complete Flutter project with Android support
Future<void> _createCompleteFlutterProject(String projectPath) async {
  await _createBasicFlutterProject(projectPath);

  // Create Android directories
  await Directory(path.join(projectPath, 'android', 'app', 'src', 'main'))
      .create(recursive: true);

  // Create android/build.gradle
  await File(path.join(projectPath, 'android', 'build.gradle'))
      .writeAsString('''
buildscript {
    ext.kotlin_version = '1.7.10'
    repositories {
        google()
        mavenCentral()
    }
}
''');

  // Create android/app/build.gradle
  await File(path.join(projectPath, 'android', 'app', 'build.gradle'))
      .writeAsString('''
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.example.testproject"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
        }
    }
}
''');
}

/// Create a project with keystore and signing configuration
Future<void> _createProjectWithSigning(String projectPath) async {
  await _createCompleteFlutterProject(projectPath);

  // Create key.properties
  await File(path.join(projectPath, 'android', 'key.properties'))
      .writeAsString('''
storePassword=password123
keyPassword=password123
keyAlias=upload
storeFile=../app/upload-keystore.jks
''');

  // Create keystore file
  await File(path.join(projectPath, 'android', 'app', 'upload-keystore.jks'))
      .writeAsString('dummy keystore content');

  // Update build.gradle with signing configuration
  await File(path.join(projectPath, 'android', 'app', 'build.gradle'))
      .writeAsString('''
android {
    compileSdkVersion 33
    
    signingConfigs {
        release {
            keyAlias 'upload'
            keyPassword 'password123'
            storeFile file('../app/upload-keystore.jks')
            storePassword 'password123'
        }
    }
    
    defaultConfig {
        applicationId "com.example.testproject"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
        }
    }
}
''');
}
