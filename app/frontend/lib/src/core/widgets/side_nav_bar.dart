import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../navigation/routes.dart';

class SideNavBar extends StatelessWidget {
  final String currentRoute;

  const SideNavBar({super.key, required this.currentRoute});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      width: 256,
      color: isDark ? const Color(0xFF1A1B1E) : const Color(0xFFF8FAFC),
      child: Column(
        children: [
          // Logo section
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 24, 24, 32),
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
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        'MANAGEMENT SYSTEM',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
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

          // Navigation items
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                children: [
                   _NavItem(
                     icon: Icons.description_outlined,
                     label: 'Documents',
                     isActive: currentRoute.startsWith(Routes.documents),
                     onTap: () => context.go(Routes.documents),
                   ),
                   const SizedBox(height: 4),
                   _NavItem(
                     icon: Icons.account_tree_outlined,
                     label: 'Sections',
                     isActive: currentRoute.startsWith(Routes.sections),
                     onTap: () => context.go(Routes.sections),
                   ),
                   const SizedBox(height: 4),
                   _NavItem(
                     icon: Icons.account_balance_outlined,
                     label: 'KG',
                     isActive: currentRoute.startsWith(Routes.knowledgeGraph),
                     onTap: () => context.go(Routes.knowledgeGraph),
                   ),
                ],
              ),
            ),
          ),

          // Bottom section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Container(
                  height: 1,
                  color: theme.colorScheme.outlineVariant.withOpacity(0.2),
                ),
                const SizedBox(height: 16),
                _NavItem(
                  icon: Icons.logout,
                  label: 'Logout',
                  isActive: false,
                  onTap: () => context.go(Routes.login),
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
  final bool isActive;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: isActive ? theme.colorScheme.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: isActive
                    ? Colors.white
                    : isDark
                    ? Colors.grey[400]
                    : theme.colorScheme.primary,
              ),
              const SizedBox(width: 12),
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: isActive
                      ? Colors.white
                      : isDark
                      ? Colors.grey[400]
                      : theme.colorScheme.primary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
