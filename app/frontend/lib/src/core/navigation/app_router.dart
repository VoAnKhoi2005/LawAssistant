import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/documents/presentation/pages/documents_page.dart';
import '../../features/sections/presentation/pages/sections_page.dart';
import '../../features/knowledge_graph/presentation/pages/knowledge_graph_page.dart';
import '../widgets/main_layout.dart';
import 'routes.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: Routes.documents,
    routes: [
      // Auth routes (without layout)
      GoRoute(
        path: Routes.login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      
      // Main routes with layout
      ShellRoute(
        builder: (context, state, child) => MainLayout(child: child),
        routes: [
          GoRoute(
            path: Routes.documents,
            name: 'documents',
            builder: (context, state) => const DocumentsPage(),
          ),
          GoRoute(
            path: Routes.sections,
            name: 'sections',
            builder: (context, state) => const SectionsPage(),
          ),
          GoRoute(
            path: Routes.knowledgeGraph,
            name: 'knowledge-graph',
            builder: (context, state) => const KnowledgeGraphPage(),
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => const _ErrorPage(),
  );
}

class _ErrorPage extends StatelessWidget {
  const _ErrorPage();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Không tìm thấy trang',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => context.go(Routes.documents),
              icon: const Icon(Icons.home),
              label: const Text('Về trang chủ'),
            ),
          ],
        ),
      ),
    );
  }
}
