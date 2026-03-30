import 'common_models.dart';

class RefDetails {
  final String? chuong;
  final String? diem;
  final String dieu;
  final String? khoan;
  final String? muc;
  final String? phan;
  final String? phuLuc;
  final String soHieu;
  final String? tieuMuc;

  const RefDetails({
    this.chuong,
    this.diem,
    required this.dieu,
    this.khoan,
    this.muc,
    this.phan,
    this.phuLuc,
    required this.soHieu,
    this.tieuMuc,
  });

  factory RefDetails.fromJson(Map<String, dynamic> json) {
    return RefDetails(
      chuong: json['chuong'] as String?,
      diem: json['diem'] as String?,
      dieu: json['dieu']?.toString() ?? '',
      khoan: json['khoan'] as String?,
      muc: json['muc'] as String?,
      phan: json['phan'] as String?,
      phuLuc: json['phu_luc'] as String?,
      soHieu: json['so_hieu']?.toString() ?? '',
      tieuMuc: json['tieu_muc'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'chuong': chuong,
      'diem': diem,
      'dieu': dieu,
      'khoan': khoan,
      'muc': muc,
      'phan': phan,
      'phu_luc': phuLuc,
      'so_hieu': soHieu,
      'tieu_muc': tieuMuc,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class SectionRelationDto {
  final ObjectIdModel? id;
  final String source;
  final String target;
  final String type;
  final List<String>? amendmentTypes;
  final RefDetails? refDetails;

  const SectionRelationDto({
    this.id,
    required this.source,
    required this.target,
    required this.type,
    this.amendmentTypes,
    this.refDetails,
  });

  factory SectionRelationDto.fromJson(Map<String, dynamic> json) {
    return SectionRelationDto(
      id: ObjectIdModel.maybeFromJson(json['_id']),
      source: json['source'] as String? ?? '',
      target: json['target'] as String? ?? '',
      type: json['type'] as String? ?? '',
      amendmentTypes: (json['amendment_types'] as List<dynamic>?)
          ?.map((item) => item.toString())
          .toList(),
      refDetails: json['ref_details'] == null
          ? null
          : RefDetails.fromJson(
              Map<String, dynamic>.from(json['ref_details'] as Map),
            ),
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'source': source,
      'target': target,
      'type': type,
      'amendment_types': amendmentTypes,
      'ref_details': refDetails?.toJson(),
    };
    if (includeId && id != null) {
      map['_id'] = id!.toJson();
    }
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class CreateSectionRelationRequest {
  final String source;
  final String target;
  final String type;
  final List<String>? amendmentTypes;
  final RefDetails? refDetails;

  const CreateSectionRelationRequest({
    required this.source,
    required this.target,
    required this.type,
    this.amendmentTypes,
    this.refDetails,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'source': source,
      'target': target,
      'type': type,
      'amendment_types': amendmentTypes,
      'ref_details': refDetails?.toJson(),
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class UpdateSectionRelationRequest {
  final String? source;
  final String? target;
  final String? type;
  final List<String>? amendmentTypes;
  final RefDetails? refDetails;

  const UpdateSectionRelationRequest({
    this.source,
    this.target,
    this.type,
    this.amendmentTypes,
    this.refDetails,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'source': source,
      'target': target,
      'type': type,
      'amendment_types': amendmentTypes,
      'ref_details': refDetails?.toJson(),
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}
