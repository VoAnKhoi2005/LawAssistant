import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/triplet_models.dart';
import 'base_api_service.dart';

class TripletApiService extends BaseApiService {
  TripletApiService(super.apiClient);

  Future<ApiResponse<List<TripletDto>>> getTriplets({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/triplets',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final triplets = asMapList(
        extractList(response),
        context: 'triplets',
      ).map(TripletDto.fromJson).toList();
      return success(triplets);
    } catch (error) {
      return failure<List<TripletDto>>(
        'Failed to load triplets: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<TripletDto>>> getTripletsBySubject(
    String subjectId, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/triplets/by-subject/${encodePathSegment(subjectId)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final triplets = asMapList(
        extractList(response),
        context: 'triplets',
      ).map(TripletDto.fromJson).toList();
      return success(triplets);
    } catch (error) {
      return failure<List<TripletDto>>(
        'Failed to load triplets: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<TripletDto>>> getTripletsByObject(
    String objectId, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/triplets/by-object/${encodePathSegment(objectId)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final triplets = asMapList(
        extractList(response),
        context: 'triplets',
      ).map(TripletDto.fromJson).toList();
      return success(triplets);
    } catch (error) {
      return failure<List<TripletDto>>(
        'Failed to load triplets: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<TripletDto>> getTriplet(String id) async {
    try {
      final response = await apiClient.get(
        '/api/triplets/${encodePathSegment(id)}',
      );
      final triplet = TripletDto.fromJson(asMapFromResponse(response));
      return success(triplet);
    } catch (error) {
      return failure<TripletDto>(
        'Failed to load triplet: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<TripletDto>> createTriplet(
    CreateTripletRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/triplets',
        data: request.toJson(),
      );
      final triplet = TripletDto.fromJson(asMapFromResponse(response));
      return success(triplet);
    } catch (error) {
      return failure<TripletDto>(
        'Failed to create triplet: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<TripletDto>> updateTriplet(
    String id,
    UpdateTripletRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/triplets/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final triplet = TripletDto.fromJson(asMapFromResponse(response));
      return success(triplet);
    } catch (error) {
      return failure<TripletDto>(
        'Failed to update triplet: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteTriplet(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/triplets/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete triplet: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<TripletDto>> addSectionToTriplet(
    String tripletId,
    AddSectionToTripletRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/triplets/${encodePathSegment(tripletId)}/sections',
        data: request.toJson(),
      );
      final triplet = TripletDto.fromJson(asMapFromResponse(response));
      return success(triplet);
    } catch (error) {
      return failure<TripletDto>(
        'Failed to link section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<TripletDto>> removeSectionFromTriplet(
    String tripletId,
    String sectionId,
  ) async {
    try {
      final response = await apiClient.delete(
        '/api/triplets/${encodePathSegment(tripletId)}/sections/${encodePathSegment(sectionId)}',
      );
      final triplet = TripletDto.fromJson(asMapFromResponse(response));
      return success(triplet);
    } catch (error) {
      return failure<TripletDto>(
        'Failed to unlink section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
