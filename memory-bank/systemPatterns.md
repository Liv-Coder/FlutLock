# System Patterns: FlutLock

## Architecture Overview

FlutLock follows a modular package-based architecture with these components:

- Main entry point module (main.py) orchestrating the overall workflow
- Core modules for specific functional domains (keystore, properties, build, verify)
- Utility modules for shared functionality (commands, config, exceptions)
- Integration modules for external tools (Fastlane, Play Store)
- Clean separation of concerns with well-defined module boundaries

## Key Technical Decisions

- Python as implementation language for cross-platform compatibility
- Package-based organization for better maintainability and testability
- Command-line interface first, with potential for GUI in future versions
- Environment variables as primary method for secure credential passing
- Modular design to enable future integrations (Fastlane, Play Store API)
- Exception hierarchy for structured error handling

## Design Patterns

- Command pattern for executing different build operations
- Strategy pattern for handling different keystore scenarios (new vs. existing)
- Factory pattern for generating different output formats (APK vs. AAB)
- Facade pattern to simplify the complex signing workflow
- Repository pattern for configuration management
- Dependency injection for better testability

## Component Relationships

```
[CLI Interface (main.py)] → [Configuration Manager (config.py)] → [Keystore Handler (keystore.py)]
                                                                ↓
                 [Command Executor (commands.py)] ← [Property File Generator (properties.py)]
                                       ↓
                 [Flutter Build (build.py)] → [Signature Verification (verify.py)]
```

## Module Organization

The code is organized into a hierarchical module structure:

- **flutter_signer**: Main package
  - **core**: Core domain functionality
    - **dependencies.py**: Dependency checking and validation
    - **keystore.py**: Keystore generation and management
    - **properties.py**: key.properties file handling
    - **build.py**: Flutter build command execution
    - **verify.py**: Signature verification
  - **utils**: Helper utilities
    - **commands.py**: Command execution utilities
    - **config.py**: Configuration management
    - **exceptions.py**: Exception hierarchy
  - **integrations**: External tool integrations
    - **fastlane.py**: Fastlane integration (future)
    - **playstore.py**: Play Store API integration (future)
  - **main.py**: Main entry point and CLI handling

## Future Design Considerations

- Plugin architecture for custom build steps
- Integration points with CI/CD systems
- Service layer for cloud keystores
- Adapter pattern for different deployment targets
- Observer pattern for build logging and reporting
