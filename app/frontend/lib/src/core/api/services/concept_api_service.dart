import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/concept_models.dart';
import 'base_api_service.dart';

class ConceptApiService extends BaseApiService {
  ConceptApiService(super.apiClient);

  Future<ApiResponse<List<ConceptDto>>> getConcepts({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/concepts',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final concepts = asMapList(
        extractList(response),
        context: 'concepts',
      ).map(ConceptDto.fromJson).toList();
      return success(concepts);
    } catch (error) {
      return failure<List<ConceptDto>>(
        'Failed to load concepts: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<ConceptDto>>> searchConcepts(
    String name, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/concepts/search',
        queryParameters: {'name': name, 'skip': skip, 'limit': limit},
      );
      final concepts = asMapList(
        extractList(response),
        context: 'concepts',
      ).map(ConceptDto.fromJson).toList();
      return success(concepts);
    } catch (error) {
      return failure<List<ConceptDto>>(
        'Failed to search concepts: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<ConceptDto>> getConcept(String id) async {
    try {
      final response = await apiClient.get(
        '/api/concepts/${encodePathSegment(id)}',
      );
      final concept = ConceptDto.fromJson(asMapFromResponse(response));
      return success(concept);
    } catch (error) {
      return failure<ConceptDto>(
        'Failed to load concept: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<ConceptDto>> createConcept(
    CreateConceptRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/concepts',
        data: request.toJson(),
      );
      final concept = ConceptDto.fromJson(asMapFromResponse(response));
      return success(concept);
    } catch (error) {
      return failure<ConceptDto>(
        'Failed to create concept: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<ConceptDto>> updateConcept(
    String id,
    UpdateConceptRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/concepts/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final concept = ConceptDto.fromJson(asMapFromResponse(response));
      return success(concept);
    } catch (error) {
      return failure<ConceptDto>(
        'Failed to update concept: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteConcept(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/concepts/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete concept: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<ConceptDto>> addSectionToConcept(
    String conceptId,
    AddSectionToConceptRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/concepts/${encodePathSegment(conceptId)}/sections',
        data: request.toJson(),
      );
      final concept = ConceptDto.fromJson(asMapFromResponse(response));
      return success(concept);
    } catch (error) {
      return failure<ConceptDto>(
        'Failed to link section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<ConceptDto>> removeSectionFromConcept(
    String conceptId,
    String sectionId,
  ) async {
    try {
      final response = await apiClient.delete(
        '/api/concepts/${encodePathSegment(conceptId)}/sections/${encodePathSegment(sectionId)}',
      );
      final concept = ConceptDto.fromJson(asMapFromResponse(response));
      return success(concept);
    } catch (error) {
      return failure<ConceptDto>(
        'Failed to unlink section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
