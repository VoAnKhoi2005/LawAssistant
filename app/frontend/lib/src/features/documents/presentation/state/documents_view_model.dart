import 'package:flutter/foundation.dart';

class DocumentItem {
  final String id;
  final String number;
  final String title;
  final String field;
  final String date;
  final String status;
  final int totalCount;
  final int pageSize;
  final String statusTagColor;
  final String iconType;

  const DocumentItem({
    required this.id,
    required this.number,
    required this.title,
    required this.field,
    required this.date,
    required this.status,
    this.totalCount = 1248,
    this.pageSize = 10,
    this.statusTagColor = 'tertiary',
    this.iconType = 'pdf',
  });
}

class DocumentsViewModel extends ChangeNotifier {
  final List<String> filters = const ['All', 'Laws', 'Decrees', 'Circulars', 'Decisions'];
  String _selectedFilter = 'All';
  int _currentPage = 1;
  int _documentsPerPage = 10;
  List<DocumentItem> _documents = const [];

  String get selectedFilter => _selectedFilter;
  int get currentPage => _currentPage;
  int get documentsPerPage => _documentsPerPage;
  List<DocumentItem> get documents => _documents;
  int get totalDocuments => _documents.isEmpty ? 0 : _documents.first.totalCount;

  DocumentsViewModel() {
    _seedDemoData();
  }

  void _seedDemoData() {
    _documents = const [
      DocumentItem(
        id: 'LAW-2023-01',
        number: '15/2023/QH15',
        title: 'Luật Đấu thầu 2023',
        field: 'Field: Bidding, Public Asset Management',
        date: '01/01/2024',
        status: 'Active',
        statusTagColor: 'tertiary',
        iconType: 'pdf',
      ),
      DocumentItem(
        id: 'DEC-2023-45',
        number: '24/2023/NĐ-CP',
        title: 'Nghị định quy định chi tiết một số điều của Luật Đấu thầu',
        field: 'Field: Administrative, Specialized Law',
        date: '27/02/2024',
        status: 'Active',
        statusTagColor: 'secondary',
        iconType: 'description',
      ),
      DocumentItem(
        id: 'LAW-2015-12',
        number: '100/2015/QH13',
        title: 'Bộ luật Hình sự 2015 (Sửa đổi 2017)',
        field: 'Field: Judicial, Criminal',
        date: '01/01/2018',
        status: 'Expired (Replaced)',
        statusTagColor: 'neutral',
        iconType: 'pdf',
      ),
    ];
  }

  void selectFilter(String filter) {
    _selectedFilter = filter;
    notifyListeners();
  }

  void changePage(int page) {
    if (page == _currentPage) return;
    _currentPage = page;
    notifyListeners();
  }

  void changePageSize(int size) {
    _documentsPerPage = size;
    notifyListeners();
  }

  void handleSearch(String query) {
    // Placeholder for search integration
    notifyListeners();
  }

  void handleAddDocument() {
    // Placeholder for create flow integration
  }

  void handleDocumentTap(String id) {
    // Placeholder for navigation
  }

  void handleEditDocument(String id) {
    // Placeholder for edit flow
  }

  void handleDeleteDocument(String id) {
    // Placeholder for delete flow
  }

  void handleMoreOptions(String id) {
    // Placeholder for more options menu
  }
}
