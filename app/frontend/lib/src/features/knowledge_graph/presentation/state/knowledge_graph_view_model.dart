import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'package:law_assistant_kg/src/core/api/models/common_models.dart';
import 'package:law_assistant_kg/src/core/api/models/triplet_models.dart';

enum GraphNodeType { subject, object }

class GraphNode {
  final String id;
  final String label;
  final GraphNodeType type;
  final int documentCount;

  const GraphNode({
    required this.id,
    required this.label,
    required this.type,
    this.documentCount = 0,
  });
}

class GraphEdge {
  final String id;
  final String from;
  final String to;
  final String relation;
  final String? soHieu;

  const GraphEdge({
    required this.id,
    required this.from,
    required this.to,
    required this.relation,
    this.soHieu,
  });
}

class KnowledgeGraphViewModel extends ChangeNotifier {
  String? _selectedDocument;
  String? _selectedSection;
  bool _showGraph = false;
  bool _showEditPanel = false;
  String? _selectedNodeId;
  List<TripletDto> _triplets = const [];

  KnowledgeGraphViewModel() {
    loadExampleGraph();
  }

  String? get selectedDocument => _selectedDocument;
  String? get selectedSection => _selectedSection;
  bool get showGraph => _showGraph;
  bool get showEditPanel => _showEditPanel;
  String? get selectedNodeId => _selectedNodeId;

  List<TripletDto> get triplets => _triplets;

  List<GraphNode> get graphNodes {
    final nodes = <String, GraphNode>{};
    for (final triplet in _triplets) {
      final subjectKey = 'subject:${triplet.subjectId.value}';
      final objectKey = 'object:${triplet.objectId.value}';

      nodes.putIfAbsent(
        subjectKey,
        () => GraphNode(
          id: subjectKey,
          label: triplet.subjectName,
          type: GraphNodeType.subject,
          documentCount: triplet.documents.length,
        ),
      );
      nodes.putIfAbsent(
        objectKey,
        () => GraphNode(
          id: objectKey,
          label: triplet.objectName,
          type: GraphNodeType.object,
          documentCount: triplet.documents.length,
        ),
      );
    }
    return nodes.values.toList();
  }

  List<GraphEdge> get graphEdges {
    final edges = <GraphEdge>[];
    for (var i = 0; i < _triplets.length; i++) {
      final triplet = _triplets[i];
      edges.add(
        GraphEdge(
          id: triplet.id?.value ?? 'edge-$i',
          from: 'subject:${triplet.subjectId.value}',
          to: 'object:${triplet.objectId.value}',
          relation: triplet.relationName,
          soHieu: triplet.documents.isNotEmpty ? triplet.documents.first.soHieu : null,
        ),
      );
    }
    return edges;
  }

  GraphNode? get selectedNode {
    try {
      return graphNodes.firstWhere((node) => node.id == _selectedNodeId);
    } catch (_) {
      return null;
    }
  }

  List<GraphEdge> edgesForNode(String nodeId) {
    return graphEdges.where((edge) => edge.from == nodeId || edge.to == nodeId).toList();
  }

  void selectDocument(String? document) {
    if (document == null) return;
    _selectedDocument = document;
    _selectedSection = null;
    notifyListeners();
    debugPrint('TODO: Load graph for document: $document');
  }

  void selectSection(String? section) {
    if (section == null) return;
    _selectedSection = section;
    notifyListeners();
    debugPrint('TODO: Load graph for section: $section');
  }

  void toggleEditPanel() {
    _showEditPanel = !_showEditPanel;
    notifyListeners();
  }

  void showGraphExample() {
    _showGraph = true;
    notifyListeners();
  }

  void loadExampleGraph() {
    _selectedDocument = 'Bộ luật Dân sự 2015';
    _selectedSection = 'Điều 385 - Hợp đồng';
    _showGraph = true;
    _triplets = _buildSampleTriplets();
    notifyListeners();
  }

  void selectNode(String? nodeId) {
    _selectedNodeId = nodeId;
    _showEditPanel = nodeId != null;
    notifyListeners();
  }

