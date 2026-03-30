import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'side_nav_bar.dart';

class MainLayout extends StatelessWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final currentLocation = GoRouterState.of(context).uri.toString();

    return Scaffold(
      body: Row(
        children: [
          SideNavBar(currentRoute: currentLocation),
          Expanded(child: child),
        ],
      ),
    );
  }
}
