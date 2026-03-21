import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/section_relation_models.dart';
import 'base_api_service.dart';

class SectionRelationApiService extends BaseApiService {
  SectionRelationApiService(super.apiClient);

  Future<ApiResponse<List<SectionRelationDto>>> getSectionRelations({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/section-relations',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'section_relations',
      ).map(SectionRelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<SectionRelationDto>>(
        'Failed to load section relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<SectionRelationDto>>> getSectionRelationsBySource(
    String source, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/section-relations/by-source/${encodePathSegment(source)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'section_relations',
      ).map(SectionRelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<SectionRelationDto>>(
        'Failed to load section relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<SectionRelationDto>>> getSectionRelationsByTarget(
    String target, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/section-relations/by-target/${encodePathSegment(target)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'section_relations',
      ).map(SectionRelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<SectionRelationDto>>(
        'Failed to load section relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<SectionRelationDto>>> getSectionRelationsByType(
    String type, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/section-relations/by-type/${encodePathSegment(type)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'section_relations',
      ).map(SectionRelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<SectionRelationDto>>(
        'Failed to load section relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<SectionRelationDto>> getSectionRelation(String id) async {
    try {
      final response = await apiClient.get(
        '/api/section-relations/${encodePathSegment(id)}',
      );
      final relation = SectionRelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<SectionRelationDto>(
        'Failed to load section relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<SectionRelationDto>> createSectionRelation(
    CreateSectionRelationRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/section-relations',
        data: request.toJson(),
      );
      final relation = SectionRelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<SectionRelationDto>(
        'Failed to create section relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<SectionRelationDto>> updateSectionRelation(
    String id,
    UpdateSectionRelationRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/section-relations/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final relation = SectionRelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<SectionRelationDto>(
        'Failed to update section relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteSectionRelation(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/section-relations/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete section relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
