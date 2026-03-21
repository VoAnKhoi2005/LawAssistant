import 'package:dio/dio.dart';
import '../api/config/api_config.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic responseData;

  ApiException(this.message, {this.statusCode, this.responseData});

  @override
  String toString() => message;
}

class ApiClient {
  late final Dio _dio;
  String? _authToken;

  ApiClient({String? baseUrl}) {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? ApiConfig.baseUrl,
        connectTimeout: Duration(seconds: ApiConfig.timeoutSeconds),
        receiveTimeout: Duration(seconds: ApiConfig.timeoutSeconds),
        headers: ApiConfig.defaultHeaders,
        validateStatus: (status) => status != null && status < 500,
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (_authToken != null) {
            options.headers['Authorization'] = 'Bearer $_authToken';
          }
          return handler.next(options);
        },
        onError: (error, handler) {
          final apiException = _handleError(error);
          return handler.reject(
            DioException(
              requestOptions: error.requestOptions,
              error: apiException,
              response: error.response,
              type: error.type,
            ),
          );
        },
      ),
    );
  }

  void updateAuthToken(String? token) {
    _authToken = token;
  }

  String? get authToken => _authToken;

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      _validateResponse(response);
      return response;
    } on DioException catch (e) {
      throw e.error ?? _handleError(e);
    }
  }

  Future<Response<dynamic>> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      _validateResponse(response);
      return response;
    } on DioException catch (e) {
      throw e.error ?? _handleError(e);
    }
  }

  Future<Response<dynamic>> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      _validateResponse(response);
      return response;
    } on DioException catch (e) {
      throw e.error ?? _handleError(e);
    }
  }

  Future<Response<dynamic>> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      _validateResponse(response);
      return response;
    } on DioException catch (e) {
      throw e.error ?? _handleError(e);
    }
  }

  Future<Response<dynamic>> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      _validateResponse(response);
      return response;
    } on DioException catch (e) {
      throw e.error ?? _handleError(e);
    }
  }

  void _validateResponse(Response<dynamic> response) {
    final statusCode = response.statusCode;
    
    if (statusCode == null) {
      throw ApiException('No status code received');
    }

    if (statusCode >= 400) {
      final data = response.data;
      String message = 'Request failed with status code $statusCode';
      
      if (data is Map<String, dynamic>) {
        message = data['message']?.toString() ?? message;
        final success = data['success'];
        if (success is bool && !success) {
          throw ApiException(
            message,
            statusCode: statusCode,
            responseData: data,
          );
        }
      }
      
      throw ApiException(
        message,
        statusCode: statusCode,
        responseData: data,
      );
    }
  }

  ApiException _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException('Connection timeout. Please try again.');
      
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final data = error.response?.data;
        
        String message = 'Request failed';
        if (data is Map<String, dynamic>) {
          message = data['message']?.toString() ?? message;
        }
        
        return ApiException(
          message,
          statusCode: statusCode,
          responseData: data,
        );
      
      case DioExceptionType.cancel:
        return ApiException('Request cancelled');
      
      case DioExceptionType.connectionError:
        return ApiException(
          'Network error. Please check your connection.',
        );
      
      case DioExceptionType.badCertificate:
        return ApiException('Certificate validation failed');
      
      case DioExceptionType.unknown:
        if (error.error != null) {
          return ApiException('Network error: ${error.error}');
        }
        return ApiException('An unexpected error occurred');
    }
  }

  Dio get dio => _dio;
}
