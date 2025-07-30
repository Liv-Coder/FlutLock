import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import 'package:flutlock/flutlock.dart';

void main() {
  group('SignatureVerifier', () {
    late Directory tempDir;
    late String testProjectPath;
    late String testApkPath;

    setUpAll(() async {
      // Create temporary directory for test projects
      tempDir =
          await Directory.systemTemp.createTemp('flutlock_signature_test_');
      testProjectPath = tempDir.path;
      testApkPath = path.join(testProjectPath, 'test-app.apk');

      // Create a dummy APK file for testing
      await File(testApkPath).writeAsString('dummy apk content');
    });

    tearDownAll(() async {
      // Clean up temporary directory
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    group('SignatureVerificationConfig', () {
      test('should create config with default values', () {
        const config = SignatureVerificationConfig();

        expect(config.verifySignature, isTrue);
        expect(config.verbose, isFalse);
        expect(config.preferredTool, isNull);
        expect(config.timeoutSeconds, equals(30));
      });

      test('should create config with custom values', () {
        const config = SignatureVerificationConfig(
          verifySignature: false,
          verbose: true,
          preferredTool: 'apksigner',
          timeoutSeconds: 60,
        );

        expect(config.verifySignature, isFalse);
        expect(config.verbose, isTrue);
        expect(config.preferredTool, equals('apksigner'));
        expect(config.timeoutSeconds, equals(60));
      });

      test('should create config from build configuration map', () {
        final buildConfig = {
          'verify': false,
          'verbose_verify': true,
          'verification_tool': 'jarsigner',
          'verification_timeout': 45,
        };

        final config = SignatureVerificationConfig.fromBuildConfig(buildConfig);

        expect(config.verifySignature, isFalse);
        expect(config.verbose, isTrue);
        expect(config.preferredTool, equals('jarsigner'));
        expect(config.timeoutSeconds, equals(45));
      });

      test('should use defaults for missing build configuration values', () {
        final buildConfig = <String, dynamic>{
          'verify': false,
        };

        final config = SignatureVerificationConfig.fromBuildConfig(buildConfig);

        expect(config.verifySignature, isFalse);
        expect(config.verbose, isFalse);
        expect(config.preferredTool, isNull);
        expect(config.timeoutSeconds, equals(30));
      });

      test('should use defaults for null build configuration', () {
        final config = SignatureVerificationConfig.fromBuildConfig(null);

        expect(config.verifySignature, isTrue);
        expect(config.verbose, isFalse);
        expect(config.preferredTool, isNull);
        expect(config.timeoutSeconds, equals(30));
      });
    });

    group('SignatureVerificationResult', () {
      test('should create successful result', () {
        final result = SignatureVerificationResult.success(
          filePath: '/path/to/app.apk',
          toolUsed: 'apksigner',
          output: 'Verified successfully',
          details: {'scheme': 'v2'},
        );

        expect(result.success, isTrue);
        expect(result.filePath, equals('/path/to/app.apk'));
        expect(result.toolUsed, equals('apksigner'));
        expect(result.output, equals('Verified successfully'));
        expect(result.errorMessage, isNull);
        expect(result.details['scheme'], equals('v2'));
      });

      test('should create failure result', () {
        final result = SignatureVerificationResult.failure(
          filePath: '/path/to/app.apk',
          toolUsed: 'apksigner',
          output: 'Verification failed',
          errorMessage: 'Invalid signature',
          details: {'error_code': 1},
        );

        expect(result.success, isFalse);
        expect(result.filePath, equals('/path/to/app.apk'));
        expect(result.toolUsed, equals('apksigner'));
        expect(result.output, equals('Verification failed'));
        expect(result.errorMessage, equals('Invalid signature'));
        expect(result.details['error_code'], equals(1));
      });
    });

    group('Tool availability checking', () {
      test('should check verification tools availability', () async {
        final tools = await SignatureVerifier.checkVerificationTools();

        expect(tools, isA<Map<String, bool>>());
        expect(tools.containsKey('apksigner'), isTrue);
        expect(tools.containsKey('jarsigner'), isTrue);
        expect(tools['apksigner'], isA<bool>());
        expect(tools['jarsigner'], isA<bool>());
      });
    });

    group('File validation', () {
      test('should fail when file does not exist', () async {
        const config = SignatureVerificationConfig();

        expect(
          () => SignatureVerifier.verifySignature('/nonexistent/file.apk',
              config: config),
          throwsA(isA<FlutLockException>()),
        );
      });
    });

    group('Output parsing', () {
      test('should parse apksigner output correctly', () {
        const output = '''
Verifies
Verified using v1 scheme (JAR signing): true
Verified using v2 scheme (APK Signature Scheme v2): true
''';

        final details = SignatureVerifier.parseApksignerOutput(output);

        expect(details['status'], equals('verified'));
        expect(details['signature_scheme'], equals('v2'));
      });

      test('should parse jarsigner output correctly', () {
        const output = '''
jar verified.

Warning:
This jar contains entries whose certificate chain is not validated.
''';

        final details = SignatureVerifier.parseJarsignerOutput(output);

        expect(details['status'], equals('jar verified'));
      });

      test('should handle verbose jarsigner output', () {
        const output = '''
jar verified.

Certificate fingerprints:
         MD5:  12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF
         SHA1: 12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78
''';

        final details = SignatureVerifier.parseJarsignerOutput(output);

        expect(details['status'], equals('jar verified'));
        expect(details['has_certificate_info'], isTrue);
      });
    });

    group('Integration tests', () {
      test('should handle verification when no tools are available', () async {
        // This test will pass if neither apksigner nor jarsigner are available
        // or will test the actual verification if tools are available
        const config = SignatureVerificationConfig();

        try {
          final result = await SignatureVerifier.verifySignature(testApkPath,
              config: config);
          // If we get here, verification tools are available
          expect(result, isA<SignatureVerificationResult>());
          expect(result.filePath, equals(testApkPath));
        } catch (e) {
          // If we get an exception, it should be about missing tools or invalid file
          expect(e, isA<FlutLockException>());
          expect(
              e.toString(),
              anyOf(
                contains('Neither apksigner nor jarsigner found'),
                contains('failed to parse'),
                contains('DOES NOT VERIFY'),
              ));
        }
      });

      test('should handle timeout configuration', () async {
        const config = SignatureVerificationConfig(timeoutSeconds: 1);

        try {
          await SignatureVerifier.verifySignature(testApkPath, config: config);
        } catch (e) {
          // Timeout or other verification error is expected
          expect(e, isA<FlutLockException>());
        }
      });

      test('should handle verbose configuration', () async {
        const config = SignatureVerificationConfig(verbose: true);

        try {
          await SignatureVerifier.verifySignature(testApkPath, config: config);
        } catch (e) {
          // Verification error is expected for dummy file
          expect(e, isA<FlutLockException>());
        }
      });
    });

    group('Error handling', () {
      test('should handle process execution errors gracefully', () async {
        const config = SignatureVerificationConfig();

        // Test with a file that exists but is not a valid APK
        final invalidFile = path.join(testProjectPath, 'invalid.apk');
        await File(invalidFile).writeAsString('not a valid apk');

        try {
          await SignatureVerifier.verifySignature(invalidFile, config: config);
        } catch (e) {
          expect(e, isA<FlutLockException>());
        }
      });

      test('should provide helpful error messages', () async {
        const config = SignatureVerificationConfig();

        try {
          await SignatureVerifier.verifySignature('/nonexistent/file.apk',
              config: config);
          fail('Should have thrown an exception');
        } catch (e) {
          expect(e, isA<FlutLockException>());
          expect(e.toString(), contains('Output file not found'));
        }
      });
    });
  });
}
