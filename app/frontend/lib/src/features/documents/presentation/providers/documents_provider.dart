import 'package:flutter/foundation.dart';
import '../../../../core/api/models/document_models.dart';
import '../../../../core/api/services/document_api_service.dart';

enum DocumentsLoadingState {
  initial,
  loading,
  loaded,
  error,
}

class DocumentsProvider extends ChangeNotifier {
  final DocumentApiService _documentService;

  DocumentsProvider(this._documentService);

  DocumentApiService get documentService => _documentService;

  DocumentsLoadingState _state = DocumentsLoadingState.initial;
  List<DocumentDto> _documents = [];
  String? _errorMessage;
  int _currentPage = 1;
  int _totalCount = 0;
  final int _pageSize = 100;

  DocumentsLoadingState get state => _state;
  List<DocumentDto> get documents => _documents;
  String? get errorMessage => _errorMessage;
  int get currentPage => _currentPage;
  int get totalPages => (_totalCount / _pageSize).ceil();
  bool get hasNextPage => _currentPage < totalPages;
  bool get hasPrevPage => _currentPage > 1;

  Future<void> loadDocuments({int page = 1}) async {
    _state = DocumentsLoadingState.loading;
    _currentPage = page;
    notifyListeners();

    final skip = (page - 1) * _pageSize;
    final response = await _documentService.getDocuments(
      skip: skip,
      limit: _pageSize,
    );

    if (response.success && response.data != null) {
      _documents = response.data!;
      _state = DocumentsLoadingState.loaded;
      _errorMessage = null;
    } else {
      _state = DocumentsLoadingState.error;
      _errorMessage = response.error ?? 'Failed to load documents';
    }
    notifyListeners();
  }

  Future<void> nextPage() async {
    if (hasNextPage) {
      await loadDocuments(page: _currentPage + 1);
    }
  }

  Future<void> prevPage() async {
    if (hasPrevPage) {
      await loadDocuments(page: _currentPage - 1);
    }
  }

  Future<bool> createDocument(CreateDocumentRequest request) async {
    final response = await _documentService.createDocument(request);
    if (response.success && response.data != null) {
      await refresh();
      return true;
    }
    _errorMessage = response.error ?? 'Failed to create document';
    return false;
  }

  Future<bool> updateDocument(String id, UpdateDocumentRequest request) async {
    final response = await _documentService.updateDocument(id, request);
    if (response.success && response.data != null) {
      final index = _documents.indexWhere((doc) => doc.id?.value == id);
      if (index != -1) {
        _documents[index] = response.data!;
        notifyListeners();
      }
      return true;
    }
    _errorMessage = response.error ?? 'Failed to update document';
    return false;
  }

  Future<bool> deleteDocument(String id) async {
    final response = await _documentService.deleteDocument(id);
    if (response.success) {
      _documents.removeWhere((doc) => doc.id?.value == id);
      notifyListeners();
      return true;
    }
    _errorMessage = response.error ?? 'Failed to delete document';
    return false;
  }

  Future<void> refresh() async {
    await loadDocuments(page: _currentPage);
  }
}
