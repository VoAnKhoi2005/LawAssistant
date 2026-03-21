import 'common_models.dart';

class ConceptDto {
  final ObjectIdModel? id;
  final String? description;
  final List<DocumentRef> documents;
  final String name;
  final List<String> synonyms;

  const ConceptDto({
    this.id,
    this.description,
    required this.documents,
    required this.name,
    required this.synonyms,
  });

  factory ConceptDto.fromJson(Map<String, dynamic> json) {
    return ConceptDto(
      id: ObjectIdModel.maybeFromJson(json['_id']),
      description: json['description'] as String?,
      documents: DocumentRef.listFromJson(json['documents']),
      name: json['name'] as String? ?? '',
      synonyms: (json['synonym'] as List<dynamic>? ?? const [])
          .map((item) => item.toString())
          .toList(),
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'description': description,
      'documents': documents.map((doc) => doc.toJson()).toList(),
      'name': name,
      'synonym': synonyms,
    };
    if (includeId && id != null) {
      map['_id'] = id!.toJson();
    }
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class CreateConceptRequest {
  final String? description;
  final List<DocumentRef> documents;
  final String name;
  final List<String> synonyms;

  const CreateConceptRequest({
    this.description,
    required this.documents,
    required this.name,
    required this.synonyms,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'description': description,
      'documents': documents.map((doc) => doc.toJson()).toList(),
      'name': name,
      'synonym': synonyms,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class UpdateConceptRequest {
  final String? description;
  final List<DocumentRef>? documents;
  final String? name;
  final List<String>? synonyms;

  const UpdateConceptRequest({
    this.description,
    this.documents,
    this.name,
    this.synonyms,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'description': description,
      'documents': documents?.map((doc) => doc.toJson()).toList(),
      'name': name,
      'synonym': synonyms,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class AddSectionToConceptRequest {
  final String sectionId;
  final String soHieu;

  const AddSectionToConceptRequest({
    required this.sectionId,
    required this.soHieu,
  });

  Map<String, dynamic> toJson() => {'section_id': sectionId, 'so_hieu': soHieu};
}
