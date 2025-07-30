/// Tests for keystore generation functionality
///
/// Validates that the Dart implementation can successfully generate keystores
/// and measures performance compared to the Python version.

import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import 'package:flutlock/flutlock.dart';

void main() {
  group('Keystore Generation Tests', () {
    late Directory tempDir;
    late String testKeystorePath;

    setUp(() async {
      // Create temporary directory for test keystores
      tempDir = await Directory.systemTemp.createTemp('flutlock_test_');
      testKeystorePath = path.join(tempDir.path, 'test_keystore.jks');
    });

    tearDown(() async {
      // Clean up temporary directory
      if (tempDir.existsSync()) {
        await tempDir.delete(recursive: true);
      }
    });

    test('should generate keystore with non-interactive mode', () async {
      // Use KeystoreConfig instead of environment variables
      final config = KeystoreConfig(
        storePassword: 'testpass123',
        keyPassword: 'testpass123',
      );

      final generator = KeystoreGenerator();
      final signerInfo = SignerInfo(
        name: 'Test User',
        orgUnit: 'Development',
        organization: 'FlutLock Test',
        locality: 'Test City',
        state: 'Test State',
        country: 'US',
      );

      final stopwatch = Stopwatch()..start();

      final success = await generator.generateKeystore(
        keystorePath: testKeystorePath,
        alias: 'test',
        config: config,
        signerInfo: signerInfo,
        interactive: false,
      );

      stopwatch.stop();

      expect(success, isTrue);
      expect(File(testKeystorePath).existsSync(), isTrue);

      print('Keystore generation time: ${stopwatch.elapsedMilliseconds}ms');

      // Verify keystore is valid by listing its contents
      final result = await Process.run('keytool', [
        '-list',
        '-keystore',
        testKeystorePath,
        '-storepass',
        config.storePassword!,
      ]);

      expect(result.exitCode, equals(0));
      expect(result.stdout.toString(), contains('test'));
    });

    test('should handle existing keystore in non-interactive mode', () async {
      // Use KeystoreConfig instead of environment variables
      final config = KeystoreConfig(
        storePassword: 'testpass123',
        keyPassword: 'testpass123',
      );

      final generator = KeystoreGenerator();
      final signerInfo = SignerInfo(
        name: 'Test User',
        orgUnit: 'Development',
        organization: 'FlutLock Test',
        locality: 'Test City',
        state: 'Test State',
        country: 'US',
      );

      // Generate keystore first time
      final success1 = await generator.generateKeystore(
        keystorePath: testKeystorePath,
        alias: 'test',
        config: config,
        signerInfo: signerInfo,
        interactive: false,
      );

      expect(success1, isTrue);
      expect(File(testKeystorePath).existsSync(), isTrue);

      // Try to generate again - should use existing
      final success2 = await generator.generateKeystore(
        keystorePath: testKeystorePath,
        alias: 'test',
        config: config,
        signerInfo: signerInfo,
        interactive: false,
      );

      expect(success2, isTrue);
      expect(File(testKeystorePath).existsSync(), isTrue);
    });

    test('should fail without required passwords', () async {
      // Don't provide any config (no passwords)

      final generator = KeystoreGenerator();
      final signerInfo = SignerInfo(
        name: 'Test User',
        orgUnit: 'Development',
        organization: 'FlutLock Test',
        locality: 'Test City',
        state: 'Test State',
        country: 'US',
      );

      expect(
        () async => await generator.generateKeystore(
          keystorePath: testKeystorePath,
          alias: 'test',
          signerInfo: signerInfo,
          interactive: false,
        ),
        throwsA(isA<KeystoreException>()),
      );
    });

    test('should create parent directories', () async {
      // Use KeystoreConfig instead of environment variables
      final config = KeystoreConfig(
        storePassword: 'testpass123',
        keyPassword: 'testpass123',
      );

      final nestedPath =
          path.join(tempDir.path, 'nested', 'deep', 'keystore.jks');

      final generator = KeystoreGenerator();
      final signerInfo = SignerInfo(
        name: 'Test User',
        orgUnit: 'Development',
        organization: 'FlutLock Test',
        locality: 'Test City',
        state: 'Test State',
        country: 'US',
      );

      final success = await generator.generateKeystore(
        keystorePath: nestedPath,
        alias: 'test',
        config: config,
        signerInfo: signerInfo,
        interactive: false,
      );

      expect(success, isTrue);
      expect(File(nestedPath).existsSync(), isTrue);
      expect(Directory(path.dirname(nestedPath)).existsSync(), isTrue);
    });
  });

  group('Performance Tests', () {
    test('should measure cold start time', () async {
      final stopwatch = Stopwatch()..start();

      // Import and initialize the library
      FlutLockCLI();

      stopwatch.stop();

      print('Cold start time: ${stopwatch.elapsedMilliseconds}ms');

      // Should be significantly faster than Python (target: <100ms)
      expect(stopwatch.elapsedMilliseconds, lessThan(500));
    });

    test('should measure dependency check performance', () async {
      final stopwatch = Stopwatch()..start();

      final dependencyChecker = DependencyChecker();
      await dependencyChecker.checkDependencies();

      stopwatch.stop();

      print('Dependency check time: ${stopwatch.elapsedMilliseconds}ms');

      // Should complete quickly
      expect(stopwatch.elapsedMilliseconds, lessThan(5000));
    });
  });

  group('CLI Integration Tests', () {
    late Directory tempDir;

    setUp(() async {
      tempDir = await Directory.systemTemp.createTemp('flutlock_cli_test_');
    });

    tearDown(() async {
      if (tempDir.existsSync()) {
        await tempDir.delete(recursive: true);
      }
    });

    test('should handle --check-deps command', () async {
      final cli = FlutLockCLI();

      final stopwatch = Stopwatch()..start();
      final exitCode = await cli.run(['--check-deps', '--quiet']);
      stopwatch.stop();

      print('CLI dependency check time: ${stopwatch.elapsedMilliseconds}ms');

      // Should exit with 0 or 1 (depending on dependencies)
      expect(exitCode, anyOf(equals(0), equals(1)));
    });

    test('should handle --help command', () async {
      final cli = FlutLockCLI();

      final exitCode = await cli.run(['--help']);

      expect(exitCode, equals(0));
    });

    test('should handle --version command', () async {
      final cli = FlutLockCLI();

      final exitCode = await cli.run(['--version']);

      expect(exitCode, equals(0));
    });
  });
}
