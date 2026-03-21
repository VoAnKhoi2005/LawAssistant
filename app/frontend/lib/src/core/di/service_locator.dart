import 'package:get_it/get_it.dart';
import '../network/api_client.dart';
import '../api/services/auth_api_service.dart';
import '../api/services/concept_api_service.dart';
import '../api/services/document_api_service.dart';
import '../api/services/legal_section_api_service.dart';
import '../api/services/relation_api_service.dart';
import '../api/services/section_relation_api_service.dart';
import '../api/services/triplet_api_service.dart';
import '../api/services/user_api_service.dart';
final getIt = GetIt.instance;

void setupDependencyInjection() {
  // Core - Network
  getIt.registerLazySingleton<ApiClient>(() => ApiClient());

  // Auth & User
  getIt.registerLazySingleton<AuthApiService>(
    () => AuthApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<UserApiService>(
    () => UserApiService(getIt<ApiClient>()),
  );

  // Knowledge Graph domain services
  getIt.registerLazySingleton<DocumentApiService>(
    () => DocumentApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<ConceptApiService>(
    () => ConceptApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<LegalSectionApiService>(
    () => LegalSectionApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<RelationApiService>(
    () => RelationApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<SectionRelationApiService>(
    () => SectionRelationApiService(getIt<ApiClient>()),
  );
  getIt.registerLazySingleton<TripletApiService>(
    () => TripletApiService(getIt<ApiClient>()),
  );
}
