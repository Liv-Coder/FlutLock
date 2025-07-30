# Flutter Architecture Patterns

FlutLock provides automatic generation of complete Flutter project structures using 7 different architecture patterns. Each pattern includes folder structures, boilerplate files, and architecture-specific dependencies.

## Available Architecture Patterns

### 1. Flat/Simple Structure (`flat`)

**Description**: Basic lib/ organization with minimal folder structure. Perfect for small projects and prototypes.

**Folder Structure**:
```
lib/
├── models/
├── screens/
├── widgets/
├── services/
├── utils/
└── main.dart
```

**Generated Files**:
- `lib/main.dart` - Basic Flutter app entry point
- `lib/models/user.dart` - Sample user model
- `lib/screens/home_screen.dart` - Home screen widget
- `lib/widgets/custom_button.dart` - Reusable button widget
- `lib/services/api_service.dart` - API service class
- `lib/utils/constants.dart` - App constants

**Dependencies**: None (uses only Flutter SDK)

**Usage**:
```bash
flutlock --setup-project --architecture flat
```

### 2. Layered (By Type) Architecture (`layered`)

**Description**: Organized by technical layers: models, views, controllers. Uses GetX for state management and dependency injection.

**Folder Structure**:
```
lib/
├── models/
├── views/
├── controllers/
├── services/
├── repositories/
├── utils/
├── constants/
└── main.dart
```

**Generated Files**:
- `lib/main.dart` - GetX-enabled Flutter app
- `lib/models/user_model.dart` - User model with GetX
- `lib/views/home_view.dart` - Home view with GetX
- `lib/controllers/home_controller.dart` - GetX controller
- `lib/services/user_service.dart` - User service
- `lib/repositories/user_repository.dart` - Data repository
- `lib/utils/app_utils.dart` - Utility functions
- `lib/constants/app_constants.dart` - App constants

**Dependencies**: 
- `get: ^4.6.6` - State management and dependency injection

**Usage**:
```bash
flutlock --setup-project --architecture layered
```

### 3. Feature-First (Vertical) Architecture (`feature`)

**Description**: Organized by features with vertical slicing. Each feature contains its own models, views, and controllers.

**Folder Structure**:
```
lib/
├── core/
│   ├── constants/
│   ├── utils/
│   └── services/
├── shared/
│   ├── widgets/
│   └── models/
├── features/
│   ├── auth/
│   │   ├── models/
│   │   ├── views/
│   │   ├── controllers/
│   │   └── services/
│   ├── home/
│   │   ├── models/
│   │   ├── views/
│   │   ├── controllers/
│   │   └── services/
│   └── profile/
│       ├── models/
│       ├── views/
│       ├── controllers/
│       └── services/
└── main.dart
```

**Generated Files**:
- `lib/main.dart` - Provider-enabled Flutter app
- `lib/core/constants/app_constants.dart` - Core constants
- `lib/core/utils/app_utils.dart` - Core utilities
- `lib/core/services/api_service.dart` - Core API service
- `lib/shared/widgets/custom_button.dart` - Shared widgets
- `lib/shared/models/base_model.dart` - Base model class
- `lib/features/auth/views/login_view.dart` - Login view
- `lib/features/home/views/home_view.dart` - Home view
- `lib/features/profile/views/profile_view.dart` - Profile view

**Dependencies**:
- `provider: ^6.1.1` - State management
- `http: ^1.1.0` - HTTP client

**Usage**:
```bash
flutlock --setup-project --architecture feature
```

### 4. BLoC-Based Architecture (`bloc`)

**Description**: Business Logic Component pattern with state management using flutter_bloc.

**Status**: 🚧 Coming Soon - Structure defined, templates in development

**Dependencies**:
- `flutter_bloc: ^8.1.3`
- `bloc: ^8.1.2`
- `equatable: ^2.0.5`

### 5. MVVM (Model-View-ViewModel) (`mvvm`)

**Description**: Model-View-ViewModel pattern with Provider for state management.

**Status**: 🚧 Coming Soon - Structure defined, templates in development

**Dependencies**:
- `provider: ^6.1.1`
- `get_it: ^7.6.4`

