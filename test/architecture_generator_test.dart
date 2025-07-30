import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;

import '../lib/src/core/architecture_generator.dart';
import '../lib/src/core/architecture_definition.dart';

void main() {
  group('ArchitectureGenerator', () {
    late String testProjectPath;

    setUp(() async {
      // Create temporary test directory
      final tempDir =
          await Directory.systemTemp.createTemp('flutlock_arch_test_');
      testProjectPath = tempDir.path;

      // Create basic Flutter project structure
      await _createBasicFlutterProject(testProjectPath);
    });

    tearDown(() async {
      // Clean up test directory
      final testDir = Directory(testProjectPath);
      if (await testDir.exists()) {
        await testDir.delete(recursive: true);
      }
    });

    group('generateArchitecture', () {
      test('should generate flat architecture successfully', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          force: true,
        );

        expect(result.success, isTrue);
        expect(result.architecture, equals('flat'));
        expect(result.foldersCreated, isNotEmpty);
        expect(result.filesCreated, isNotEmpty);
        expect(result.errors, isEmpty);

        // Verify folders were created
        expect(result.foldersCreated, contains('lib/models'));
        expect(result.foldersCreated, contains('lib/screens'));
        expect(result.foldersCreated, contains('lib/widgets'));
        expect(result.foldersCreated, contains('lib/services'));
        expect(result.foldersCreated, contains('lib/utils'));

        // Verify files were created
        expect(result.filesCreated, contains('lib/main.dart'));
        expect(result.filesCreated, contains('lib/models/user.dart'));
        expect(result.filesCreated, contains('lib/screens/home_screen.dart'));

        // Verify actual files exist
        expect(await File(path.join(testProjectPath, 'lib/main.dart')).exists(),
            isTrue);
        expect(
            await File(path.join(testProjectPath, 'lib/models/user.dart'))
                .exists(),
            isTrue);
        expect(
            await Directory(path.join(testProjectPath, 'lib/models')).exists(),
            isTrue);
      });

      test('should generate layered architecture with dependencies', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'layered',
          force: true,
        );

        expect(result.success, isTrue);
        expect(result.architecture, equals('layered'));
        expect(result.dependenciesAdded, isNotEmpty);
        expect(result.dependenciesAdded, contains('get: ^4.6.6'));

        // Verify layered architecture folders
        expect(result.foldersCreated, contains('lib/models'));
        expect(result.foldersCreated, contains('lib/views'));
        expect(result.foldersCreated, contains('lib/controllers'));
        expect(result.foldersCreated, contains('lib/services'));
        expect(result.foldersCreated, contains('lib/repositories'));

        // Verify GetX integration in main.dart
        final mainFile = File(path.join(testProjectPath, 'lib/main.dart'));
        final mainContent = await mainFile.readAsString();
        expect(mainContent, contains('import \'package:get/get.dart\';'));
        expect(mainContent, contains('GetMaterialApp'));
      });

      test('should handle dry run mode', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          dryRun: true,
        );

        expect(result.success, isTrue);
        expect(result.foldersCreated, isNotEmpty);
        expect(result.filesCreated, isNotEmpty);

        // Verify no actual files were created in dry run
        expect(
            await File(path.join(testProjectPath, 'lib/models/user.dart'))
                .exists(),
            isFalse);
        expect(
            await Directory(path.join(testProjectPath, 'lib/models')).exists(),
            isFalse);
      });

      test('should fail for unknown architecture', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'unknown',
        );

        expect(result.success, isFalse);
        expect(result.errorMessage, contains('Unknown architecture: unknown'));
      });

      test('should fail for non-existent project path', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: '/non/existent/path',
          architectureName: 'flat',
        );

        expect(result.success, isFalse);
        expect(
            result.errorMessage, contains('Project directory does not exist'));
      });

      test('should handle existing files without force flag', () async {
        // Create a file that would conflict
        final conflictFile = File(path.join(testProjectPath, 'lib/main.dart'));
        await conflictFile.create(recursive: true);
        await conflictFile.writeAsString('existing content');

        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          force: false,
        );

        expect(result.success, isFalse);
        expect(result.errors, isNotEmpty);
        expect(
            result.errors.any((error) => error.contains('File already exists')),
            isTrue);
      });

      test('should overwrite existing files with force flag', () async {
        // Create a file that would conflict
        final conflictFile = File(path.join(testProjectPath, 'lib/main.dart'));
        await conflictFile.create(recursive: true);
        await conflictFile.writeAsString('existing content');

        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          force: true,
        );

        expect(result.success, isTrue);
        expect(result.filesCreated, contains('lib/main.dart'));

        // Verify file was overwritten
        final newContent = await conflictFile.readAsString();
        expect(newContent, isNot(equals('existing content')));
        expect(
            newContent, contains('import \'package:flutter/material.dart\';'));
      });

      test('should substitute template variables correctly', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          projectName: 'MyTestApp',
          packageName: 'com.test.myapp',
          force: true,
        );

        expect(result.success, isTrue);

        // Check that template variables were substituted
        final mainFile = File(path.join(testProjectPath, 'lib/main.dart'));
        final mainContent = await mainFile.readAsString();
        expect(mainContent, contains('MyTestApp'));

        final homeScreenFile =
            File(path.join(testProjectPath, 'lib/screens/home_screen.dart'));
        final homeScreenContent = await homeScreenFile.readAsString();
        expect(homeScreenContent, contains('Welcome to MyTestApp!'));
      });
    });

    group('listArchitectures', () {
      test('should list all available architectures', () {
        // This test verifies that listArchitectures runs without error
        // In a real test environment, we would capture stdout
        expect(
            () => ArchitectureGenerator.listArchitectures(), returnsNormally);
      });
    });

    group('helper methods', () {
      test('should generate correct project name from path', () async {
        final result = await ArchitectureGenerator.generateArchitecture(
          projectPath: testProjectPath,
          architectureName: 'flat',
          force: true,
        );

        expect(result.success, isTrue);

        // Check that project name was derived from path
        final mainFile = File(path.join(testProjectPath, 'lib/main.dart'));
        final mainContent = await mainFile.readAsString();
        final expectedProjectName = path.basename(testProjectPath);
        expect(mainContent, contains(expectedProjectName));
      });
    });
  });

  group('ArchitectureDefinition', () {
    test('should return all available architectures', () {
      final architectures = ArchitectureDefinition.getAllArchitectures();

      expect(architectures, isNotEmpty);
      expect(architectures.keys, contains('flat'));
      expect(architectures.keys, contains('layered'));
      expect(architectures.keys, contains('feature'));
      expect(architectures.keys, contains('bloc'));
      expect(architectures.keys, contains('mvvm'));
      expect(architectures.keys, contains('clean'));
      expect(architectures.keys, contains('redux'));
    });

    test('should return specific architecture by name', () {
      final flatArch = ArchitectureDefinition.getArchitecture('flat');
      expect(flatArch, isNotNull);
      expect(flatArch!.name, equals('flat'));
      expect(flatArch.displayName, equals('Flat/Simple Structure'));
      expect(flatArch.folders, isNotEmpty);
      expect(flatArch.files, isNotEmpty);
    });

    test('should return null for unknown architecture', () {
      final unknownArch = ArchitectureDefinition.getArchitecture('unknown');
      expect(unknownArch, isNull);
    });

    test('should return list of architecture names', () {
      final names = ArchitectureDefinition.getArchitectureNames();
      expect(names, isNotEmpty);
      expect(names, contains('flat'));
      expect(names, contains('layered'));
    });
  });
}

/// Create a basic Flutter project structure for testing
Future<void> _createBasicFlutterProject(String projectPath) async {
  // Create lib directory
  await Directory(path.join(projectPath, 'lib')).create(recursive: true);

  // Create pubspec.yaml
  final pubspecContent = '''
name: ${path.basename(projectPath)}
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
}
