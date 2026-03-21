import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/documents_provider.dart';
import '../widgets/documents_header.dart';
import '../widgets/documents_filter_bar.dart';
import '../widgets/documents_table.dart';
import '../widgets/documents_sidebar.dart';
import '../../../../core/constants/breakpoints.dart';

class DocumentsPage extends StatefulWidget {
  const DocumentsPage({super.key});

  @override
  State<DocumentsPage> createState() => _DocumentsPageState();
}

class _DocumentsPageState extends State<DocumentsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DocumentsProvider>().loadDocuments();
    });
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final breakpoints = Breakpoints(constraints.maxWidth);
        
        return Scaffold(
          appBar: !breakpoints.showSidebar
              ? AppBar(
                  title: const Text('Documents'),
                  elevation: 0,
                )
              : null,
          body: Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    DocumentsHeader(isMobile: breakpoints.isMobile),
                    if (!breakpoints.isMobile) const DocumentsFilterBar(),
                    const Expanded(child: DocumentsTable()),
                  ],
                ),
              ),
              if (breakpoints.showDetailsSidebar) const DocumentsSidebar(),
            ],
          ),
          endDrawer: breakpoints.isMobile || breakpoints.isTablet
              ? const Drawer(child: DocumentsSidebar())
              : null,
        );
      },
    );
  }
}
