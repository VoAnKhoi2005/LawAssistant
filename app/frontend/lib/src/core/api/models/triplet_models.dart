import 'common_models.dart';

class TripletDto {
  final ObjectIdModel? id;
  final List<DocumentRef> documents;
  final ObjectIdModel objectId;
  final String objectName;
  final ObjectIdModel relationId;
  final String relationName;
  final ObjectIdModel subjectId;
  final String subjectName;

  const TripletDto({
    this.id,
    required this.documents,
    required this.objectId,
    required this.objectName,
    required this.relationId,
    required this.relationName,
    required this.subjectId,
    required this.subjectName,
  });

  factory TripletDto.fromJson(Map<String, dynamic> json) {
    return TripletDto(
      id: ObjectIdModel.maybeFromJson(json['_id']),
      documents: DocumentRef.listFromJson(json['documents']),
      objectId: ObjectIdModel.fromJson(json['object_id']),
      objectName: json['object_name'] as String? ?? '',
      relationId: ObjectIdModel.fromJson(json['relation_id']),
      relationName: json['relation_name'] as String? ?? '',
      subjectId: ObjectIdModel.fromJson(json['subject_id']),
      subjectName: json['subject_name'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'documents': documents.map((doc) => doc.toJson()).toList(),
      'object_id': objectId.toJson(),
      'object_name': objectName,
      'relation_id': relationId.toJson(),
      'relation_name': relationName,
      'subject_id': subjectId.toJson(),
      'subject_name': subjectName,
    };
    if (includeId && id != null) {
      map['_id'] = id!.toJson();
    }
    return map;
  }
}

class CreateTripletRequest {
  final List<DocumentRef> documents;
  final ObjectIdModel objectId;
  final String objectName;
  final ObjectIdModel relationId;
  final String relationName;
  final ObjectIdModel subjectId;
  final String subjectName;

  const CreateTripletRequest({
    required this.documents,
    required this.objectId,
    required this.objectName,
    required this.relationId,
    required this.relationName,
    required this.subjectId,
    required this.subjectName,
  });

  Map<String, dynamic> toJson() => {
    'documents': documents.map((doc) => doc.toJson()).toList(),
    'object_id': objectId.toJson(),
    'object_name': objectName,
    'relation_id': relationId.toJson(),
    'relation_name': relationName,
    'subject_id': subjectId.toJson(),
    'subject_name': subjectName,
  };
}

class UpdateTripletRequest {
  final List<DocumentRef>? documents;
  final ObjectIdModel? objectId;
  final String? objectName;
  final ObjectIdModel? relationId;
  final String? relationName;
  final ObjectIdModel? subjectId;
  final String? subjectName;

  const UpdateTripletRequest({
    this.documents,
    this.objectId,
    this.objectName,
    this.relationId,
    this.relationName,
    this.subjectId,
    this.subjectName,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'documents': documents?.map((doc) => doc.toJson()).toList(),
      'object_id': objectId?.toJson(),
      'object_name': objectName,
      'relation_id': relationId?.toJson(),
      'relation_name': relationName,
      'subject_id': subjectId?.toJson(),
      'subject_name': subjectName,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class AddSectionToTripletRequest {
  final String sectionId;
  final String soHieu;

  const AddSectionToTripletRequest({
    required this.sectionId,
    required this.soHieu,
  });

  Map<String, dynamic> toJson() => {'section_id': sectionId, 'so_hieu': soHieu};
}
