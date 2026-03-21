import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../navigation/routes.dart';
import '../constants/breakpoints.dart';

class MainLayout extends StatelessWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final breakpoints = Breakpoints(constraints.maxWidth);
        
        return Scaffold(
          drawer: !breakpoints.showSidebar ? const _SideNavigationDrawer() : null,
          body: Row(
            children: [
              if (breakpoints.showSidebar) const _SideNavigation(),
              Expanded(child: child),
            ],
          ),
        );
      },
    );
  }
}

class _SideNavigation extends StatelessWidget {
  const _SideNavigation();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentLocation = GoRouterState.of(context).uri.toString();
    
    return Container(
      width: 256,
      decoration: BoxDecoration(
        color: theme.brightness == Brightness.light
            ? const Color(0xFFF5F2F8)
            : const Color(0xFF1A1B1E),
      ),
      child: Column(
        children: [
          // Logo Header
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.account_balance,
                    color: theme.colorScheme.onPrimary,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Lexis Obsidian',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                        ),
                      ),
                      Text(
                        'MANAGEMENT SYSTEM',
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.5,
                          color: theme.colorScheme.primary.withOpacity(0.6),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Navigation Items
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Column(
                children: [
                  _NavItem(
                    icon: Icons.description,
                    label: 'Documents',
                    route: Routes.documents,
                    isActive: currentLocation.startsWith(Routes.documents),
                  ),
                  const SizedBox(height: 4),
                  _NavItem(
                    icon: Icons.account_tree,
                    label: 'Sections',
                    route: Routes.sections,
                    isActive: currentLocation.startsWith(Routes.sections),
                  ),
                  const SizedBox(height: 4),
                  _NavItem(
                    icon: Icons.account_balance,
                    label: 'KG',
                    route: Routes.knowledgeGraph,
                    isActive: currentLocation.startsWith(Routes.knowledgeGraph),
                  ),
                ],
              ),
            ),
          ),
          
          // Bottom Actions
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: () {
                      // TODO: Implement add new entry
                    },
                    icon: const Icon(Icons.add, size: 20),
                    label: const Text('New Entry'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  height: 1,
                  color: theme.colorScheme.outlineVariant.withOpacity(0.2),
                ),
                const SizedBox(height: 16),
                InkWell(
                  onTap: () {
                    context.go(Routes.login);
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      children: [
                        Icon(
                          Icons.logout,
                          color: theme.colorScheme.primary,
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Logout',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String route;
  final bool isActive;
  final VoidCallback? onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.route,
    required this.isActive,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return InkWell(
      onTap: onTap ?? () => context.go(route),
      borderRadius: BorderRadius.circular(12),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          color: isActive
              ? theme.colorScheme.primary
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Icon(
              icon,
              color: isActive
                  ? theme.colorScheme.onPrimary
                  : theme.colorScheme.primary,
              size: 20,
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: isActive
                    ? theme.colorScheme.onPrimary
                    : theme.colorScheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Drawer version for mobile
class _SideNavigationDrawer extends StatelessWidget {
  const _SideNavigationDrawer();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentLocation = GoRouterState.of(context).uri.toString();
    
    return Drawer(
      child: Container(
        decoration: BoxDecoration(
          color: theme.brightness == Brightness.light
              ? const Color(0xFFF5F2F8)
              : const Color(0xFF1A1B1E),
        ),
        child: Column(
          children: [
            // Logo Header
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Row(
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primary,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.account_balance,
                      color: theme.colorScheme.onPrimary,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Lexis Obsidian',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            fontSize: 20,
                          ),
                        ),
                        Text(
                          'MANAGEMENT SYSTEM',
                          style: theme.textTheme.labelSmall?.copyWith(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.5,
                            color: theme.colorScheme.primary.withOpacity(0.6),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            // Navigation Items
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Column(
                  children: [
                    _NavItem(
                      icon: Icons.description,
                      label: 'Documents',
                      route: Routes.documents,
                      isActive: currentLocation.startsWith(Routes.documents),
                      onTap: () {
                        context.go(Routes.documents);
                        Navigator.pop(context);
                      },
                    ),
                    const SizedBox(height: 4),
                    _NavItem(
                      icon: Icons.account_tree,
                      label: 'Sections',
                      route: Routes.sections,
                      isActive: currentLocation.startsWith(Routes.sections),
                      onTap: () {
                        context.go(Routes.sections);
                        Navigator.pop(context);
                      },
                    ),
                    const SizedBox(height: 4),
                    _NavItem(
                      icon: Icons.account_balance,
                      label: 'KG',
                      route: Routes.knowledgeGraph,
                      isActive: currentLocation.startsWith(Routes.knowledgeGraph),
                      onTap: () {
                        context.go(Routes.knowledgeGraph);
                        Navigator.pop(context);
                      },
                    ),
                  ],
                ),
              ),
            ),
            
            // Bottom Actions
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      icon: const Icon(Icons.add, size: 20),
                      label: const Text('New Entry'),
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    height: 1,
                    color: theme.colorScheme.outlineVariant.withOpacity(0.2),
                  ),
                  const SizedBox(height: 16),
                  InkWell(
                    onTap: () {
                      Navigator.pop(context);
                      context.go(Routes.login);
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          Icon(
                            Icons.logout,
                            color: theme.colorScheme.primary,
                            size: 20,
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Logout',
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
