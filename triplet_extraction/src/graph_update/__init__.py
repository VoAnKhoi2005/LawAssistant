"""
Knowledge Graph Update Module

This module implements the near-realtime knowledge update system for legal documents
as described in the paper 'Near-Realtime Knowledge Update on the Legal Search Platform'
(KSE IEEE).

Main components:
- AmendmentDetector: Analyzes legal text to identify amendments and their types
- KnowledgeGraphUpdater: Updates the knowledge graph based on amendment types
- AmendmentProcessor: Orchestrates the complete amendment processing workflow

Usage:
    from triplet_extraction.src.graph_update import create_amendment_processor
    
    # Create processor
    processor = create_amendment_processor()
    
    # Get summary of amendments
    summary = processor.get_amendment_summary()
    
    # Process all amendments (dry run)
    results = processor.process_all_amendments(dry_run=True)
    
    # Process amendments for specific document
    results = processor.process_all_amendments(so_hieu='123/2021/ND-CP')
"""

from triplet_extraction.src.graph_update.amendment_detector import (
    AmendmentDetector,
    AmendmentType,
    AMENDMENT_PATTERNS,
    LOCATION_PATTERNS,
    build_target_path
)

from triplet_extraction.src.graph_update.graph_updater import (
    KnowledgeGraphUpdater
)

from triplet_extraction.src.graph_update.processor import (
    AmendmentProcessor,
    create_amendment_processor
)

__all__ = [
    'AmendmentDetector',
    'AmendmentType',
    'KnowledgeGraphUpdater',
    'AmendmentProcessor',
    'create_amendment_processor',
    'AMENDMENT_PATTERNS',
    'LOCATION_PATTERNS',
    'build_target_path'
]
