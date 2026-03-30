/// Section Content Model - Represents the content of a section/article
class SectionContent {
  final String id;
  final String title;
  final String reference;
  final String type;
  final String content;
  final List<String> paragraphs;
  final SectionStatus status;
  final String? revisionDate;
  final SectionMetadata? metadata;

  SectionContent({
    required this.id,
    required this.title,
    required this.reference,
    required this.type,
    required this.content,
    this.paragraphs = const [],
    this.status = SectionStatus.effective,
    this.revisionDate,
    this.metadata,
  });

  factory SectionContent.fromJson(Map<String, dynamic> json) {
    return SectionContent(
      id: json['id'] as String,
      title: json['title'] as String,
      reference: json['reference'] as String,
      type: json['type'] as String,
      content: json['content'] as String,
      paragraphs: (json['paragraphs'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      status: SectionStatus.fromString(json['status'] as String? ?? 'effective'),
      revisionDate: json['revisionDate'] as String?,
      metadata: json['metadata'] != null
          ? SectionMetadata.fromJson(json['metadata'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'reference': reference,
      'type': type,
      'content': content,
      'paragraphs': paragraphs,
      'status': status.name,
      'revisionDate': revisionDate,
      'metadata': metadata?.toJson(),
    };
  }
}

/// Section Status
enum SectionStatus {
  effective,
  amended,
  expired,
  draft;

  static SectionStatus fromString(String status) {
    switch (status.toLowerCase()) {
      case 'effective':
        return SectionStatus.effective;
      case 'amended':
        return SectionStatus.amended;
      case 'expired':
        return SectionStatus.expired;
      case 'draft':
        return SectionStatus.draft;
      default:
        return SectionStatus.effective;
    }
  }

  String get displayName {
    switch (this) {
      case SectionStatus.effective:
        return 'Status: Effective';
      case SectionStatus.amended:
        return 'Status: Amended';
      case SectionStatus.expired:
        return 'Status: Expired';
      case SectionStatus.draft:
        return 'Status: Draft';
    }
  }
}

/// Section Metadata
class SectionMetadata {
  final String? originalSource;
  final String? authorizingBody;
  final List<String> tags;

  SectionMetadata({
    this.originalSource,
    this.authorizingBody,
    this.tags = const [],
  });

  factory SectionMetadata.fromJson(Map<String, dynamic> json) {
    return SectionMetadata(
      originalSource: json['originalSource'] as String?,
      authorizingBody: json['authorizingBody'] as String?,
      tags: (json['tags'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'originalSource': originalSource,
      'authorizingBody': authorizingBody,
      'tags': tags,
    };
  }
}
