import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';

import 'di/service_locator.dart';
import 'navigation/app_router.dart';
import '../features/documents/presentation/providers/documents_provider.dart';
import 'api/services/document_api_service.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    final providers = <SingleChildWidget>[
      ChangeNotifierProvider(
        create: (_) => DocumentsProvider(getIt<DocumentApiService>()),
      ),
    ];

    return MultiProvider(providers: providers, child: _buildApp());
  }

  Widget _buildApp() {
    return MaterialApp.router(
      title: 'Law Assistant',
      theme: _buildLightTheme(),
      darkTheme: _buildDarkTheme(),
      themeMode: ThemeMode.light, // Force light mode
      routerConfig: AppRouter.router,
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return _MinimumSizeWrapper(child: child ?? const SizedBox());
      },
    );
  }

  ThemeData _buildLightTheme() {
    return ThemeData(
      colorScheme: const ColorScheme.light(
        primary: Color(0xFF525F71),
        secondary: Color(0xFF48617E),
        tertiary: Color(0xFF7A5A00),
        surface: Color(0xFFFBF8FC),
        error: Color(0xFF9E3F4E),
        onPrimary: Color(0xFFF5F8FF),
        onSecondary: Color(0xFFF7F9FF),
        onSurface: Color(0xFF31323A),
        onError: Color(0xFFFFF7F7),
        primaryContainer: Color(0xFFD6E4F9),
        secondaryContainer: Color(0xFFD1E4FF),
        tertiaryContainer: Color(0xFFF9C13D),
        errorContainer: Color(0xFFFF8B9A),
        surfaceContainerLowest: Color(0xFFFFFFFF),
        surfaceContainerLow: Color(0xFFF5F2F8),
        surfaceContainer: Color(0xFFEFEDF4),
        surfaceContainerHigh: Color(0xFFE9E7F0),
        surfaceContainerHighest: Color(0xFFE3E1EC),
        outline: Color(0xFF7A7A83),
        outlineVariant: Color(0xFFB2B1BB),
      ),
      useMaterial3: true,
      fontFamily: 'Inter',
      textTheme: const TextTheme(
        headlineLarge: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w800),
        headlineMedium: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w700),
        headlineSmall: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w600),
        titleLarge: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w700),
        titleMedium: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w600),
        bodyLarge: TextStyle(fontFamily: 'Inter'),
        bodyMedium: TextStyle(fontFamily: 'Inter'),
        labelLarge: TextStyle(fontFamily: 'Inter', fontWeight: FontWeight.w700),
      ),
    );
  }

  ThemeData _buildDarkTheme() {
    return ThemeData(
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFF525F71),
        secondary: Color(0xFF48617E),
        tertiary: Color(0xFF7A5A00),
        surface: Color(0xFF1A1B1E),
        error: Color(0xFF9E3F4E),
        onPrimary: Color(0xFFF5F8FF),
        onSecondary: Color(0xFFF7F9FF),
        onSurface: Color(0xFFE3E1EC),
      ),
      useMaterial3: true,
      fontFamily: 'Inter',
      textTheme: const TextTheme(
        headlineLarge: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w800),
        headlineMedium: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w700),
        headlineSmall: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w600),
        titleLarge: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w700),
        titleMedium: TextStyle(fontFamily: 'Manrope', fontWeight: FontWeight.w600),
        bodyLarge: TextStyle(fontFamily: 'Inter'),
        bodyMedium: TextStyle(fontFamily: 'Inter'),
        labelLarge: TextStyle(fontFamily: 'Inter', fontWeight: FontWeight.w700),
      ),
    );
  }
}

class _MinimumSizeWrapper extends StatelessWidget {
  final Widget child;
  
  const _MinimumSizeWrapper({required this.child});
  
  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        const minWidth = 1024.0;
        const minHeight = 768.0;
        
        if (constraints.maxWidth < minWidth || constraints.maxHeight < minHeight) {
          return Center(
            child: Container(
              constraints: const BoxConstraints(
                minWidth: minWidth,
                minHeight: minHeight,
              ),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SingleChildScrollView(
                  child: SizedBox(
                    width: minWidth,
                    height: minHeight,
                    child: child,
                  ),
                ),
              ),
            ),
          );
        }
        
        return child;
      },
    );
  }
}
