import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/auth_models.dart';
import 'base_api_service.dart';

class AuthApiService extends BaseApiService {
  AuthApiService(super.apiClient);

  Future<ApiResponse<AuthSession>> register(RegisterRequest request) async {
    try {
      final response = await apiClient.post(
        '/api/auth/register',
        data: request.toJson(),
      );
      final session = AuthSession.fromJson(asMapFromResponse(response));
      _applyToken(session);
      return success(session);
    } catch (error) {
      return failure<AuthSession>(
        'Registration failed: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<AuthSession>> login(LoginRequest request) async {
    try {
      final response = await apiClient.post(
        '/api/auth/login',
        data: request.toJson(),
      );
      final session = AuthSession.fromJson(asMapFromResponse(response));
      _applyToken(session);
      return success(session);
    } catch (error) {
      return failure<AuthSession>(
        'Login failed: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<AuthSession>> refreshToken(
    RefreshTokenRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/auth/refresh',
        data: request.toJson(),
      );
      final session = AuthSession.fromJson(asMapFromResponse(response));
      _applyToken(session);
      return success(session);
    } catch (error) {
      return failure<AuthSession>(
        'Token refresh failed: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> logout() async {
    try {
      final response = await apiClient.post('/api/auth/logout');
      apiClient.updateAuthToken(null);
      extractData(response);
      return success(true);
    } catch (error) {
      return failure<bool>(
        'Logout failed: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  void _applyToken(AuthSession session) {
    apiClient.updateAuthToken(session.tokens.accessToken);
  }
}
