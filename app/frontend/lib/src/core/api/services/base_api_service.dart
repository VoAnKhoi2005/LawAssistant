import 'package:dio/dio.dart';

import '../models/api_response.dart';
import '../../network/api_client.dart';

abstract class BaseApiService {
  BaseApiService(this.apiClient);

  final ApiClient apiClient;

  Map<String, dynamic> _unwrapBody(Response<dynamic> response) {
    final body = response.data;
    if (body is Map<String, dynamic>) {
      final success = body['success'];
      if (success is bool && !success) {
        final message = body['message']?.toString() ?? 'Request failed';
        throw ApiException(message);
      }
      return body;
    }
    throw ApiException('Unexpected response format: ${body.runtimeType}');
  }

  dynamic extractData(Response<dynamic> response) {
    final body = _unwrapBody(response);
    return body['data'];
  }

  List<dynamic> extractList(Response<dynamic> response) {
    final data = extractData(response);
    if (data is List<dynamic>) {
      return data;
    }
    throw ApiException('Expected list payload but got ${data.runtimeType}');
  }

  Map<String, dynamic> extractMap(Response<dynamic> response) {
    final data = extractData(response);
    if (data is Map<String, dynamic>) {
      return data;
    }
    throw ApiException('Expected object payload but got ${data.runtimeType}');
  }

  Map<String, dynamic> asMap(dynamic value, {String context = 'payload'}) {
    if (value is Map<String, dynamic>) {
      return Map<String, dynamic>.from(value);
    }
    if (value is Map) {
      return value.map((key, dynamic val) => MapEntry(key.toString(), val));
    }
    throw ApiException(
      'Expected $context to be a Map but got ${value.runtimeType}',
    );
  }

  Map<String, dynamic> asMapFromResponse(Response<dynamic> response) =>
      extractMap(response);

  List<Map<String, dynamic>> asMapList(
    List<dynamic> data, {
    String context = 'payload list',
  }) {
    return data
        .map((item) => asMap(item, context: context))
        .map((map) => Map<String, dynamic>.from(map))
        .toList();
  }

  String resolveError(Object error, String fallback) {
    if (error is ApiException) {
      return error.message;
    }
    return fallback;
  }

  ApiResponse<T> success<T>(T data) => ApiResponse.success(data);

  ApiResponse<T> failure<T>(String message) => ApiResponse.error(message);

  String encodePathSegment(String value) => Uri.encodeComponent(value);
}
