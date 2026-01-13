from typing import List, Dict


def collect_sections_content_upward(
    sections_col,
    section_ids: List[str]
) -> Dict[str, str]:
    """
    For each section_id:
      - walk parent_id upward until type == 'điều'
      - collect all content on the path

    Returns:
      { section_id: merged_content }
    """

    pipeline = [
        {
            "$match": {
                "_id": {"$in": section_ids}
            }
        },
        {
            "$graphLookup": {
                "from": sections_col.name,
                "startWith": "$parent_id",
                "connectFromField": "parent_id",
                "connectToField": "_id",
                "as": "ancestors",
                "depthField": "depth"
            }
        },
        {
            "$addFields": {
                "chain": {
                    "$concatArrays": [["$$ROOT"], "$ancestors"]
                }
            }
        },
        {
            "$project": {
                "_id": 1,
                "chain": 1
            }
        }
    ]

    docs = list(sections_col.aggregate(pipeline))

    result = {}

    for doc in docs:
        chain = doc["chain"]

        # sort bottom → top
        chain.sort(key=lambda x: x.get("depth", -1))

        contents = []
        for s in chain:
            if s.get("content"):
                contents.append(s["content"].strip())
            if s.get("type") == "điều":
                break

        result[str(doc["_id"])] = "\n".join(reversed(contents))

    return result

def collect_sections_content_downward(
    sections_col,
    section_ids: List[str],
) -> Dict[str, str]:
    """
    For each section_id:
      - walk downward to all children (parent may have multiple children)
      - collect all content in the subtree

    Returns:
      { section_id: merged_content }
    """

    pipeline = [
        {
            "$match": {
                "_id": {"$in": section_ids}
            }
        },
        {
            "$graphLookup": {
                "from": sections_col.name,
                "startWith": "$_id",
                "connectFromField": "_id",
                "connectToField": "parent_id",
                "as": "descendants",
                "depthField": "depth"
            }
        },
        {
            "$addFields": {
                "subtree": {
                    "$concatArrays": [["$$ROOT"], "$descendants"]
                }
            }
        },
        {
            "$project": {
                "_id": 1,
                "subtree": 1
            }
        }
    ]

    docs = list(sections_col.aggregate(pipeline))
    result = {}

    for doc in docs:
        nodes = doc["subtree"]

        # sort top → bottom
        nodes.sort(key=lambda x: x.get("depth", 0))

        contents = []
        for n in nodes:
            if n.get("content"):
                contents.append(n["content"].strip())

        result[str(doc["_id"])] = "\n".join(contents)

    return result