import 'package:event_bus/event_bus.dart';

final EventBus eventBus = EventBus();

// Base event class
abstract class AppEvent {}

// Example events - add more as needed
class SearchEvent extends AppEvent {
  final String query;
  
  SearchEvent(this.query);
}

class DocumentSelectedEvent extends AppEvent {
  final String documentId;
  
  DocumentSelectedEvent(this.documentId);
}

class ChatMessageEvent extends AppEvent {
  final String message;
  
  ChatMessageEvent(this.message);
}

class ErrorEvent extends AppEvent {
  final String message;
  final dynamic error;
  
  ErrorEvent(this.message, [this.error]);
}

class LoadingEvent extends AppEvent {
  final bool isLoading;
  
  LoadingEvent(this.isLoading);
}
