import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/relation_models.dart';
import 'base_api_service.dart';

class RelationApiService extends BaseApiService {
  RelationApiService(super.apiClient);

  Future<ApiResponse<List<RelationDto>>> getRelations({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/relations',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'relations',
      ).map(RelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<RelationDto>>(
        'Failed to load relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<RelationDto>>> getRelationsByName(
    String name, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/relations/by-name/${encodePathSegment(name)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'relations',
      ).map(RelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<RelationDto>>(
        'Failed to load relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<RelationDto>> getRelation(String id) async {
    try {
      final response = await apiClient.get(
        '/api/relations/${encodePathSegment(id)}',
      );
      final relation = RelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<RelationDto>(
        'Failed to load relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<RelationDto>> createRelation(
    CreateRelationRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/relations',
        data: request.toJson(),
      );
      final relation = RelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<RelationDto>(
        'Failed to create relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<RelationDto>> updateRelation(
    String id,
    UpdateRelationRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/relations/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final relation = RelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<RelationDto>(
        'Failed to update relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteRelation(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/relations/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete relation: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<RelationDto>> addSectionToRelation(
    String relationId,
    AddSectionToRelationRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/relations/${encodePathSegment(relationId)}/sections',
        data: request.toJson(),
      );
      final relation = RelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<RelationDto>(
        'Failed to link section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<RelationDto>> removeSectionFromRelation(
    String relationId,
    String sectionId,
  ) async {
    try {
      final response = await apiClient.delete(
        '/api/relations/${encodePathSegment(relationId)}/sections/${encodePathSegment(sectionId)}',
      );
      final relation = RelationDto.fromJson(asMapFromResponse(response));
      return success(relation);
    } catch (error) {
      return failure<RelationDto>(
        'Failed to unlink section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