### 6. Clean Architecture (`clean`)

**Description**: Domain-driven design with clear layer separation (domain, data, presentation).

**Status**: 🚧 Coming Soon - Structure defined, templates in development

**Dependencies**:
- `dartz: ^0.10.1`
- `injectable: ^2.3.2`
- `get_it: ^7.6.4`

### 7. Redux-Style (Flutter_Redux) (`redux`)

**Description**: Redux pattern with actions, reducers, and store using flutter_redux.

**Status**: 🚧 Coming Soon - Structure defined, templates in development

**Dependencies**:
- `flutter_redux: ^0.10.0`
- `redux: ^5.0.0`

## Usage Examples

### List Available Architectures

```bash
flutlock --list-architectures
```

Output:
```
📐 Available Flutter Architecture Patterns:

  flat     - Flat/Simple Structure
    Basic lib/ organization with minimal folder structure
    Folders: 5, Files: 6

  layered  - Layered (By Type) Architecture
    Organized by technical layers: models, views, controllers
    Dependencies: get
    Folders: 7, Files: 8

  feature  - Feature-First (Vertical) Architecture
    Organized by features with vertical slicing
    Dependencies: provider, http
    Folders: 14, Files: 9

  bloc     - BLoC-Based Architecture
    Business Logic Component pattern with state management
    Folders: 0, Files: 0

  mvvm     - MVVM (Model-View-ViewModel)
    Model-View-ViewModel pattern with Provider
    Folders: 0, Files: 0

  clean    - Clean Architecture
    Domain-driven design with clear layer separation
    Folders: 0, Files: 0

  redux    - Redux-Style (Flutter_Redux)
    Redux pattern with actions, reducers, and store
    Folders: 0, Files: 0

Usage:
  flutlock --setup-project --architecture <name>
  flutlock --setup-project --architecture clean
```

### Generate Architecture with Project Setup

```bash
# Generate flat architecture
flutlock --setup-project --architecture flat

# Generate layered architecture with GetX
flutlock --setup-project --architecture layered

# Generate feature-first architecture with Provider
flutlock --setup-project --architecture feature
```

### Interactive Architecture Selection

```bash
# Will prompt for architecture selection
flutlock --setup-project --architecture
```

## Features

### Automatic Dependency Management

FlutLock automatically adds architecture-specific dependencies to your `pubspec.yaml` file:

- **Version Management**: Uses predefined, tested versions for all dependencies
- **Conflict Resolution**: Skips dependencies that already exist
- **Automatic Installation**: Runs `flutter pub get` after updating dependencies

### Template System

Each architecture pattern includes:

- **Folder Structure**: Complete directory hierarchy
- **Boilerplate Files**: Ready-to-use Dart files with proper imports
- **Variable Substitution**: Project name and package name automatically inserted
- **Best Practices**: Code follows Flutter and Dart best practices

### Safety Features

- **Dry Run Mode**: Preview changes without making them (`--dry-run`)
- **Force Overwrite**: Overwrite existing files when needed (`--force`)
- **Error Handling**: Comprehensive error reporting and recovery

## Best Practices

### Choosing an Architecture

- **Flat**: Small projects, prototypes, learning Flutter
- **Layered**: Medium projects with clear separation of concerns
- **Feature-First**: Large projects with multiple features
- **BLoC**: Projects requiring complex state management
- **MVVM**: Projects with heavy business logic
- **Clean**: Enterprise applications with strict architectural requirements
- **Redux**: Projects requiring predictable state management

### Project Structure Guidelines

1. **Keep features isolated**: Each feature should be self-contained
2. **Use consistent naming**: Follow Dart naming conventions
3. **Separate concerns**: Keep business logic separate from UI
4. **Test everything**: Write tests for all layers
5. **Document decisions**: Use README files in feature folders

## Contributing

To add new architecture patterns:

1. Define the pattern in `lib/src/core/architecture_definition.dart`
2. Create file templates with proper variable substitution
3. Add dependencies to the pattern definition
4. Write comprehensive tests
5. Update documentation

For more information, see the [Contributing Guide](../CONTRIBUTING.md).
