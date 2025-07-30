import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;

import '../lib/src/core/dependency_manager.dart';

void main() {
  group('DependencyManager', () {
    late String testProjectPath;

    setUp(() async {
      // Create temporary test directory
      final tempDir = await Directory.systemTemp.createTemp('flutlock_dep_test_');
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

    group('updateDependencies', () {
      test('should add new dependencies successfully', () async {
        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get', 'http'],
          devDependencies: ['build_runner'],
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, contains('get: ^4.6.6'));
        expect(result.dependenciesAdded, contains('http: ^1.1.0'));
        expect(result.devDependenciesAdded, contains('build_runner: ^2.4.7'));

        // Verify pubspec.yaml was updated
        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        final pubspecContent = await pubspecFile.readAsString();
        expect(pubspecContent, contains('get: ^4.6.6'));
        expect(pubspecContent, contains('http: ^1.1.0'));
        expect(pubspecContent, contains('build_runner: ^2.4.7'));
      });

      test('should handle dry run mode', () async {
        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get'],
          devDependencies: ['build_runner'],
          dryRun: true,
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, contains('get: ^4.6.6'));
        expect(result.devDependenciesAdded, contains('build_runner: ^2.4.7'));

        // Verify pubspec.yaml was NOT updated in dry run
        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        final pubspecContent = await pubspecFile.readAsString();
        expect(pubspecContent, isNot(contains('get: ^4.6.6')));
        expect(pubspecContent, isNot(contains('build_runner: ^2.4.7')));
      });

      test('should skip existing dependencies', () async {
        // First, add a dependency
        await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get'],
          devDependencies: [],
        );

        // Try to add the same dependency again
        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get', 'http'],
          devDependencies: [],
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, isNot(contains('get: ^4.6.6')));
        expect(result.dependenciesAdded, contains('http: ^1.1.0'));
      });

      test('should handle empty dependency lists', () async {
        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: [],
          devDependencies: [],
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, isEmpty);
        expect(result.devDependenciesAdded, isEmpty);
      });

      test('should fail for non-existent project', () async {
        final result = await DependencyManager.updateDependencies(
          projectPath: '/non/existent/path',
          dependencies: ['get'],
          devDependencies: [],
        );

        expect(result.success, isFalse);
        expect(result.errorMessage, contains('pubspec.yaml not found'));
      });

      test('should preserve existing pubspec structure', () async {
        // Add some custom content to pubspec.yaml
        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        final originalContent = await pubspecFile.readAsString();
        
        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get'],
          devDependencies: [],
        );

        expect(result.success, isTrue);

        // Verify original structure is preserved
        final updatedContent = await pubspecFile.readAsString();
        expect(updatedContent, contains('name: ${path.basename(testProjectPath)}'));
        expect(updatedContent, contains('description: A test Flutter project'));
        expect(updatedContent, contains('version: 1.0.0+1'));
        expect(updatedContent, contains('flutter:'));
        expect(updatedContent, contains('uses-material-design: true'));
        expect(updatedContent, contains('get: ^4.6.6'));
      });

      test('should handle complex pubspec with existing dependencies', () async {
        // Create a more complex pubspec.yaml
        final complexPubspec = '''
name: ${path.basename(testProjectPath)}
description: A test Flutter project
version: 1.0.0+1

environment:
  sdk: '>=2.17.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  shared_preferences: ^2.0.15

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
  assets:
    - images/
''';

        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        await pubspecFile.writeAsString(complexPubspec);

        final result = await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get', 'http'],
          devDependencies: ['build_runner'],
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, contains('get: ^4.6.6'));
        expect(result.dependenciesAdded, contains('http: ^1.1.0'));
        expect(result.devDependenciesAdded, contains('build_runner: ^2.4.7'));

        // Verify existing dependencies are preserved
        final updatedContent = await pubspecFile.readAsString();
        expect(updatedContent, contains('cupertino_icons: ^1.0.2'));
        expect(updatedContent, contains('shared_preferences: ^2.0.15'));
        expect(updatedContent, contains('flutter_lints: ^2.0.0'));
        expect(updatedContent, contains('assets:'));
        expect(updatedContent, contains('- images/'));
      });
    });

    group('helper methods', () {
      test('should return correct dependency versions', () {
        expect(DependencyManager.getDependencyVersion('get'), equals('^4.6.6'));
        expect(DependencyManager.getDependencyVersion('http'), equals('^1.1.0'));
        expect(DependencyManager.getDependencyVersion('unknown_package'), equals('^1.0.0'));
      });

      test('should return correct dev dependency versions', () {
        expect(DependencyManager.getDevDependencyVersion('build_runner'), equals('^2.4.7'));
        expect(DependencyManager.getDevDependencyVersion('freezed'), equals('^2.4.6'));
        expect(DependencyManager.getDevDependencyVersion('unknown_package'), equals('^1.0.0'));
      });

      test('should check if dependency exists', () async {
        // Add a dependency first
        await DependencyManager.updateDependencies(
          projectPath: testProjectPath,
          dependencies: ['get'],
          devDependencies: ['build_runner'],
        );

        expect(await DependencyManager.hasDependency(testProjectPath, 'get'), isTrue);
        expect(await DependencyManager.hasDependency(testProjectPath, 'build_runner'), isTrue);
        expect(await DependencyManager.hasDependency(testProjectPath, 'flutter'), isTrue);
        expect(await DependencyManager.hasDependency(testProjectPath, 'non_existent'), isFalse);
      });

      test('should handle missing pubspec when checking dependencies', () async {
        final nonExistentPath = path.join(testProjectPath, 'non_existent');
        expect(await DependencyManager.hasDependency(nonExistentPath, 'get'), isFalse);
      });
    });

    group('DependencyResult', () {
      test('should create success result correctly', () {
        final result = DependencyResult.success(
          dependenciesAdded: ['get: ^4.6.6'],
          devDependenciesAdded: ['build_runner: ^2.4.7'],
        );

        expect(result.success, isTrue);
        expect(result.dependenciesAdded, equals(['get: ^4.6.6']));
        expect(result.devDependenciesAdded, equals(['build_runner: ^2.4.7']));
        expect(result.errors, isEmpty);
        expect(result.errorMessage, isNull);
      });

      test('should create failure result correctly', () {
        final result = DependencyResult.failure(
          errorMessage: 'Test error',
          errors: ['Error 1', 'Error 2'],
        );

        expect(result.success, isFalse);
        expect(result.dependenciesAdded, isEmpty);
        expect(result.devDependenciesAdded, isEmpty);
        expect(result.errors, equals(['Error 1', 'Error 2']));
        expect(result.errorMessage, equals('Test error'));
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
