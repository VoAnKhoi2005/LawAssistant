import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/user_models.dart';
import 'base_api_service.dart';

class UserApiService extends BaseApiService {
  UserApiService(super.apiClient);

  Future<ApiResponse<UserDto?>> getCurrentUser() async {
    try {
      final response = await apiClient.get('/api/users/me');
      final data = extractData(response);
      if (data == null) {
        return success<UserDto?>(null);
      }
      return success(UserDto.fromJson(asMap(data)));
    } catch (error) {
      return failure<UserDto?>(
        'Failed to load profile: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
