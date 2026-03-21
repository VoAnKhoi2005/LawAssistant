import 'package:flutter/material.dart';
import 'src/core/app.dart';
import 'src/core/di/service_locator.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Setup dependency injection
  setupDependencyInjection();
  
  runApp(const App());
}
