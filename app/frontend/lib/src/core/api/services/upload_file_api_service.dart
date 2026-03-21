import 'package:dio/dio.dart';
import 'package:law_assistant_kg/src/core/api/models/api_response.dart';

import '../models/upload_file_models.dart';
import 'base_api_service.dart';

class UploadFileApiService extends BaseApiService {
  UploadFileApiService(super.apiClient);

  Future<ApiResponse<List<UploadFileDto>>> getFiles({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/upload-files',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final files = asMapList(
        extractList(response),
        context: 'files',
      ).map(UploadFileDto.fromJson).toList();
      return success(files);
    } catch (error) {
      return failure<List<UploadFileDto>>(
        'Failed to load files: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<UploadFileDto>> getFileById(String id) async {
    try {
      final response = await apiClient.get(
        '/api/upload-files/${encodePathSegment(id)}',
      );
      final file = UploadFileDto.fromJson(asMapFromResponse(response));
      return success(file);
    } catch (error) {
      return failure<UploadFileDto>(
        'Failed to load file: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<UploadFileDto>>> getMyFiles({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/upload-files/user/me',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final files = asMapList(
        extractList(response),
        context: 'files',
      ).map(UploadFileDto.fromJson).toList();
      return success(files);
    } catch (error) {
      return failure<List<UploadFileDto>>(
        'Failed to load files: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<List<UploadFileDto>>> getFilesByStatus(
    String status, {
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await apiClient.get(
        '/api/upload-files/status/${encodePathSegment(status)}',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      final files = asMapList(
        extractList(response),
        context: 'files',
      ).map(UploadFileDto.fromJson).toList();
      return success(files);
    } catch (error) {
      return failure<List<UploadFileDto>>(
        'Failed to load files: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<UploadFileDto>> uploadFile(
    String filePath,
    String filename,
  ) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: filename),
      });
      final response = await apiClient.post(
        '/api/upload-files/upload',
        data: formData,
      );
      final file = UploadFileDto.fromJson(asMapFromResponse(response));
      return success(file);
    } catch (error) {
      return failure<UploadFileDto>(
        'Failed to upload file: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<Map<String, dynamic>>> uploadMultipleFiles(
    List<String> filePaths,
  ) async {
    try {
      final files = <MultipartFile>[];
      for (final path in filePaths) {
        files.add(await MultipartFile.fromFile(path));
      }
      final formData = FormData.fromMap({'files': files});
      final response = await apiClient.post(
        '/api/upload-files/upload-multiple',
        data: formData,
      );
      return success(asMapFromResponse(response));
    } catch (error) {
      return failure<Map<String, dynamic>>(
        'Failed to upload files: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<UploadFileDto>> updateFileStatus(
    String fileId,
    UpdateFileStatusRequest request,
  ) async {
    try {
      final response = await apiClient.put(
        '/api/upload-files/${encodePathSegment(fileId)}/status',
        data: request.toJson(),
      );
      final file = UploadFileDto.fromJson(asMapFromResponse(response));
      return success(file);
    } catch (error) {
      return failure<UploadFileDto>(
        'Failed to update file status: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<void>> downloadFile(String fileId) async {
    try {
      final response = await apiClient.get(
        '/api/upload-files/${encodePathSegment(fileId)}/download',
        options: Options(responseType: ResponseType.bytes),
      );
      return success(null);
    } catch (error) {
      return failure<void>(
        'Failed to download file: ${resolveError(error, 'unexpected error')}',
      );
    }
  }

  Future<ApiResponse<bool>> deleteFile(String fileId) async {
    try {
      final response = await apiClient.delete(
        '/api/upload-files/${encodePathSegment(fileId)}',
      );
      final result = extractData(response);
      final deleted = result is bool ? result : true;
      return success(deleted);
    } catch (error) {
      return failure<bool>(
        'Failed to delete file: ${resolveError(error, 'unexpected error')}',
      );
    }
  }
}
