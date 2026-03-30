import 'dart:io';

import 'package:flutter/material.dart';
import 'package:window_manager/window_manager.dart';

import 'src/core/app.dart';
import 'src/core/di/service_locator.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    await windowManager.ensureInitialized();
    const minSize = Size(1200, 768);
    await windowManager.setMinimumSize(minSize);
    await windowManager.waitUntilReadyToShow(
      const WindowOptions(minimumSize: minSize),
      () async {
        await windowManager.show();
        await windowManager.focus();
      },
    );
  }

  // Setup dependency injection
  setupDependencyInjection();

  runApp(const App());
}
