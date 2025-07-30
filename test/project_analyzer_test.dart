import 'dart:io';
import 'package:test/test.dart';
import 'package:path/path.dart' as path;
import '../lib/src/core/project_analyzer.dart';
import '../lib/src/utils/exceptions.dart';

void main() {
  group('ProjectAnalyzer', () {
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

    group('analyzeFlutterProject', () {
      test('should throw exception for non-existent directory', () async {
        final nonExistentPath = path.join(testProjectPath, 'non_existent');
        
        expect(
          () => ProjectAnalyzer.analyzeFlutterProject(nonExistentPath),
          throwsA(isA<ProjectAnalysisException>()),
        );
      });

      test('should detect non-Flutter project', () async {
        // Create empty directory
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.isFlutterProject, isFalse);
        expect(result.projectPath, equals(path.absolute(testProjectPath)));
        expect(result.missingFiles, contains('pubspec.yaml'));
        expect(result.missingDirectories, contains('lib'));
        expect(result.warnings, isNotEmpty);
      });

      test('should detect basic Flutter project structure', () async {
        // Create basic Flutter project structure
        await _createBasicFlutterProject(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.isFlutterProject, isTrue);
        expect(result.projectName, equals('test_project'));
        expect(result.hasPubspec, isTrue);
        expect(result.hasAndroidDir, isFalse);
        expect(result.isReadyForSigning, isFalse);
      });

      test('should detect complete Flutter project with Android support', () async {
        // Create complete Flutter project structure
        await _createCompleteFlutterProject(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.isFlutterProject, isTrue);
        expect(result.hasAndroidDir, isTrue);
        expect(result.hasAndroidAppDir, isTrue);
        expect(result.hasAndroidGradle, isTrue);
        expect(result.hasAppGradle, isTrue);
        expect(result.missingDirectories, isEmpty);
        expect(result.missingFiles, isEmpty);
      });

      test('should detect existing keystore and signing configuration', () async {
        // Create project with keystore and signing config
        await _createProjectWithSigning(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.hasKeyProperties, isTrue);
        expect(result.hasKeystore, isTrue);
        expect(result.existingSigningConfig, isTrue);
        expect(result.existingKeystorePath, isNotNull);
        expect(result.isReadyForSigning, isTrue);
      });

      test('should extract Android package name from build.gradle', () async {
        // Create project with package name in build.gradle
        await _createProjectWithPackageName(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.androidPackageName, equals('com.example.testapp'));
      });

      test('should generate appropriate recommendations', () async {
        // Create minimal Flutter project
        await _createBasicFlutterProject(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.recommendations, isNotEmpty);
        expect(
          result.recommendations.any((r) => r.contains('Add Android support')),
          isTrue,
        );
        expect(
          result.recommendations.any((r) => r.contains('Generate a keystore')),
          isTrue,
        );
      });

      test('should handle malformed pubspec.yaml gracefully', () async {
        // Create project with malformed pubspec.yaml
        await _createProjectWithMalformedPubspec(testProjectPath);
        
        final result = await ProjectAnalyzer.analyzeFlutterProject(testProjectPath);
        
        expect(result.hasPubspec, isTrue);
        expect(result.isFlutterProject, isTrue);
        expect(result.warnings, isNotEmpty);
        expect(
          result.warnings.any((w) => w.contains('Could not parse pubspec.yaml')),
          isTrue,
        );
      });
    });

    group('getProjectStatus', () {
      test('should return status summary for valid project', () async {
        await _createCompleteFlutterProject(testProjectPath);
        
        final status = await ProjectAnalyzer.getProjectStatus(testProjectPath);
        
        expect(status['is_flutter_project'], isTrue);
        expect(status['project_name'], equals('test_project'));
        expect(status['ready_for_signing'], isFalse);
        expect(status['missing_components'], isA<int>());
        expect(status['warnings_count'], isA<int>());
      });

      test('should return error status for invalid project', () async {
        final nonExistentPath = path.join(testProjectPath, 'non_existent');
        
        final status = await ProjectAnalyzer.getProjectStatus(nonExistentPath);
        
        expect(status['is_flutter_project'], isFalse);
        expect(status['error'], isNotNull);
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
  
  await File(path.join(projectPath, 'pubspec.yaml')).writeAsString(pubspecContent);
  
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
  await File(path.join(projectPath, 'android', 'build.gradle')).writeAsString('''
buildscript {
    ext.kotlin_version = '1.7.10'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.2.0'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:\$kotlin_version"
    }
}
''');
  
  // Create android/app/build.gradle
  await File(path.join(projectPath, 'android', 'app', 'build.gradle')).writeAsString('''
def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterRoot = localProperties.getProperty('flutter.sdk')
if (flutterRoot == null) {
    throw new GradleException("Flutter SDK not found. Define location with flutter.sdk in the local.properties file.")
}

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
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
''');
  
  // Create AndroidManifest.xml
  await File(path.join(projectPath, 'android', 'app', 'src', 'main', 'AndroidManifest.xml'))
      .writeAsString('''
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.testproject">
    
    <application
        android:label="test_project"
        android:name="\${applicationName}"
        android:icon="@mipmap/ic_launcher">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme">
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
''');
}

/// Create a project with keystore and signing configuration
Future<void> _createProjectWithSigning(String projectPath) async {
  await _createCompleteFlutterProject(projectPath);
  
  // Create key.properties
  await File(path.join(projectPath, 'android', 'key.properties')).writeAsString('''
storePassword=password123
keyPassword=password123
keyAlias=upload
storeFile=../app/upload-keystore.jks
''');
  
  // Create keystore file
  await File(path.join(projectPath, 'android', 'app', 'upload-keystore.jks'))
      .writeAsString('dummy keystore content');
  
  // Update build.gradle with signing configuration
  await File(path.join(projectPath, 'android', 'app', 'build.gradle')).writeAsString('''
def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    compileSdkVersion 33
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
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

/// Create a project with package name in build.gradle
Future<void> _createProjectWithPackageName(String projectPath) async {
  await _createCompleteFlutterProject(projectPath);
  
  // Update build.gradle with specific package name
  await File(path.join(projectPath, 'android', 'app', 'build.gradle')).writeAsString('''
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.example.testapp"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
}
''');
}

/// Create a project with malformed pubspec.yaml
Future<void> _createProjectWithMalformedPubspec(String projectPath) async {
  // Create lib directory
  await Directory(path.join(projectPath, 'lib')).create(recursive: true);
  
  // Create malformed pubspec.yaml
  await File(path.join(projectPath, 'pubspec.yaml')).writeAsString('''
name: test_project
description: A test Flutter project
version: 1.0.0+1
invalid_yaml: [unclosed bracket
dependencies:
  flutter:
    sdk: flutter
''');
}
