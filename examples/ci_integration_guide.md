# FlutLock CI/CD Integration Guide

This guide explains how to integrate FlutLock into various CI/CD systems to automate your Flutter app signing process.

## General Principles

For any CI/CD system, you'll need to:

1. Make sure the necessary dependencies are available:

   - Python 3.6+
   - Flutter SDK
   - JDK
   - Android SDK (for signature verification)

2. Securely store your keystore credentials
3. Make FlutLock available in your build environment
4. Run FlutLock with appropriate environment variables/arguments

## GitHub Actions

```yaml
name: Build and Sign Flutter App

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          distribution: "temurin"
          java-version: "11"

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.x"

      - name: Get FlutLock
        run: |
          git clone https://github.com/yourusername/flutlock.git

      - name: Build and Sign Flutter App
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
          STORE_ALIAS: upload
        run: |
          python flutlock/sign_flutter_app.py --path . --build-type appbundle --verify
```

## GitLab CI

```yaml
stages:
  - build

flutter_build:
  stage: build
  image: cirrusci/flutter:latest
  before_script:
    - apt-get update -qq && apt-get install -y -qq python3 python3-pip openjdk-11-jdk
    - git clone https://github.com/yourusername/flutlock.git
  script:
    - python3 flutlock/sign_flutter_app.py --path . --build-type appbundle --verify
  variables:
    KEYSTORE_PASSWORD: ${KEYSTORE_PASSWORD}
    KEY_PASSWORD: ${KEY_PASSWORD}
    STORE_ALIAS: upload
```

## Jenkins

```groovy
pipeline {
    agent any

    environment {
        KEYSTORE_PASSWORD = credentials('keystore-password')
        KEY_PASSWORD = credentials('key-password')
        STORE_ALIAS = 'upload'
    }

    stages {
        stage('Clone FlutLock') {
            steps {
                sh 'git clone https://github.com/yourusername/flutlock.git'
            }
        }

        stage('Build and Sign') {
            steps {
                sh 'python flutlock/sign_flutter_app.py --path . --build-type appbundle --verify'
            }
        }
    }
}
```

## Azure DevOps

```yaml
trigger:
  - main

pool:
  vmImage: "ubuntu-latest"

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: "3.9"

  - task: FlutterInstall@0
    inputs:
      channel: "stable"
      version: "latest"

  - script: |
      git clone https://github.com/yourusername/flutlock.git
    displayName: "Clone FlutLock"

  - script: |
      python flutlock/sign_flutter_app.py --path . --build-type appbundle --verify
    displayName: "Build and Sign Flutter App"
    env:
      KEYSTORE_PASSWORD: $(keystorePassword)
      KEY_PASSWORD: $(keyPassword)
      STORE_ALIAS: upload
```

## CircleCI

```yaml
version: 2.1
jobs:
  build:
    docker:
      - image: cirrusci/flutter:latest
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            apt-get update
            apt-get install -y python3 python3-pip openjdk-11-jdk
      - run:
          name: Clone FlutLock
          command: |
            git clone https://github.com/yourusername/flutlock.git
      - run:
          name: Build and Sign Flutter App
          command: |
            python3 flutlock/sign_flutter_app.py --path . --build-type appbundle --verify
          environment:
            KEYSTORE_PASSWORD: ${KEYSTORE_PASSWORD}
            KEY_PASSWORD: ${KEY_PASSWORD}
            STORE_ALIAS: upload
```

## Security Considerations

- **Never** commit keystores or passwords to your repository
- Use your CI/CD platform's secret/environment variable management:
  - GitHub: Secrets in repository settings
  - GitLab: CI/CD Variables
  - Jenkins: Credentials plugin
  - Azure DevOps: Pipeline variables/secrets
  - CircleCI: Environment variables
- Consider using a dedicated keystore for CI/CD builds
- For production apps, consider more advanced security measures like hardware security modules or cloud key management services
