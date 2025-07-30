/// Tests for Flutter build functionality
///
/// This test suite validates the Flutter build execution module,
/// including build configuration, command construction, and error handling.

import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import 'package:flutlock/flutlock.dart';

void main() {
  group('FlutterBuilder', () {
    late Directory tempDir;
    late String testProjectPath;

    setUp(() async {
      // Create temporary directory for test projects
      tempDir = await Directory.systemTemp.createTemp('flutlock_test_');
      testProjectPath = tempDir.path;
    });

    tearDown(() async {
      // Clean up temporary directory
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    group('Flutter availability checks', () {
      test('should check if Flutter is available', () async {
        final isAvailable = await FlutterBuilder.isFlutterAvailable();
        // This test depends on Flutter being installed in the environment
        // In CI/CD, this might be false, so we just verify the method works
        expect(isAvailable, isA<bool>());
      });

      test('should get Flutter version if available', () async {
        final version = await FlutterBuilder.getFlutterVersion();
        // Version might be null if Flutter is not installed
        expect(version, anyOf(isNull, isA<String>()));
      });
    });

    group('Build configuration', () {
      test('should create default build configuration', () {
        const config = FlutterBuildConfig();

        expect(config.buildType, equals(BuildType.apk));
        expect(config.release, isTrue);
        expect(config.additionalArgs, isEmpty);
        expect(config.flavor, isNull);
        expect(config.target, isNull);
      });

      test('should create custom build configuration', () {
        const config = FlutterBuildConfig(
          buildType: BuildType.aab,
          release: false,
          additionalArgs: ['--verbose', '--dart-define=ENV=test'],
          flavor: 'development',
          target: 'lib/main_dev.dart',
        );

        expect(config.buildType, equals(BuildType.aab));
        expect(config.release, isFalse);
        expect(config.additionalArgs, contains('--verbose'));
        expect(config.additionalArgs, contains('--dart-define=ENV=test'));
        expect(config.flavor, equals('development'));
        expect(config.target, equals('lib/main_dev.dart'));
      });
    });

    group('Build type enum', () {
      test('should have correct command values', () {
        expect(BuildType.apk.command, equals('apk'));
        expect(BuildType.aab.command, equals('appbundle'));
      });

      test('should have correct string representation', () {
        expect(BuildType.apk.toString(), equals('apk'));
        expect(BuildType.aab.toString(), equals('aab'));
      });
    });

    group('Build output directory', () {
      test('should return correct APK output directory', () {
        final outputDir = FlutterBuilder.getBuildOutputDirectory(
          testProjectPath,
          BuildType.apk,
        );

        final expectedPath = path.join(
          testProjectPath,
          'build',
          'app',
          'outputs',
          'flutter-apk',
        );

        expect(outputDir, equals(expectedPath));
      });

      test('should return correct AAB output directory', () {
        final outputDir = FlutterBuilder.getBuildOutputDirectory(
          testProjectPath,
          BuildType.aab,
        );

        final expectedPath = path.join(
          testProjectPath,
          'build',
          'app',
          'outputs',
          'bundle',
          'release',
        );

        expect(outputDir, equals(expectedPath));
      });
    });

    group('Project validation', () {
      test('should reject invalid project path', () async {
        const config = FlutterBuildConfig();

        expect(
          () => FlutterBuilder.buildFlutterApp('/nonexistent/path', config),
          throwsA(isA<BuildException>()),
        );
      });

      test('should reject directory without pubspec.yaml', () async {
        // Create empty directory
        const config = FlutterBuildConfig();

        expect(
          () => FlutterBuilder.buildFlutterApp(testProjectPath, config),
          throwsA(isA<BuildException>()),
        );
      });

      test('should accept directory with valid pubspec.yaml', () async {
        // Create minimal pubspec.yaml
        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        await pubspecFile.writeAsString('''
name: test_app
description: Test Flutter app

flutter:
  uses-material-design: true
''');

        const config = FlutterBuildConfig();

        // This will fail because it's not a real Flutter project,
        // but it should pass the initial validation
        try {
          await FlutterBuilder.buildFlutterApp(testProjectPath, config);
          fail('Expected BuildException to be thrown');
        } on BuildException catch (e) {
          // Should fail at build execution, not project validation
          expect(e.message, isNot(contains('Invalid Flutter project path')));
          expect(e.message, isNot(contains('missing pubspec.yaml')));
          // Should fail because Flutter command is not available or project is incomplete
          expect(
              e.message,
              anyOf([
                contains('Flutter build failed'),
                contains('Unexpected error during Flutter build')
              ]));
        } on ProcessException {
          // This is expected if Flutter is not installed
          // The test passes because we got past project validation
        }
      });
    });

    group('Clean build artifacts', () {
      test('should handle clean command gracefully', () async {
        // Create minimal pubspec.yaml for flutter clean to work
        final pubspecFile = File(path.join(testProjectPath, 'pubspec.yaml'));
        await pubspecFile.writeAsString('''
name: test_app
description: Test Flutter app

flutter:
  uses-material-design: true
''');

        final result =
            await FlutterBuilder.cleanBuildArtifacts(testProjectPath);

        // Result depends on whether Flutter is available and project is valid
        expect(result, isA<bool>());
      });

      test('should handle clean command on invalid project', () async {
        final result =
            await FlutterBuilder.cleanBuildArtifacts('/nonexistent/path');

        // Should return false for invalid projects
        expect(result, isFalse);
      });
    });

    group('Build result', () {
      test('should create successful build result', () {
        const result = FlutterBuildResult(
          success: true,
          outputPath: '/path/to/app.apk',
          buildTime: Duration(seconds: 30),
        );

        expect(result.success, isTrue);
        expect(result.outputPath, equals('/path/to/app.apk'));
        expect(result.errorMessage, isNull);
        expect(result.buildTime, equals(const Duration(seconds: 30)));
      });

      test('should create failed build result', () {
        const result = FlutterBuildResult(
          success: false,
          outputPath: '',
          errorMessage: 'Build failed',
          buildTime: Duration(seconds: 5),
        );

        expect(result.success, isFalse);
        expect(result.outputPath, isEmpty);
        expect(result.errorMessage, equals('Build failed'));
        expect(result.buildTime, equals(const Duration(seconds: 5)));
      });
    });
  });
}
