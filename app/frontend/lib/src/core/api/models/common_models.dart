class ObjectIdModel {
  final String value;

  const ObjectIdModel(this.value);

  factory ObjectIdModel.fromJson(dynamic json) {
    if (json is ObjectIdModel) {
      return json;
    }
    if (json is String) {
      return ObjectIdModel(json);
    }
    if (json is Map<String, dynamic>) {
      final raw = json[r'$oid'] ?? json['oid'] ?? json['_id'];
      if (raw is String) {
        return ObjectIdModel(raw);
      }
    }
    throw const FormatException('Invalid ObjectId representation');
  }

  static ObjectIdModel? maybeFromJson(dynamic json) {
    if (json == null) {
      return null;
    }
    return ObjectIdModel.fromJson(json);
  }

  Map<String, dynamic> toJson() => {r'$oid': value};

  String get hexString => value;

  @override
  String toString() => value;
}

class DateModel {
  final DateTime value;

  const DateModel(this.value);

  factory DateModel.fromJson(dynamic json) {
    if (json is DateModel) {
      return json;
    }
    if (json is DateTime) {
      return DateModel(json);
    }
    if (json is String) {
      return DateModel(DateTime.parse(json));
    }
    if (json is int) {
      return DateModel(DateTime.fromMillisecondsSinceEpoch(json));
    }
    if (json is Map<String, dynamic>) {
      final raw = json[r'$date'] ?? json['date'];
      if (raw is String) {
        return DateModel(DateTime.parse(raw));
      }
      if (raw is int) {
        return DateModel(DateTime.fromMillisecondsSinceEpoch(raw));
      }
    }
    throw const FormatException('Invalid date representation');
  }

  Map<String, dynamic> toJson() => {r'$date': value.toUtc().toIso8601String()};

  DateTime get dateTime => value;
}

class DocumentRef {
  final String sectionId;
  final String soHieu;

  const DocumentRef({required this.sectionId, required this.soHieu});

  factory DocumentRef.fromJson(Map<String, dynamic> json) {
    final section =
        json['section_id'] ?? json['sectionId'] ?? json['sectionID'];
    final soHieuValue = json['so_hieu'] ?? json['soHieu'];
    if (section is! String || soHieuValue is! String) {
      throw const FormatException('Invalid document reference payload');
    }
    return DocumentRef(sectionId: section, soHieu: soHieuValue);
  }

  static List<DocumentRef> listFromJson(dynamic value) {
    if (value == null) {
      return <DocumentRef>[];
    }
    if (value is List) {
      return value
          .map(
            (item) =>
                DocumentRef.fromJson(Map<String, dynamic>.from(item as Map)),
          )
          .toList();
    }
    throw const FormatException('Invalid document reference list');
  }

  Map<String, dynamic> toJson() => {'section_id': sectionId, 'so_hieu': soHieu};
}

class FileRef {
  final String fileId;
  final String? filename;

  const FileRef({required this.fileId, this.filename});

  factory FileRef.fromJson(Map<String, dynamic> json) {
    final fileIdValue = json['file_id'] ?? json['fileId'];
    if (fileIdValue is! String) {
      throw const FormatException('Invalid file reference payload');
    }
    return FileRef(
      fileId: fileIdValue,
      filename: json['filename'] as String?,
    );
  }

  static List<FileRef> listFromJson(dynamic value) {
    if (value == null) {
      return <FileRef>[];
    }
    if (value is List) {
      return value
          .map(
            (item) => FileRef.fromJson(Map<String, dynamic>.from(item as Map)),
          )
          .toList();
    }
    throw const FormatException('Invalid file reference list');
  }

  Map<String, dynamic> toJson() {
    final map = {'file_id': fileId};
    if (filename != null) {
      map['filename'] = filename!;
    }
    return map;
  }
}
