/// Section Node Model - Represents a node in the document hierarchy tree
class SectionNode {
  final String id;
  final String title;
  final String? subtitle;
  final SectionNodeType type;
  final List<SectionNode> children;
  final Map<String, dynamic>? metadata;

  SectionNode({
    required this.id,
    required this.title,
    this.subtitle,
    required this.type,
    this.children = const [],
    this.metadata,
  });

  bool get hasChildren => children.isNotEmpty;

  factory SectionNode.fromJson(Map<String, dynamic> json) {
    return SectionNode(
      id: json['id'] as String,
      title: json['title'] as String,
      subtitle: json['subtitle'] as String?,
      type: SectionNodeType.fromString(json['type'] as String),
      children: (json['children'] as List<dynamic>?)
              ?.map((e) => SectionNode.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'subtitle': subtitle,
      'type': type.name,
      'children': children.map((e) => e.toJson()).toList(),
      'metadata': metadata,
    };
  }
}

/// Section Node Type - Types of nodes in the hierarchy
enum SectionNodeType {
  chapter,    // Chương
  section,    // Mục
  article,    // Điều
  clause,     // Khoản
  point,      // Điểm
  subpoint;   // Tiểu mục

  static SectionNodeType fromString(String type) {
    switch (type.toLowerCase()) {
      case 'chapter':
      case 'chuong':
        return SectionNodeType.chapter;
      case 'section':
      case 'muc':
        return SectionNodeType.section;
      case 'article':
      case 'dieu':
        return SectionNodeType.article;
      case 'clause':
      case 'khoan':
        return SectionNodeType.clause;
      case 'point':
      case 'diem':
        return SectionNodeType.point;
      case 'subpoint':
        return SectionNodeType.subpoint;
      default:
        return SectionNodeType.article;
    }
  }

  String get displayName {
    switch (this) {
      case SectionNodeType.chapter:
        return 'Chương';
      case SectionNodeType.section:
        return 'Mục';
      case SectionNodeType.article:
        return 'Điều';
      case SectionNodeType.clause:
        return 'Khoản';
      case SectionNodeType.point:
        return 'Điểm';
      case SectionNodeType.subpoint:
        return 'Tiểu mục';
    }
  }
}
