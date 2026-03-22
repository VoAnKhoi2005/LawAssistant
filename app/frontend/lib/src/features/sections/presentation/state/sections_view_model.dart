import 'package:flutter/material.dart';

import '../../domain/models/section_content.dart';
import '../../domain/models/section_node.dart';

class SectionsViewModel extends ChangeNotifier {
  String? _selectedDocument;
  String? _selectedNodeId;
  String _selectedFilter = 'All';
  List<SectionNode> _hierarchyNodes = [];
  SectionContent? _currentContent;

  SectionsViewModel() {
    _seedMockData();
  }

  String? get selectedDocument => _selectedDocument;
  String? get selectedNodeId => _selectedNodeId;
  String get selectedFilter => _selectedFilter;
  List<SectionNode> get hierarchyNodes => _hierarchyNodes;
  SectionContent? get currentContent => _currentContent;

  List<String> get availableDocuments => const [
        'Luật Đất đai 2024',
        'Bộ luật Dân sự 2015',
        'Luật Đầu tư 2020',
      ];

  List<Map<String, dynamic>> get filters => const [
        {'label': 'All', 'icon': null},
        {'label': 'Amendments', 'icon': Icons.edit_note},
        {'label': 'Appendix', 'icon': Icons.attachment},
      ];

  void selectDocument(String? document) {
    if (document == null || document == _selectedDocument) return;
    _selectedDocument = document;
    _selectedNodeId = null;
    _currentContent = null;
    _hierarchyNodes = [];
    notifyListeners();
    debugPrint('TODO: Load document: $document');
  }

  void selectFilter(String filter) {
    if (_selectedFilter == filter) return;
    _selectedFilter = filter;
    notifyListeners();
    debugPrint('TODO: Filter by: $filter');
  }

  void search(String query) {
    debugPrint('TODO: Search for: $query');
    notifyListeners();
  }

  void selectNode(SectionNode node) {
    if (_selectedNodeId == node.id) return;
    _selectedNodeId = node.id;
    _currentContent = _mapNodeToContent(node);
    notifyListeners();
    debugPrint('Load content for node: ${node.id}');
  }

  void handlePrint() {
    debugPrint('TODO: Print current section');
  }

  void handleShare() {
    debugPrint('TODO: Share current section');
  }

  void handleHistory() {
    debugPrint('TODO: Show section history');
  }

  void _seedMockData() {
    _hierarchyNodes = [
      SectionNode(
        id: 'chuong-1',
        title: 'Chương I',
        subtitle: 'Quy định chung',
        type: SectionNodeType.chapter,
        children: [
          SectionNode(
            id: 'muc-1',
            title: 'Mục 1',
            subtitle: 'Phạm vi điều chỉnh',
            type: SectionNodeType.section,
            children: [
              SectionNode(
                id: 'dieu-1',
                title: 'Điều 1',
                type: SectionNodeType.article,
                children: [
                  SectionNode(
                    id: 'khoan-1',
                    title: 'Khoản 1',
                    type: SectionNodeType.clause,
                  ),
                  SectionNode(
                    id: 'khoan-2',
                    title: 'Khoản 2',
                    type: SectionNodeType.clause,
                    children: [
                      SectionNode(
                        id: 'diem-a',
                        title: 'Điểm a',
                        type: SectionNodeType.point,
                      ),
                    ],
                  ),
                ],
              ),
              SectionNode(
                id: 'dieu-2',
                title: 'Điều 2',
                type: SectionNodeType.article,
              ),
            ],
          ),
        ],
      ),
      SectionNode(
        id: 'chuong-2',
        title: 'Chương II',
        subtitle: 'Quyền và nghĩa vụ',
        type: SectionNodeType.chapter,
      ),
    ];

    _selectedDocument = 'Luật Đất đai 2024';
    _selectedNodeId = 'dieu-1';
    _currentContent = SectionContent(
      id: 'dieu-1',
      title: 'Điều 1. Phạm vi điều chỉnh',
      reference: '01/2024/L-CTN',
      type: 'General Provisions',
      content:
          'Luật này quy định về chế độ sở hữu đất đai, quyền hạn và trách nhiệm của Nhà nước đại diện chủ sở hữu toàn dân về đất đai và thống nhất quản lý về đất đai, chế độ quản lý và sử dụng đất đai, quyền và nghĩa vụ của công dân, người sử dụng đất đối với đất đai thuộc lãnh thổ của nước Cộng hòa xã hội chủ nghĩa Việt Nam.',
      paragraphs: const [
        'Đất đai thuộc sở hữu toàn dân do Nhà nước đại diện chủ sở hữu và thống nhất quản lý.',
        'Nhà nước trao quyền sử dụng đất cho người sử dụng đất theo quy định của Luật này.',
      ],
      status: SectionStatus.effective,
      revisionDate: '2023',
      metadata: SectionMetadata(
        originalSource: 'Văn bản hợp nhất số 12/VBHN-VPQH',
        authorizingBody: 'Quốc hội Khóa XV',
        tags: const ['Real Estate', 'Civil'],
      ),
    );
  }

  SectionContent _mapNodeToContent(SectionNode node) {
    if (node.type == SectionNodeType.chapter || node.type == SectionNodeType.section) {
      return SectionContent(
        id: node.id,
        title: node.title,
        reference: 'STRUCTURE',
        type: 'Hierarchy',
        content: 'Đây là mục cấu trúc: ${node.title}',
        paragraphs: const [],
        status: SectionStatus.effective,
        metadata: SectionMetadata(
          authorizingBody: 'System',
          tags: const ['Structure'],
        ),
      );
    }

    return SectionContent(
      id: node.id,
      title: '${node.title}${node.subtitle != null ? '. ${node.subtitle}' : ''}',
      reference: 'AUTO/${node.id.toUpperCase()}',
      type: node.type.name,
      content:
          'Nội dung của ${node.title}. Đây là dữ liệu giả lập để hiển thị nội dung điều khoản.',
      paragraphs: [
        'Khoản 1: Nội dung chi tiết cho ${node.title}.',
        'Khoản 2: Quy định bổ sung liên quan đến ${node.title}.',
      ],
      status: SectionStatus.effective,
      revisionDate: '2024',
      metadata: SectionMetadata(
        originalSource: 'Generated Mock Data',
        authorizingBody: 'Quốc hội Việt Nam',
        tags: [node.type.name],
      ),
    );
  }
}
