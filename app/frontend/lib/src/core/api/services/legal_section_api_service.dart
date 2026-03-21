import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/concept_models.dart';
import '../models/legal_section_models.dart';
import '../models/relation_models.dart';
import '../models/triplet_models.dart';
import 'base_api_service.dart';

class LegalSectionApiService extends BaseApiService {
  LegalSectionApiService(super.apiClient);

  Future<ApiResponse<List<LegalSectionDto>>> getSections({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final sections = asMapList(
        extractList(response),
        context: 'sections',
      ).map(LegalSectionDto.fromJson).toList();
      return success(sections);
    } catch (error) {
      return failure<List<LegalSectionDto>>(
        'Failed to load sections: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<LegalSectionDto>>> searchSections(
    String title, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/search',
        queryParameters: {'title': title, 'skip': skip, 'limit': limit},
      );
      final sections = asMapList(
        extractList(response),
        context: 'sections',
      ).map(LegalSectionDto.fromJson).toList();
      return success(sections);
    } catch (error) {
      return failure<List<LegalSectionDto>>(
        'Failed to search sections: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<LegalSectionDto>>> getSectionsBySoHieu(
    String soHieu, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/by-so-hieu/${encodePathSegment(soHieu)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final sections = asMapList(
        extractList(response),
        context: 'sections',
      ).map(LegalSectionDto.fromJson).toList();
      return success(sections);
    } catch (error) {
      return failure<List<LegalSectionDto>>(
        'Failed to load sections: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<LegalSectionDto>> getSection(String id) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/${encodePathSegment(id)}',
      );
      final section = LegalSectionDto.fromJson(asMapFromResponse(response));
      return success(section);
    } catch (error) {
      return failure<LegalSectionDto>(
        'Failed to load section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<LegalSectionDto>> createSection(
    CreateLegalSectionRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/legal-sections',
        data: request.toJson(),
      );
      final section = LegalSectionDto.fromJson(asMapFromResponse(response));
      return success(section);
    } catch (error) {
      return failure<LegalSectionDto>(
        'Failed to create section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<LegalSectionDto>> updateSection(
    String id,
    UpdateLegalSectionRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/legal-sections/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final section = LegalSectionDto.fromJson(asMapFromResponse(response));
      return success(section);
    } catch (error) {
      return failure<LegalSectionDto>(
        'Failed to update section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteSection(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/legal-sections/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete section: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<ConceptDto>>> getSectionConcepts(
    String sectionId, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/${encodePathSegment(sectionId)}/concepts',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final concepts = asMapList(
        extractList(response),
        context: 'concepts',
      ).map(ConceptDto.fromJson).toList();
      return success(concepts);
    } catch (error) {
      return failure<List<ConceptDto>>(
        'Failed to load section concepts: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<RelationDto>>> getSectionRelations(
    String sectionId, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/${encodePathSegment(sectionId)}/relations',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final relations = asMapList(
        extractList(response),
        context: 'relations',
      ).map(RelationDto.fromJson).toList();
      return success(relations);
    } catch (error) {
      return failure<List<RelationDto>>(
        'Failed to load section relations: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<TripletDto>>> getSectionTriplets(
    String sectionId, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/legal-sections/${encodePathSegment(sectionId)}/triplets',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final triplets = asMapList(
        extractList(response),
        context: 'triplets',
      ).map(TripletDto.fromJson).toList();
      return success(triplets);
    } catch (error) {
      return failure<List<TripletDto>>(
        'Failed to load section triplets: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
