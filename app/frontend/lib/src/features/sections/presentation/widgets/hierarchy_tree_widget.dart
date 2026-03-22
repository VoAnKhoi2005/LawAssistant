import 'package:flutter/material.dart';

import '../../domain/models/section_node.dart';

class HierarchyTreeWidget extends StatefulWidget {
  final List<SectionNode> nodes;
  final String? selectedNodeId;
  final ValueChanged<SectionNode> onNodeSelected;
  final double baseIndent;

  const HierarchyTreeWidget({
    Key? key,
    required this.nodes,
    this.selectedNodeId,
    required this.onNodeSelected,
    this.baseIndent = 10,
  }) : super(key: key);

  @override
  State<HierarchyTreeWidget> createState() => _HierarchyTreeWidgetState();
}

class _HierarchyTreeWidgetState extends State<HierarchyTreeWidget> {
  final Set<String> _expandedNodes = {};

  @override
  void initState() {
    super.initState();
    _expandInitial();
  }

  void _expandInitial() {
    for (var node in widget.nodes) {
      _expandedNodes.add(node.id);

      if (node.hasChildren) {
        for (var child in node.children) {
          if (child.id == widget.selectedNodeId) {
            _expandedNodes.add(node.id); // expand parent
          }
        }
      }
    }
  }

  @override
  void didUpdateWidget(covariant HierarchyTreeWidget oldWidget) {
    super.didUpdateWidget(oldWidget);

    // Ensure UI reacts when parent changes selected node
    if (oldWidget.selectedNodeId != widget.selectedNodeId) {
      _expandToSelected(widget.nodes);
    }
  }

  void _expandToSelected(List<SectionNode> nodes) {
    for (var node in nodes) {
      if (node.id == widget.selectedNodeId) return;

      if (node.hasChildren) {
        for (var child in node.children) {
          if (child.id == widget.selectedNodeId) {
            _expandedNodes.add(node.id);
          }
        }
        _expandToSelected(node.children);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'DOCUMENT STRUCTURE',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              color: colorScheme.outlineVariant,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: ListView.builder(
              itemCount: widget.nodes.length,
              itemBuilder: (context, index) {
                return _buildTreeNode(widget.nodes[index], 0);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTreeNode(SectionNode node, int level) {
    final colorScheme = Theme.of(context).colorScheme;
    final isSelected = node.id == widget.selectedNodeId;
    final isExpanded = _expandedNodes.contains(node.id);

    final styleConfig = _getStyleForLevel(level);

    return Container(
      margin: EdgeInsets.only(left: styleConfig.leftMargin, bottom: 2),
      child: Column(
        children: [
          InkWell(
            onTap: () {
              widget.onNodeSelected(node);

              // Optional: auto expand when clicking parent
              if (node.hasChildren) {
                setState(() {
                  _expandedNodes.add(node.id);
                });
              }
            },
            borderRadius: BorderRadius.circular(styleConfig.borderRadius),
            child: Container(
              padding: styleConfig.padding,
              decoration: BoxDecoration(
                color: isSelected ? colorScheme.primary : Colors.transparent,
                borderRadius: BorderRadius.circular(styleConfig.borderRadius),
              ),
              child: Row(
                children: [
                  if (node.hasChildren)
                    GestureDetector(
                      onTap: () {
                        setState(() {
                          if (_expandedNodes.contains(node.id)) {
                            _expandedNodes.remove(node.id);
                          } else {
                            _expandedNodes.add(node.id);
                          }
                        });
                      },
                      child: Icon(
                        isExpanded
                            ? Icons.keyboard_arrow_down
                            : Icons.keyboard_arrow_right,
                        size: styleConfig.iconSize,
                        color: isSelected
                            ? colorScheme.onSecondaryContainer
                            : colorScheme.outline,
                      ),
                    )
                  else
                    SizedBox(width: styleConfig.iconSize),

                  const SizedBox(width: 4),

                  Icon(
                    _getIconForNodeType(node.type),
                    size: styleConfig.iconSize,
                    color: isSelected
                        ? colorScheme.onSecondaryContainer
                        : colorScheme.outline,
                  ),

                  const SizedBox(width: 8),

                  Expanded(
                    child: Text(
                      node.title,
                      style: TextStyle(
                        fontSize: styleConfig.fontSize,
                        fontWeight: styleConfig.fontWeight,
                        color: isSelected
                            ? colorScheme.onSecondaryContainer
                            : colorScheme.onSurface,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),

                  if (node.subtitle != null && node.subtitle!.isNotEmpty) ...[
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        node.subtitle!,
                        style: TextStyle(
                          fontSize: styleConfig.subtitleFontSize,
                          fontStyle: FontStyle.italic,
                          color: isSelected
                              ? colorScheme.onSecondaryContainer.withOpacity(
                                  0.7,
                                )
                              : colorScheme.outlineVariant,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],

                  if (isSelected) ...[
                    const SizedBox(width: 8),
                    Icon(
                      Icons.chevron_right,
                      size: 16,
                      color: colorScheme.primary,
                    ),
                  ],
                ],
              ),
            ),
          ),

          if (node.hasChildren && isExpanded)
            ...node.children.map((child) => _buildTreeNode(child, level + 1)),
        ],
      ),
    );
  }

  _NodeStyleConfig _getStyleForLevel(int level) {
    final baseIndent = widget.baseIndent;

    switch (level) {
      case 0:
        return _NodeStyleConfig(
          fontSize: 14,
          subtitleFontSize: 11,
          fontWeight: FontWeight.w700,
          iconSize: 20,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          leftMargin: level * baseIndent,
          borderRadius: 8,
        );
      case 1:
        return _NodeStyleConfig(
          fontSize: 13,
          subtitleFontSize: 10,
          fontWeight: FontWeight.w600,
          iconSize: 18,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          leftMargin: level * baseIndent,
          borderRadius: 8,
        );
      case 2:
        return _NodeStyleConfig(
          fontSize: 12,
          subtitleFontSize: 10,
          fontWeight: FontWeight.w500,
          iconSize: 16,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
          leftMargin: level * baseIndent,
          borderRadius: 6,
        );
      default:
        return _NodeStyleConfig(
          fontSize: 11,
          subtitleFontSize: 9,
          fontWeight: FontWeight.w400,
          iconSize: 14,
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
          leftMargin: level * baseIndent,
          borderRadius: 6,
        );
    }
  }

  IconData _getIconForNodeType(SectionNodeType type) {
    switch (type) {
      case SectionNodeType.chapter:
        return Icons.folder;
      case SectionNodeType.section:
        return Icons.folder_open;
      case SectionNodeType.article:
        return Icons.description;
      case SectionNodeType.clause:
        return Icons.subject;
      case SectionNodeType.point:
        return Icons.fiber_manual_record;
      case SectionNodeType.subpoint:
        return Icons.fiber_manual_record_outlined;
    }
  }
}

class _NodeStyleConfig {
  final double fontSize;
  final double subtitleFontSize;
  final FontWeight fontWeight;
  final double iconSize;
  final EdgeInsets padding;
  final double leftMargin;
  final double borderRadius;

  _NodeStyleConfig({
    required this.fontSize,
    required this.subtitleFontSize,
    required this.fontWeight,
    required this.iconSize,
    required this.padding,
    required this.leftMargin,
    required this.borderRadius,
  });
}
