import json


def format_results_for_llm(results):
    '''
    Format retrieval results into a structured JSON format suitable for LLM input.

    Args:
        results: List of section dictionaries from pipeline.retrieve()

    Returns:
        JSON string with structured data for main and related sections
    '''
    # Separate main results and related sections
    main_results = [r for r in results if not r.get('is_related_section', False)]
    related_results = [r for r in results if r.get('is_related_section', False)]

    output = {
        "retrieved_sections": [],
        "related_sections": []
    }

    # Format main results
    for idx, section in enumerate(main_results, 1):
        output["retrieved_sections"].append({
            "rank": section.get('rank', idx),
            "document": section.get('so_hieu', 'N/A'),
            "path": section.get('full_path', 'N/A').replace('_', ', '),
            "effective_date": section.get('effective_date', section.get('ngay_hieu_luc', 'N/A')),
            "content": section.get('content', 'N/A')
        })

    # Format related sections
    for idx, section in enumerate(related_results, 1):
        relation_info = section.get('relation_info', [])
        relations = []

        for rel in relation_info:
            rel_data = {
                "type": rel.get('type', 'N/A')
            }
            amendment_types = rel.get('amendment_types', [])
            if amendment_types:
                rel_data["amendment_types"] = amendment_types
            relations.append(rel_data)

        output["related_sections"].append({
            "index": idx,
            "document": section.get('so_hieu', 'N/A'),
            "path": section.get('full_path', 'N/A'),
            "effective_date": section.get('effective_date', section.get('ngay_hieu_luc', 'N/A')),
            "relations": relations,
            "content": section.get('content', 'N/A')
        })

    return json.dumps(output, ensure_ascii=False, indent=2)