#!/usr/bin/env dart

/// FlutLock - Main executable entry point
///
/// This is the main entry point for the FlutLock Dart implementation.
/// It provides the same CLI interface as the Python version for backward compatibility.

import 'dart:io';
import 'package:flutlock/flutlock.dart';

Future<void> main(List<String> arguments) async {
  // Handle version check directly
  if (arguments.length == 1 &&
      (arguments[0] == '--version' || arguments[0] == '-v')) {
    print('FlutLock v1.0.0');
    exit(0);
  }

  try {
    final cli = FlutLockCLI();
    final exitCode = await cli.run(arguments);
    exit(exitCode);
  } catch (e, stackTrace) {
    stderr.writeln('Fatal error: $e');
    if (arguments.contains('--verbose') || arguments.contains('-v')) {
      stderr.writeln('Stack trace: $stackTrace');
    }
    exit(1);
  }
}
