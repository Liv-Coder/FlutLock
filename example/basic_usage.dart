/// Basic usage example of FlutLock library
///
/// This example demonstrates how to use FlutLock programmatically
/// to setup Flutter projects and manage Android signing.

import 'dart:io';
import 'package:flutlock/flutlock.dart';

void main() async {
  print('🚀 FlutLock Basic Usage Example');
  print('================================\n');

  try {
    // Example 1: Check dependencies
    print('📋 Checking system dependencies...');
    final dependencyChecker = DependencyChecker();
    final allDepsOk = await dependencyChecker.checkDependencies();

    print(
        'All dependencies: ${allDepsOk ? "✅ Found" : "❌ Missing some dependencies"}');
    print('Run "flutlock --check-deps" for detailed dependency information\n');

    // Example 2: Project analysis (conceptual)
    print('🔍 Project analysis capabilities...');
    print(
        'ProjectAnalyzer.analyzeFlutterProject() - Analyzes Flutter project structure');
    print('ProjectAnalyzer.getProjectStatus() - Gets quick project status');
    print(
        'Available for analyzing: pubspec.yaml, Android setup, Gradle config\n');

    // Example 3: Template engine usage (conceptual)
    print('📝 Template engine capabilities...');
    print('TemplateEngine.processTemplate() - Processes template files');
    print('TemplateContext - Provides variable substitution');
    print('Supports variables like: PROJECT_NAME, PACKAGE_NAME, VERSION_CODE');
    print('Used for generating: build.gradle, key.properties, Dart files\n');

    // Example 4: Architecture patterns (conceptual)
    print('🏗️ Available architecture patterns:');
    print('• flat: Flat/Simple Structure - Basic lib/ organization');
    print('• layered: Layered Architecture - Organized by technical layers');
    print(
        '• feature: Feature-First Architecture - Vertical slicing by features');
    print('• bloc: BLoC Architecture - Business Logic Component pattern');
    print('• mvvm: MVVM Architecture - Model-View-ViewModel pattern');
    print('• clean: Clean Architecture - Domain-driven design');
    print(
        '• feature-clean: Feature Wise Clean - Hybrid approach (36 folders, 43 files)');
    print('• redux: Redux Architecture - Redux pattern with actions/reducers');
    print('Use: flutlock --list-architectures for detailed information\n');

    // Example 5: Keystore operations (conceptual)
    print('🔐 Keystore operations capabilities...');
    print('KeystoreGenerator.generateKeystore() - Generate new keystore');
    print('KeystoreGenerator.validateKeystore() - Validate existing keystore');
    print('KeystoreConfig - Configuration for keystore generation');
    print(
        'Supports: password management, alias configuration, certificate details\n');

    // Example 6: Configuration processing (conceptual)
    print('⚙️ Configuration processing capabilities...');
    print('ConfigProcessor - Handles FlutLock configuration files');
    print('ConfigTemplates - Provides configuration templates');

    // Example configuration
    final sampleConfig = {
      'keystore': {
        'path': 'android/app/keystore.jks',
        'alias': 'my-app-key',
        'storePassword': 'store-password',
        'keyPassword': 'key-password',
      },
      'build': {
        'buildApk': true,
        'buildAab': false,
        'outputDir': 'build/app/outputs',
      },
      'signing': {
        'verifySignature': true,
        'skipExisting': false,
      }
    };

    print('Sample configuration structure:');
    print('${sampleConfig.toString()}\n');

    print('✅ Basic usage example completed successfully!');
    print('\n💡 Next steps:');
    print('• Try running: dart pub global activate flutlock');
    print('• Create a Flutter project: flutter create my_app');
    print(
        '• Setup with architecture: flutlock --setup-project --architecture feature-clean');
    print(
        '• Generate keystore: flutlock --keystore-path android/app/keystore.jks');
  } catch (e, stackTrace) {
    print('❌ Error running example: $e');
    print('Stack trace: $stackTrace');
    exit(1);
  }
}
