import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/document_models.dart';
import 'base_api_service.dart';

class DocumentApiService extends BaseApiService {
  DocumentApiService(super.apiClient);

  Future<ApiResponse<List<DocumentDto>>> getDocuments({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/documents',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final documents = asMapList(
        extractList(response),
        context: 'documents',
      ).map(DocumentDto.fromJson).toList();
      return success(documents);
    } catch (error) {
      return failure<List<DocumentDto>>(
        'Failed to load documents: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<DocumentDto>> getDocumentById(String id) async {
    try {
      final response = await apiClient.get(
        '/api/documents/${encodePathSegment(id)}',
      );
      final document = DocumentDto.fromJson(asMapFromResponse(response));
      return success(document);
    } catch (error) {
      return failure<DocumentDto>(
        'Failed to load document: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<DocumentDto>> getDocumentBySoHieu(String soHieu) async {
    try {
      final response = await apiClient.get(
        '/api/documents/by-so-hieu/${encodePathSegment(soHieu)}',
      );
      final document = DocumentDto.fromJson(asMapFromResponse(response));
      return success(document);
    } catch (error) {
      return failure<DocumentDto>(
        'Failed to load document: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<DocumentDto>> createDocument(
    CreateDocumentRequest request,
  ) async {
    try {
      final response = await apiClient.post(
        '/api/documents',
        data: request.toJson(),
      );
      final document = DocumentDto.fromJson(asMapFromResponse(response));
      return success(document);
    } catch (error) {
      return failure<DocumentDto>(
        'Failed to create document: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<DocumentDto>> updateDocument(
    String id,
    UpdateDocumentRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/documents/${encodePathSegment(id)}',
        data: request.toJson(),
      );
      final document = DocumentDto.fromJson(asMapFromResponse(response));
      return success(document);
    } catch (error) {
      return failure<DocumentDto>(
        'Failed to update document: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteDocument(String id) async {
    try {
      final response = await apiClient.delete(
        '/api/documents/${encodePathSegment(id)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete document: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
