import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import '../lib/src/cli/flutlock_cli.dart';

void main() {
  group('Template CLI Commands', () {
    late String testDir;
    late FlutLockCLI cli;

    setUp(() async {
      final tempDir = await Directory.systemTemp.createTemp('template_cli_test_');
      testDir = tempDir.path;
      cli = FlutLockCLI();
    });

    tearDown(() async {
      if (await Directory(testDir).exists()) {
        await Directory(testDir).delete(recursive: true);
      }
    });

    group('List Templates Command', () {
      test('should list all available templates', () async {
        final result = await cli.run(['--list-templates']);
        expect(result, equals(0));
      });

      test('should exit after listing templates', () async {
        final result = await cli.run(['--list-templates', '--path', testDir]);
        expect(result, equals(0));
      });
    });

    group('Validate Templates Command', () {
      test('should validate all embedded templates', () async {
        final result = await cli.run(['--validate-templates']);
        expect(result, equals(0));
      });

      test('should exit after validation', () async {
        final result = await cli.run(['--validate-templates', '--path', testDir]);
        expect(result, equals(0));
      });
    });

    group('Create Template Command', () {
      test('should create file from android_build_gradle template', () async {
        final outputPath = path.join(testDir, 'build.gradle');
        final result = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('com.android.tools.build:gradle:8.1.0'));
        expect(content, contains('kotlin_version'));
      });

      test('should create file from android_app_build_gradle template', () async {
        final outputPath = path.join(testDir, 'app_build.gradle');
        final result = await cli.run([
          '--create-template',
          'android_app_build_gradle:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('namespace \'com.example.'));
        expect(content, contains('signingConfigs'));
        expect(content, contains('keystoreProperties'));
      });

      test('should create file from android_manifest template', () async {
        final outputPath = path.join(testDir, 'AndroidManifest.xml');
        final result = await cli.run([
          '--create-template',
          'android_manifest:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('<manifest'));
        expect(content, contains('MainActivity'));
        expect(content, contains('android.intent.action.MAIN'));
      });

      test('should create file from gradle_properties template', () async {
        final outputPath = path.join(testDir, 'gradle.properties');
        final result = await cli.run([
          '--create-template',
          'gradle_properties:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('org.gradle.jvmargs'));
        expect(content, contains('android.useAndroidX'));
        expect(content, contains('android.enableJetifier'));
      });

      test('should create file from settings_gradle template', () async {
        final outputPath = path.join(testDir, 'settings.gradle');
        final result = await cli.run([
          '--create-template',
          'settings_gradle:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('include \':app\''));
        expect(content, contains('flutter.sdk'));
        expect(content, contains('app_plugin_loader.gradle'));
      });

      test('should handle invalid template specification', () async {
        final result = await cli.run([
          '--create-template',
          'invalid_format',
          '--path',
          testDir,
        ]);

        expect(result, equals(1));
      });

      test('should handle unknown template name', () async {
        final outputPath = path.join(testDir, 'unknown.gradle');
        final result = await cli.run([
          '--create-template',
          'unknown_template:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(1));
      });

      test('should respect force flag when overwriting files', () async {
        final outputPath = path.join(testDir, 'build.gradle');
        
        // Create existing file
        await File(outputPath).writeAsString('existing content');

        // Try without force (should fail)
        final result1 = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result1, equals(1));
        final content1 = await File(outputPath).readAsString();
        expect(content1, equals('existing content'));

        // Try with force (should succeed)
        final result2 = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
          '--force',
        ]);

        expect(result2, equals(0));
        final content2 = await File(outputPath).readAsString();
        expect(content2, contains('com.android.tools.build:gradle'));
      });

      test('should create backup when overwriting with backup enabled', () async {
        final outputPath = path.join(testDir, 'build.gradle');
        
        // Create existing file
        await File(outputPath).writeAsString('existing content');

        // Overwrite with backup (default)
        final result = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
          '--force',
        ]);

        expect(result, equals(0));

        // Check that backup was created
        final backupFiles = await Directory(testDir)
            .list()
            .where((entity) => entity.path.contains('.backup.'))
            .toList();
        expect(backupFiles, isNotEmpty);
      });

      test('should skip backup when no-backup flag is used', () async {
        final outputPath = path.join(testDir, 'build.gradle');
        
        // Create existing file
        await File(outputPath).writeAsString('existing content');

        // Overwrite without backup
        final result = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
          '--force',
          '--no-backup',
        ]);

        expect(result, equals(0));

        // Check that no backup was created
        final backupFiles = await Directory(testDir)
            .list()
            .where((entity) => entity.path.contains('.backup.'))
            .toList();
        expect(backupFiles, isEmpty);
      });

      test('should create output directory if it does not exist', () async {
        final outputPath = path.join(testDir, 'nested', 'dir', 'build.gradle');
        
        final result = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          testDir,
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);
        expect(await Directory(path.join(testDir, 'nested', 'dir')).exists(), isTrue);
      });

      test('should use absolute path when provided', () async {
        final outputPath = path.join(testDir, 'absolute_build.gradle');
        
        final result = await cli.run([
          '--create-template',
          'android_build_gradle:$outputPath',
          '--path',
          '/different/path',
        ]);

        expect(result, equals(0));
        expect(await File(outputPath).exists(), isTrue);
      });
    });

    group('Template Command Priority', () {
      test('should prioritize template commands over other commands', () async {
        // List templates should execute even with other flags
        final result = await cli.run([
          '--list-templates',
          '--path',
          testDir,
          '--verbose',
        ]);

        expect(result, equals(0));
      });

      test('should handle multiple template commands correctly', () async {
        // Only the first template command should execute
        final result = await cli.run([
          '--list-templates',
          '--validate-templates',
        ]);

        expect(result, equals(0));
      });
    });
  });
}
