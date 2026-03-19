# Flutter Architecture Structure

## Directory Structure

```
lib/
├── main.dart                          # Application entry point
└── src/
    ├── core/                          # Core functionality
    │   ├── app.dart                   # Main App widget with providers
    │   ├── config/                    # Configuration files
    │   │   └── api_config.dart        # API configuration
    │   ├── di/                        # Dependency Injection
    │   │   └── service_locator.dart   # GetIt service locator setup
    │   ├── events/                    # Event Bus
    │   │   └── app_events.dart        # Application-wide events
    │   ├── models/                    # Core models
    │   │   └── api_response.dart      # Generic API response wrapper
    │   ├── navigation/                # Navigation
    │   │   └── app_router.dart        # GoRouter configuration
    │   └── network/                   # Network layer
    │       └── api_client.dart        # Dio HTTP client wrapper
    │
    └── features/                      # Feature modules
        ├── search/                    # Search feature
        │   ├── data/
        │   │   ├── models/
        │   │   │   └── search_result.dart
        │   │   └── services/
        │   │       └── search_service.dart
        │   └── presentation/
        │       ├── pages/
        │       ├── widgets/
        │       └── providers/
        │
        ├── documents/                 # Documents feature
        │   ├── data/
        │   │   ├── models/
        │   │   │   └── law_document.dart
        │   │   └── services/
        │   │       └── document_service.dart
        │   └── presentation/
        │       ├── pages/
        │       ├── widgets/
        │       └── providers/
        │
        └── chat/                      # Chat feature
            ├── data/
            │   ├── models/
            │   │   └── chat_message.dart
            │   └── services/
            │       └── chat_service.dart
            └── presentation/
                ├── pages/
                ├── widgets/
                └── providers/
```

## Architecture Components

### 1. Dependency Injection (GetIt)
- **Location**: `src/core/di/service_locator.dart`
- **Usage**: 
  ```dart
  final searchService = getIt<SearchService>();
  ```
- All services are registered at app startup in `main.dart`

### 2. Navigation (GoRouter)
- **Location**: `src/core/navigation/app_router.dart`
- **Routes**:
  - `/` - Home page
  - `/search` - Search page
  - `/documents` - Documents list
  - `/documents/:id` - Document detail
  - `/chat` - Chat page
- **Usage**:
  ```dart
  context.go('/search');
  context.pushNamed('document-detail', pathParameters: {'id': '123'});
  ```

### 3. Event Bus
- **Location**: `src/core/events/app_events.dart`
- **Usage**:
  ```dart
  // Emit event
  eventBus.fire(SearchEvent('query'));
  
  // Listen to event
  eventBus.on<SearchEvent>().listen((event) {
    print(event.query);
  });
  ```

### 4. State Management (Provider)
- **Location**: Feature-specific providers in `features/*/presentation/providers/`
- Registered in `src/core/app.dart`

### 5. API Communication
- **Base Client**: `src/core/network/api_client.dart` (using Dio)
- **Configuration**: `src/core/config/api_config.dart`
- **Services**: Feature-specific services in `features/*/data/services/`

## Services

### SearchService
```dart
final searchService = getIt<SearchService>();

// Basic search
final result = await searchService.search('query');

// Hybrid search with options
final result = await searchService.hybridSearch(
  query: 'query',
  limit: 20,
  threshold: 0.5,
);
```

### DocumentService
```dart
final docService = getIt<DocumentService>();

// Get all documents
final docs = await docService.getDocuments();

// Get document by ID
final doc = await docService.getDocumentById('id');

// Get document articles
final articles = await docService.getDocumentArticles('soHieu');
```

### ChatService
```dart
final chatService = getIt<ChatService>();

// Send message
final response = await chatService.sendMessage('Hello');

// Get chat history
final history = await chatService.getChatHistory();
```

## Setup Instructions

1. **Install dependencies**:
   ```bash
   cd frontend
   flutter pub get
   ```

2. **Generate JSON serialization code**:
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## Environment Configuration

Create a `.env` file in the frontend directory:
```
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
```

## Adding a New Feature

1. Create feature directory structure:
   ```
   features/
   └── new_feature/
       ├── data/
       │   ├── models/
       │   └── services/
       └── presentation/
           ├── pages/
           ├── widgets/
           └── providers/
   ```

2. Create service and register in `service_locator.dart`

3. Add routes in `app_router.dart`

4. Create providers and register in `app.dart`

## Best Practices

- Keep features independent and modular
- Use dependency injection for all services
- Handle errors consistently with `ApiResponse<T>`
- Use events for cross-feature communication
- Follow the established folder structure
- Write unit tests for services and providers
