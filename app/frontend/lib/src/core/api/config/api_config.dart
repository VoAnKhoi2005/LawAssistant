import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  static String get baseUrl {
    final envValue = dotenv.env['API_BASE_URL'];
    if (envValue != null && envValue.isNotEmpty) {
      return envValue;
    }

    return const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000',
    );
  }

  static int get timeoutSeconds {
    final envValue = dotenv.env['API_TIMEOUT'];
    final timeoutMs = int.tryParse(envValue ?? '');
    if (timeoutMs != null && timeoutMs > 0) {
      return (timeoutMs / 1000).ceil();
    }

    return 30;
  }

  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
}
