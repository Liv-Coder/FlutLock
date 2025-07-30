import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import '../lib/src/core/template_engine.dart';

void main() {
  group('TemplateEngine', () {
    late String testDir;

    setUp(() async {
      final tempDir = await Directory.systemTemp.createTemp('template_test_');
      testDir = tempDir.path;
    });

    tearDown(() async {
      if (await Directory(testDir).exists()) {
        await Directory(testDir).delete(recursive: true);
      }
    });

    group('TemplateContext', () {
      test('should create context from project', () {
        final context = TemplateContext.fromProject(
          projectPath: '/test/project',
          projectName: 'test_app',
          packageName: 'com.example.test',
        );

        expect(context.get('PROJECT_PATH'), equals('/test/project'));
        expect(context.get('PROJECT_NAME'), equals('test_app'));
        expect(context.get('PACKAGE_NAME'), equals('com.example.test'));
        expect(context.get('GRADLE_VERSION'), equals('8.0'));
      });

      test('should handle missing package name with default', () {
        final context = TemplateContext.fromProject(
          projectPath: '/test/project',
          projectName: 'test_app',
        );

        expect(context.get('PACKAGE_NAME'), equals('com.example.test_app'));
      });

      test('should allow setting and getting variables', () {
        final context = TemplateContext({});

        context.set('CUSTOM_VAR', 'custom_value');
        expect(context.get('CUSTOM_VAR'), equals('custom_value'));
        expect(context.get('MISSING_VAR', 'default'), equals('default'));
      });
    });

    group('Template Processing', () {
      test('should process template with variable substitution', () {
        final template = '''
Project: \${PROJECT_NAME}
Package: \${PACKAGE_NAME}
Version: \${VERSION}
''';
        final context = TemplateContext({
          'PROJECT_NAME': 'test_app',
          'PACKAGE_NAME': 'com.example.test',
          'VERSION': '1.0.0',
        });

        final result = TemplateEngine.processTemplate(template, context);

        expect(result.success, isTrue);
        expect(result.content, contains('Project: test_app'));
        expect(result.content, contains('Package: com.example.test'));
        expect(result.content, contains('Version: 1.0.0'));
      });

      test('should process template with mustache syntax', () {
        final template = '''
Project: {{PROJECT_NAME}}
Package: {{PACKAGE_NAME}}
''';
        final context = TemplateContext({
          'PROJECT_NAME': 'test_app',
          'PACKAGE_NAME': 'com.example.test',
        });

        final result = TemplateEngine.processTemplate(template, context);

        expect(result.success, isTrue);
        expect(result.content, contains('Project: test_app'));
        expect(result.content, contains('Package: com.example.test'));
      });

      test('should leave unknown variables unchanged', () {
        final template = 'Known: \${KNOWN}, Unknown: \${UNKNOWN}';
        final context = TemplateContext({'KNOWN': 'value'});

        final result = TemplateEngine.processTemplate(template, context);

        expect(result.success, isTrue);
        expect(result.content, contains('Known: value'));
        expect(result.content, contains('Unknown: \${UNKNOWN}'));
      });
    });

    group('Embedded Templates', () {
      test('should process android build gradle template', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
          packageName: 'com.example.test',
        );

        final result = await TemplateEngine.processTemplateFile(
          'android_build_gradle',
          context,
        );

        expect(result.success, isTrue);
        expect(
            result.content, contains('com.android.tools.build:gradle:8.1.0'));
        expect(result.content, contains('kotlin_version'));
        expect(result.content, contains('google()'));
      });

      test('should process android app build gradle template', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
          packageName: 'com.example.test',
        );

        final result = await TemplateEngine.processTemplateFile(
          'android_app_build_gradle',
          context,
        );

        expect(result.success, isTrue);
        expect(result.content, contains('namespace \'com.example.test\''));
        expect(result.content, contains('applicationId \'com.example.test\''));
        expect(result.content, contains('compileSdkVersion 34'));
        expect(result.content, contains('signingConfigs'));
      });

      test('should process android manifest template', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
          packageName: 'com.example.test',
        );

        final result = await TemplateEngine.processTemplateFile(
          'android_manifest',
          context,
        );

        expect(result.success, isTrue);
        expect(result.content, contains('android:label="test_app"'));
        expect(result.content, contains('MainActivity'));
        expect(result.content, contains('android.intent.action.MAIN'));
      });

      test('should return error for unknown template', () async {
        final context = TemplateContext({});

        final result = await TemplateEngine.processTemplateFile(
          'unknown_template',
          context,
        );

        expect(result.success, isFalse);
        expect(result.error, contains('Template not found'));
      });
    });

    group('File Creation', () {
      test('should create file from template', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
          packageName: 'com.example.test',
        );

        final outputPath = path.join(testDir, 'build.gradle');
        final success = await TemplateEngine.createFileFromTemplate(
          'android_build_gradle',
          outputPath,
          context,
        );

        expect(success, isTrue);
        expect(await File(outputPath).exists(), isTrue);

        final content = await File(outputPath).readAsString();
        expect(content, contains('com.android.tools.build:gradle:8.1.0'));
      });

      test('should not overwrite existing file without force', () async {
        final context = TemplateContext({});
        final outputPath = path.join(testDir, 'existing.gradle');

        // Create existing file
        await File(outputPath).writeAsString('existing content');

        final success = await TemplateEngine.createFileFromTemplate(
          'android_build_gradle',
          outputPath,
          context,
          force: false,
        );

        expect(success, isFalse);
        final content = await File(outputPath).readAsString();
        expect(content, equals('existing content'));
      });

      test('should overwrite existing file with force', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
        );
        final outputPath = path.join(testDir, 'existing.gradle');

        // Create existing file
        await File(outputPath).writeAsString('existing content');

        final success = await TemplateEngine.createFileFromTemplate(
          'android_build_gradle',
          outputPath,
          context,
          force: true,
        );

        expect(success, isTrue);
        final content = await File(outputPath).readAsString();
        expect(content, contains('com.android.tools.build:gradle'));
      });

      test('should create backup when overwriting', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
        );
        final outputPath = path.join(testDir, 'existing.gradle');

        // Create existing file
        await File(outputPath).writeAsString('existing content');

        final success = await TemplateEngine.createFileFromTemplate(
          'android_build_gradle',
          outputPath,
          context,
          force: true,
          backup: true,
        );

        expect(success, isTrue);

        // Check that backup was created
        final backupFiles = await Directory(testDir)
            .list()
            .where((entity) => entity.path.contains('.backup.'))
            .toList();
        expect(backupFiles, isNotEmpty);
      });

      test('should create output directory if it does not exist', () async {
        final context = TemplateContext.fromProject(
          projectPath: testDir,
          projectName: 'test_app',
        );
        final outputPath = path.join(testDir, 'nested', 'dir', 'build.gradle');

        final success = await TemplateEngine.createFileFromTemplate(
          'android_build_gradle',
          outputPath,
          context,
        );

        expect(success, isTrue);
        expect(await File(outputPath).exists(), isTrue);
        expect(await Directory(path.join(testDir, 'nested', 'dir')).exists(),
            isTrue);
      });
    });
  });
}
