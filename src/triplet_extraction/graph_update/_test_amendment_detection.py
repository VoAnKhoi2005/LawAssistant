from src.db import init_mongo
from src.triplet_extraction.graph_update import parse_amendment_reference

mongo_client = init_mongo()
db = mongo_client["KB_PROPERTY_LAW"]
document_col = db["documents"]

lines = []

with open("test_amendment_detection.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            lines.append(line)

for i, text in enumerate(lines, 1):
    print(f"\nTest {i}")
    print("Input:", text)

    try:
        result = parse_amendment_reference(text, document_col)

        print("Output:")
        for ref in result:
            print(ref)

    except Exception as e:
        print("Error:", e)