  void handleHistory() => debugPrint('TODO: Show graph history');

  void handleShare() => debugPrint('TODO: Share graph snapshot');

  void handleZoomIn() => debugPrint('TODO: Zoom in');

  void handleZoomOut() => debugPrint('TODO: Zoom out');

  void handleCenter() => debugPrint('TODO: Center graph');

  void handleSaveChanges() => debugPrint('TODO: Persist graph edits');

  void handleDeleteRelation() => debugPrint('TODO: Delete selected relation');

  List<TripletDto> _buildSampleTriplets() {
    return const [
      TripletDto(
        id: ObjectIdModel('triplet-1'),
        documents: [
          DocumentRef(sectionId: 'dieu-385', soHieu: 'BLDS 2015'),
          DocumentRef(sectionId: 'dieu-401', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-thuc-hien'),
        objectName: 'Thực hiện nghĩa vụ',
        relationId: ObjectIdModel('rel-quy-dinh'),
        relationName: 'Quy định',
        subjectId: ObjectIdModel('subject-hop-dong'),
        subjectName: 'Hợp đồng dân sự',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-2'),
        documents: [
          DocumentRef(sectionId: 'dieu-398', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-bao-lanh'),
        objectName: 'Bảo lãnh',
        relationId: ObjectIdModel('rel-lien-quan'),
        relationName: 'Liên quan đến',
        subjectId: ObjectIdModel('subject-hop-dong'),
        subjectName: 'Hợp đồng dân sự',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-3'),
        documents: [
          DocumentRef(sectionId: 'dieu-117', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-vo-hieu'),
        objectName: 'Giao dịch vô hiệu',
        relationId: ObjectIdModel('rel-dan-den'),
        relationName: 'Dẫn đến',
        subjectId: ObjectIdModel('subject-dieu-kien'),
        subjectName: 'Điều kiện có hiệu lực',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-4'),
        documents: [
          DocumentRef(sectionId: 'dieu-351', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-trach-nhiem'),
        objectName: 'Trách nhiệm dân sự',
        relationId: ObjectIdModel('rel-phat-sinh'),
        relationName: 'Phát sinh',
        subjectId: ObjectIdModel('subject-vi-pham'),
        subjectName: 'Vi phạm nghĩa vụ',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-5'),
        documents: [
          DocumentRef(sectionId: 'dieu-117', soHieu: 'BLDS 2015'),
          DocumentRef(sectionId: 'dieu-122', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-vo-hieu-toan-phan'),
        objectName: 'Vô hiệu toàn phần',
        relationId: ObjectIdModel('rel-dan-toi'),
        relationName: 'Dẫn tới',
        subjectId: ObjectIdModel('subject-vi-pham-nghiem-trong'),
        subjectName: 'Vi phạm nghiêm trọng',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-6'),
        documents: [
          DocumentRef(sectionId: 'dieu-401', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-thoa-thuan'),
        objectName: 'Thỏa thuận bổ sung',
        relationId: ObjectIdModel('rel-bo-sung'),
        relationName: 'Bổ sung',
        subjectId: ObjectIdModel('subject-hop-dong'),
        subjectName: 'Hợp đồng dân sự',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-7'),
        documents: [
          DocumentRef(sectionId: 'dieu-420', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-dam-bao'),
        objectName: 'Biện pháp bảo đảm',
        relationId: ObjectIdModel('rel-ap-dung'),
        relationName: 'Áp dụng',
        subjectId: ObjectIdModel('subject-hop-dong'),
        subjectName: 'Hợp đồng dân sự',
      ),
      TripletDto(
        id: ObjectIdModel('triplet-8'),
        documents: [
          DocumentRef(sectionId: 'dieu-423', soHieu: 'BLDS 2015'),
        ],
        objectId: ObjectIdModel('object-cham-dut'),
        objectName: 'Chấm dứt nghĩa vụ',
        relationId: ObjectIdModel('rel-dan-den'),
        relationName: 'Dẫn đến',
        subjectId: ObjectIdModel('subject-thuc-hien'),
        subjectName: 'Thực hiện nghĩa vụ',
      ),
    ];
  }
}
