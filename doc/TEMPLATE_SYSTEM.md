# FlutLock Template System

The FlutLock template system provides a powerful and flexible way to generate Android project files for Flutter applications. This system is designed to automate the creation of properly configured Android build files with signing configurations.

## Overview

The template system consists of several key components:

- **Template Engine**: Core processing engine for variable substitution and file generation
- **Template Context**: Variable management and project-specific data
- **Embedded Templates**: Pre-built templates for common Android project files
- **CLI Integration**: Command-line interface for template management
- **Project Setup Integration**: Automatic file creation during project setup

## Template Engine

### TemplateEngine Class

The `TemplateEngine` class provides static methods for processing templates and creating files:

```dart
// Process a template string with variable substitution
final result = TemplateEngine.processTemplate(templateContent, context);

// Process a template file by name
final result = await TemplateEngine.processTemplateFile('android_build_gradle', context);

// Create a file from template
final success = await TemplateEngine.createFileFromTemplate(
  'android_build_gradle',
  'android/build.gradle',
  context,
  force: true,
  backup: true,
);
```

### Variable Substitution

The template engine supports two variable substitution formats:

1. **Shell-style**: `${VARIABLE_NAME}`
2. **Mustache-style**: `{{VARIABLE_NAME}}`

Variables that are not found in the context are left unchanged in the output.

## Template Context

### TemplateContext Class

The `TemplateContext` class manages variables for template processing:

```dart
// Create context from project information
final context = TemplateContext.fromProject(
  projectPath: '/path/to/project',
  projectName: 'my_app',
  packageName: 'com.example.myapp',
  keystorePath: '../keystore.jks',
  keyAlias: 'key',
);

// Manual context creation
final context = TemplateContext({
  'PROJECT_NAME': 'my_app',
  'PACKAGE_NAME': 'com.example.myapp',
});

// Get and set variables
final projectName = context.get('PROJECT_NAME');
context.set('CUSTOM_VAR', 'custom_value');
```

### Default Variables

When using `TemplateContext.fromProject()`, the following variables are automatically set:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `PROJECT_PATH` | Path to the project directory | Provided path |
| `PROJECT_NAME` | Name of the project | Provided name |
| `PACKAGE_NAME` | Android package name | `com.example.{project_name}` |
| `KEYSTORE_PATH` | Path to keystore file | `../keystore.jks` |
| `KEY_ALIAS` | Keystore key alias | `key` |
| `GRADLE_VERSION` | Gradle version | `8.0` |
| `ANDROID_GRADLE_PLUGIN_VERSION` | Android Gradle Plugin version | `8.1.0` |
| `COMPILE_SDK_VERSION` | Android compile SDK version | `34` |
| `MIN_SDK_VERSION` | Minimum Android SDK version | `21` |
| `TARGET_SDK_VERSION` | Target Android SDK version | `34` |

## Embedded Templates

### Available Templates

The following templates are embedded in the FlutLock system:

1. **android_build_gradle**: Root Android project build.gradle file
2. **android_app_build_gradle**: Android app module build.gradle file with signing configuration
3. **android_manifest**: AndroidManifest.xml file
4. **gradle_properties**: gradle.properties file with Android settings
5. **settings_gradle**: settings.gradle file for project structure

### Template Content

#### android_build_gradle
Creates the root-level build.gradle file with:
- Kotlin and Android Gradle Plugin dependencies
- Repository configurations
- Build directory settings

#### android_app_build_gradle
Creates the app-level build.gradle file with:
- Flutter integration
- Android configuration (SDK versions, package name)
- Signing configuration for release builds
- Keystore properties loading

#### android_manifest
Creates AndroidManifest.xml with:
- Main activity configuration
- Flutter embedding setup
- Launch intent filters

#### gradle_properties
Creates gradle.properties with:
- JVM arguments
- AndroidX and Jetifier settings

#### settings_gradle
Creates settings.gradle with:
- App module inclusion
- Flutter SDK integration

## CLI Commands

### List Templates

```bash
flutlock --list-templates
```

Lists all available templates with descriptions.

### Create File from Template

```bash
flutlock --create-template template_name:output_path
```

Creates a file from the specified template:

```bash
# Create Android build.gradle
flutlock --create-template android_build_gradle:android/build.gradle

# Create app build.gradle with custom project context
flutlock --path /my/project --create-template android_app_build_gradle:android/app/build.gradle

# Force overwrite existing file
flutlock --create-template android_manifest:android/app/src/main/AndroidManifest.xml --force

# Skip backup creation
flutlock --create-template gradle_properties:android/gradle.properties --no-backup
```

### Validate Templates

```bash
flutlock --validate-templates
```

Validates all embedded templates to ensure they process correctly.

## Project Setup Integration

The template system is automatically integrated with the project setup functionality:

```bash
# Setup project with template-based file creation
flutlock --setup-project

# Fix project structure using templates
flutlock --fix-structure
```

During project setup, the template system:

1. Analyzes the project structure
2. Identifies missing Android files
3. Creates template context from project information
4. Generates missing files using appropriate templates
5. Applies proper file permissions and backup handling

## Error Handling

The template system includes comprehensive error handling:

- **Template Not Found**: Returns error when template doesn't exist
- **Processing Errors**: Catches and reports template processing failures
- **File Creation Errors**: Handles file system errors during creation
- **Backup Failures**: Reports backup creation issues

## Testing

The template system includes extensive test coverage:

- **Template Context Tests**: Variable management and project context creation
- **Template Processing Tests**: Variable substitution and template rendering
- **Embedded Template Tests**: Validation of all built-in templates
- **File Creation Tests**: File system operations and error handling
- **CLI Integration Tests**: Command-line interface functionality

## Best Practices

### Template Usage

1. **Always validate templates** before using in production
2. **Use project context** for consistent variable values
3. **Enable backups** when overwriting existing files
4. **Test template output** in development environments

### Custom Templates

While the system currently uses embedded templates, it's designed to support custom templates:

1. Templates can be loaded from the file system
2. Custom template directories can be specified
3. Template validation ensures correctness

### Integration

When integrating the template system:

1. **Use TemplateContext.fromProject()** for consistent variable setup
2. **Handle errors gracefully** with try-catch blocks
3. **Provide user feedback** during file creation
4. **Respect force and backup flags** for user control

## Future Enhancements

The template system is designed for extensibility:

- **Custom Template Support**: Load templates from external files
- **Template Inheritance**: Support for template extension and overrides
- **Conditional Logic**: Template sections based on project configuration
- **Multi-language Support**: Templates for different programming languages
- **Template Validation**: Schema-based template validation
- **Template Marketplace**: Sharing and distribution of custom templates
