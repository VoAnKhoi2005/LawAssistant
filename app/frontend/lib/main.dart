import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:window_manager/window_manager.dart';

import 'src/core/app.dart';
import 'src/core/di/service_locator.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await dotenv.load(fileName: '.env');
  } catch (_) {
    // Allow startup without a local .env when values come from --dart-define.
  }

  final isDesktop = !kIsWeb &&
      (defaultTargetPlatform == TargetPlatform.windows ||
          defaultTargetPlatform == TargetPlatform.linux ||
          defaultTargetPlatform == TargetPlatform.macOS);

  if (isDesktop) {
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
