import 'common_models.dart';

class UploadFileDto {
  final ObjectIdModel? id;
  final String userId;
  final String filename;
  final String storagePath;
  final String? contentType;
  final int? size;
  final String status;
  final String? error;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UploadFileDto({
    this.id,
    required this.userId,
    required this.filename,
    required this.storagePath,
    this.contentType,
    this.size,
    required this.status,
    this.error,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UploadFileDto.fromJson(Map<String, dynamic> json) {
    return UploadFileDto(
      id: ObjectIdModel.maybeFromJson(json['_id']),
      userId: json['user_id'] as String? ?? '',
      filename: json['filename'] as String? ?? '',
      storagePath: json['storage_path'] as String? ?? '',
      contentType: json['content_type'] as String?,
      size: (json['size'] as num?)?.toInt(),
      status: json['status'] as String? ?? 'uploaded',
      error: json['error'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'].toString())
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'].toString())
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'user_id': userId,
      'filename': filename,
      'storage_path': storagePath,
      'content_type': contentType,
      'size': size,
      'status': status,
      'error': error,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
    if (includeId && id != null) {
      map['_id'] = id!.toJson();
    }
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class UpdateFileStatusRequest {
  final String status;
  final String? error;

  const UpdateFileStatusRequest({required this.status, this.error});

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{'status': status};
    if (error != null) {
      map['error'] = error;
    }
    return map;
  }
}

class FileListResponse {
  final List<UploadFileDto> files;
  final int total;
  final int skip;
  final int limit;

  const FileListResponse({
    required this.files,
    required this.total,
    required this.skip,
    required this.limit,
  });

  factory FileListResponse.fromJson(Map<String, dynamic> json) {
    return FileListResponse(
      files: (json['files'] as List<dynamic>? ?? const [])
          .map((item) =>
              UploadFileDto.fromJson(Map<String, dynamic>.from(item as Map)))
          .toList(),
      total: (json['total'] as num?)?.toInt() ?? 0,
      skip: (json['skip'] as num?)?.toInt() ?? 0,
      limit: (json['limit'] as num?)?.toInt() ?? 0,
    );
  }
}
