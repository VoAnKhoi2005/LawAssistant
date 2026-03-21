class LegalSectionDto {
  final String? id;
  final String sectionId;
  final String? content;
  final String documentTitle;
  final String effectiveDate;
  final String fullPath;
  final String? parentId;
  final String soHieu;
  final String sourceFile;
  final String title;
  final String type;
  final bool? isAmendment;
  final bool? isPhuLuc;

  const LegalSectionDto({
    this.id,
    required this.sectionId,
    this.content,
    required this.documentTitle,
    required this.effectiveDate,
    required this.fullPath,
    this.parentId,
    required this.soHieu,
    required this.sourceFile,
    required this.title,
    required this.type,
    this.isAmendment,
    this.isPhuLuc,
  });

  factory LegalSectionDto.fromJson(Map<String, dynamic> json) {
    return LegalSectionDto(
      id: json['_id']?.toString(),
      sectionId: json['id']?.toString() ?? json['section_id']?.toString() ?? '',
      content: json['content'] as String?,
      documentTitle: json['document_title'] as String? ?? '',
      effectiveDate: json['effective_date'] as String? ?? '',
      fullPath: json['full_path'] as String? ?? '',
      parentId: json['parent_id'] as String?,
      soHieu: json['so_hieu'] as String? ?? '',
      sourceFile: json['source_file'] as String? ?? '',
      title: json['title'] as String? ?? '',
      type: json['type'] as String? ?? '',
      isAmendment: json['is_amendment'] as bool?,
      isPhuLuc: json['is_phu_luc'] as bool?,
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'content': content,
      'document_title': documentTitle,
      'effective_date': effectiveDate,
      'full_path': fullPath,
      'id': sectionId,
      'parent_id': parentId,
      'so_hieu': soHieu,
      'source_file': sourceFile,
      'title': title,
      'type': type,
      'is_amendment': isAmendment,
      'is_phu_luc': isPhuLuc,
    };
    if (includeId && id != null) {
      map['_id'] = id;
    }
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class CreateLegalSectionRequest {
  final String? content;
  final String documentTitle;
  final String effectiveDate;
  final String fullPath;
  final String sectionId;
  final String? parentId;
  final String soHieu;
  final String sourceFile;
  final String title;
  final String type;
  final bool? isAmendment;
  final bool? isPhuLuc;

  const CreateLegalSectionRequest({
    this.content,
    required this.documentTitle,
    required this.effectiveDate,
    required this.fullPath,
    required this.sectionId,
    this.parentId,
    required this.soHieu,
    required this.sourceFile,
    required this.title,
    required this.type,
    this.isAmendment,
    this.isPhuLuc,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'content': content,
      'document_title': documentTitle,
      'effective_date': effectiveDate,
      'full_path': fullPath,
      'id': sectionId,
      'parent_id': parentId,
      'so_hieu': soHieu,
      'source_file': sourceFile,
      'title': title,
      'type': type,
      'is_amendment': isAmendment,
      'is_phu_luc': isPhuLuc,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class UpdateLegalSectionRequest {
  final String? content;
  final String? documentTitle;
  final String? effectiveDate;
  final String? fullPath;
  final String? parentId;
  final String? soHieu;
  final String? sourceFile;
  final String? title;
  final String? type;
  final bool? isAmendment;
  final bool? isPhuLuc;

  const UpdateLegalSectionRequest({
    this.content,
    this.documentTitle,
    this.effectiveDate,
    this.fullPath,
    this.parentId,
    this.soHieu,
    this.sourceFile,
    this.title,
    this.type,
    this.isAmendment,
    this.isPhuLuc,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'content': content,
      'document_title': documentTitle,
      'effective_date': effectiveDate,
      'full_path': fullPath,
      'parent_id': parentId,
      'so_hieu': soHieu,
      'source_file': sourceFile,
      'title': title,
      'type': type,
      'is_amendment': isAmendment,
      'is_phu_luc': isPhuLuc,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}
