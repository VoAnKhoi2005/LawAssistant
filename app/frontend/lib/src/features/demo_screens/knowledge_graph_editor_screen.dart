import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Knowledge Graph Editor Screen
/// Based on: law_assistant_demo/kg_editor_english_ui/code.html
class KnowledgeGraphEditorScreen extends StatefulWidget {
  const KnowledgeGraphEditorScreen({Key? key}) : super(key: key);

  @override
  State<KnowledgeGraphEditorScreen> createState() =>
      _KnowledgeGraphEditorScreenState();
}

class _KnowledgeGraphEditorScreenState
    extends State<KnowledgeGraphEditorScreen> {
  String? _selectedDocument;
  String? _selectedSection;
  bool _showGraph = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Stack(
        children: [
          Column(
            children: [
              _buildHeader(theme, colorScheme),
              _buildSelectionFlow(theme, colorScheme),
              Expanded(
                child: _showGraph
                    ? _buildGraphCanvas(theme, colorScheme)
                    : _buildEmptyState(theme, colorScheme),
              ),
            ],
          ),
          if (_showGraph)
            Positioned(
              right: 0,
              top: 0,
              bottom: 0,
              child: _buildEditSidebar(theme, colorScheme),
            ),
        ],
      ),
    );
  }

  Widget _buildHeader(ThemeData theme, ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(32, 24, 32, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'KNOWLEDGE GRAPH EXPLORER',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurfaceVariant.withOpacity(0.7),
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Cơ sở Dữ liệu Luật Dân sự',
                  style: theme.textTheme.headlineLarge?.copyWith(
                    fontSize: 30,
                  ),
                ),
              ],
            ),
          ),
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.history, size: 16),
                label: const Text('History'),
                style: OutlinedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  side: BorderSide(color: colorScheme.surfaceContainer),
                  backgroundColor: colorScheme.surfaceContainerHigh,
                ),
              ),
              const SizedBox(width: 12),
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: colorScheme.primary,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: colorScheme.primary.withOpacity(0.3),
                      blurRadius: 8,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.share,
                  color: Colors.white,
                  size: 18,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSelectionFlow(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.surfaceContainer),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
          ),
        ],
      ),
      child: Row(
        children: [
          _buildStep('1', 'Select Document', colorScheme),
          Icon(Icons.arrow_forward, size: 14, color: colorScheme.outlineVariant.withOpacity(0.5)),
          const SizedBox(width: 16),
          _buildStep('2', 'Select Section', colorScheme),
        ],
      ),
    );
  }

  Widget _buildStep(String number, String label, ColorScheme colorScheme) {
    return Expanded(
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              number,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: colorScheme.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border.all(color: colorScheme.surfaceContainer),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '-- $label --',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Icon(
                    Icons.expand_more,
                    size: 16,
                    color: colorScheme.outlineVariant,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme, ColorScheme colorScheme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.hub_outlined,
              size: 40,
              color: colorScheme.outlineVariant,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Ready for Relationship Analysis',
            style: theme.textTheme.titleLarge?.copyWith(
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Complete the Document and Section selection above to begin visualizing legal entities.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildStepIndicator('1', 'Document', colorScheme),
              Container(
                width: 40,
                height: 1,
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  border: Border(
                    top: BorderSide(
                      color: colorScheme.outlineVariant,
                      style: BorderStyle.solid,
                      width: 1,
                    ),
                  ),
                ),
              ),
              _buildStepIndicator('2', 'Section', colorScheme),
            ],
          ),
          const SizedBox(height: 48),
          FilledButton(
            onPressed: () {
              setState(() => _showGraph = true);
            },
            child: const Text('Show Example Graph'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(
      String number, String label, ColorScheme colorScheme) {
    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            border: Border.all(
              color: colorScheme.outlineVariant,
              style: BorderStyle.solid,
            ),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            number,
            style: TextStyle(
              fontSize: 12,
              color: colorScheme.outlineVariant,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 9,
            fontWeight: FontWeight.w700,
            color: colorScheme.outline,
            letterSpacing: 1,
          ),
        ),
      ],
    );
  }

  Widget _buildGraphCanvas(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      margin: const EdgeInsets.fromLTRB(32, 8, 32, 24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colorScheme.surfaceContainer),
      ),
      child: Stack(
        children: [
          _buildDottedBackground(),
          _buildGraphNodes(colorScheme),
          _buildFloatingToolbar(colorScheme),
        ],
      ),
    );
  }

  Widget _buildDottedBackground() {
    return CustomPaint(
      painter: DottedBackgroundPainter(),
      child: Container(),
    );
  }

  Widget _buildGraphNodes(ColorScheme colorScheme) {
    return Stack(
      children: [
        CustomPaint(
          painter: GraphEdgesPainter(colorScheme),
          child: Container(),
        ),
        _buildNode(
          'Hợp đồng',
          Icons.gavel,
          colorScheme.primary,
          0.35,
          0.40,
          size: 128,
        ),
        _buildNode(
          'Quyền sử dụng đất',
          Icons.landscape,
          colorScheme.secondaryContainer,
          0.60,
          0.25,
          size: 96,
          label: 'Bao gồm',
        ),
        _buildNode(
          'Bị vô hiệu',
          Icons.warning,
          colorScheme.tertiaryContainer,
          0.60,
          0.35,
          size: 96,
          label: 'Trạng thái',
          labelColor: colorScheme.error,
        ),
        _buildNode(
          'Chủ thể',
          Icons.person,
          colorScheme.surfaceContainerHighest,
          0.65,
          0.60,
          size: 96,
        ),
      ],
    );
  }

  Widget _buildNode(
    String text,
    IconData icon,
    Color color,
    double left,
    double top, {
    double size = 96,
    String? label,
    Color? labelColor,
  }) {
    final isCentral = size > 100;

    return Positioned(
      left: left,
      top: top,
      child: FractionalTranslation(
        translation: const Offset(-0.5, -0.5),
        child: Column(
          children: [
            if (label != null && !isCentral)
              Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: labelColor != null
                      ? labelColor.withOpacity(0.1)
                      : color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: labelColor != null
                      ? Border.all(color: labelColor.withOpacity(0.2))
                      : null,
                ),
                child: Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: labelColor ?? color,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                border: isCentral
                    ? null
                    : Border.all(color: Colors.white, width: 4),
                boxShadow: [
                  BoxShadow(
                    color: color.withOpacity(0.3),
                    blurRadius: isCentral ? 20 : 12,
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    icon,
                    size: isCentral ? 32 : 24,
                    color: isCentral ? Colors.white : null,
                  ),
                  const SizedBox(height: 4),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: Text(
                      text,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: isCentral ? 12 : 10,
                        fontWeight: FontWeight.w700,
                        color: isCentral ? Colors.white : null,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (!isCentral)
              Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(
                    color: Theme.of(context)
                        .colorScheme
                        .outlineVariant
                        .withOpacity(0.2),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 4,
                    ),
                  ],
                ),
                child: Text(
                  'ENTITY',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFloatingToolbar(ColorScheme colorScheme) {
    return Positioned(
      left: 24,
      bottom: 24,
      child: Column(
        children: [
          _buildToolbarButton(Icons.zoom_in, colorScheme),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.zoom_out, colorScheme),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.center_focus_strong, colorScheme),
        ],
      ),
    );
  }

  Widget _buildToolbarButton(IconData icon, ColorScheme colorScheme) {
    return Container(
      width: 36,
      height: 36,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colorScheme.surfaceContainer),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
          ),
        ],
      ),
      child: Icon(
        icon,
        size: 20,
        color: colorScheme.primary,
      ),
    );
  }

  Widget _buildEditSidebar(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      width: 320,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.8),
        border: Border(
          left: BorderSide(
            color: colorScheme.surfaceContainer.withOpacity(0.5),
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 24,
          ),
        ],
      ),
      child: BackdropFilter(
        filter: const ColorFilter.mode(Colors.transparent, BlendMode.multiply),
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Live Edit Panel',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      setState(() => _showGraph = false);
                    },
                  ),
                ],
              ),
              const SizedBox(height: 32),
              _buildSelectedEntitySection(theme, colorScheme),
              const SizedBox(height: 32),
              _buildTripletEditor(theme, colorScheme),
              const SizedBox(height: 32),
              _buildColorPicker(theme, colorScheme),
              const Spacer(),
              _buildActionButtons(theme, colorScheme),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSelectedEntitySection(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'SELECTED ENTITY',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: colorScheme.onSurfaceVariant,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer.withOpacity(0.4),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: colorScheme.primary.withOpacity(0.1),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.gavel, color: colorScheme.primary, size: 20),
                  const SizedBox(width: 12),
                  const Text(
                    'Hợp đồng',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Điều 385. Hợp đồng là sự thỏa thuận giữa các bên về việc xác lập, thay đổi hoặc chấm dứt quyền, nghĩa vụ dân sự.',
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onPrimaryContainer,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTripletEditor(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'UPDATE RELATION (TRIPLET)',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: colorScheme.onSurfaceVariant,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 16),
        _buildTripletField('Subject', 'Hợp đồng', colorScheme),
        const SizedBox(height: 16),
        _buildTripletField('Predicate', 'Bao gồm', colorScheme, hasDropdown: true),
        const SizedBox(height: 16),
        _buildTripletField('Object', 'Quyền sử dụng đất', colorScheme),
      ],
    );
  }

  Widget _buildTripletField(
    String label,
    String value,
    ColorScheme colorScheme, {
    bool hasDropdown = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: colorScheme.outline,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: TextEditingController(text: value),
          decoration: InputDecoration(
            border: const UnderlineInputBorder(),
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(color: colorScheme.outlineVariant),
            ),
            focusedBorder: UnderlineInputBorder(
              borderSide: BorderSide(color: colorScheme.primary),
            ),
            suffixIcon: hasDropdown
                ? Icon(Icons.unfold_more, size: 12, color: colorScheme.outlineVariant)
                : null,
          ),
        ),
      ],
    );
  }

  Widget _buildColorPicker(ThemeData theme, ColorScheme colorScheme) {
    final colors = [
      colorScheme.primary,
      colorScheme.secondaryContainer,
      colorScheme.tertiaryContainer,
      colorScheme.error,
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'NODE APPEARANCE',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: colorScheme.onSurfaceVariant,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: colors.map((color) {
            final isSelected = color == colorScheme.primary;
            return Container(
              width: 32,
              height: 32,
              margin: const EdgeInsets.only(right: 8),
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                border: isSelected
                    ? Border.all(color: colorScheme.primary, width: 2)
                    : null,
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: colorScheme.primary.withOpacity(0.3),
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ]
                    : null,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildActionButtons(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.save, size: 14),
            label: const Text('Save Changes'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton(
            onPressed: () {},
            style: OutlinedButton.styleFrom(
              foregroundColor: colorScheme.error,
              side: BorderSide(color: colorScheme.error.withOpacity(0.2)),
              backgroundColor: colorScheme.errorContainer.withOpacity(0.1),
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
            child: const Text('Delete Relation'),
          ),
        ),
      ],
    );
  }
}

class DottedBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFB2B1BB).withOpacity(0.3)
      ..style = PaintingStyle.fill;

    const spacing = 32.0;
    for (var x = 0.0; x < size.width; x += spacing) {
      for (var y = 0.0; y < size.height; y += spacing) {
        canvas.drawCircle(Offset(x, y), 2, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class GraphEdgesPainter extends CustomPainter {
  final ColorScheme colorScheme;

  GraphEdgesPainter(this.colorScheme);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = colorScheme.primary
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final dashedPaint = Paint()
      ..color = colorScheme.primary
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    _drawLine(canvas, size, 0.45, 0.40, 0.55, 0.40, dashedPaint, dashed: true);
    _drawLine(canvas, size, 0.40, 0.45, 0.35, 0.60, paint);
    _drawLine(canvas, size, 0.55, 0.45, 0.65, 0.60, paint);
  }

  void _drawLine(Canvas canvas, Size size, double x1, double y1, double x2,
      double y2, Paint paint,
      {bool dashed = false}) {
    final start = Offset(size.width * x1, size.height * y1);
    final end = Offset(size.width * x2, size.height * y2);

    if (dashed) {
      _drawDashedLine(canvas, start, end, paint);
    } else {
      canvas.drawLine(start, end, paint);
    }
  }

  void _drawDashedLine(Canvas canvas, Offset start, Offset end, Paint paint) {
    const dashWidth = 4;
    const dashSpace = 4;
    final distance = (end - start).distance;
    final dashCount = (distance / (dashWidth + dashSpace)).floor();

    for (var i = 0; i < dashCount; i++) {
      final t1 = i * (dashWidth + dashSpace) / distance;
      final t2 = (i * (dashWidth + dashSpace) + dashWidth) / distance;
      final p1 = Offset.lerp(start, end, t1)!;
      final p2 = Offset.lerp(start, end, t2)!;
      canvas.drawLine(p1, p2, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
