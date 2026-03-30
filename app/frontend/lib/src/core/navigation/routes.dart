class Routes {
  // Auth routes
  static const login = '/login';
  static const register = '/register';
  
  // Main routes
  static const documents = '/documents';
  static const sections = '/sections';
  static const knowledgeGraph = '/kg';
  
  // Document routes
  static const documentDetail = '/documents/:id';
  static String documentDetailPath(String id) => '/documents/$id';
  
  // Section routes
  static const sectionDetail = '/sections/:id';
  static String sectionDetailPath(String id) => '/sections/$id';
  
  // KG routes
  static const kgDetail = '/kg/:id';
  static String kgDetailPath(String id) => '/kg/$id';
}
