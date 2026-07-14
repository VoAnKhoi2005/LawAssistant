import json
import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from transformers.integrations import tiktoken

from knowledge_graph.triplet_extraction.utils import clean_text

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
MODEL_NAME = "gpt-4o-mini"
MAX_FILE_TOKENS = 2_000_000
MAX_TASK_TOKENS = 500_000
OUTPUT_PREFIX = "batch_property_law_v2"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "KB_PROPERTY_LAW"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db['legal_sections']

# Prompt template for sentence simplification
SIMPLIFY_SYSTEM_PROMPT = """
Role: You are a professional Legal and Linguistics AI Assistant specializing in Vietnamese law. Your task is to deconstruct complex legal texts into independent, direct simple sentences.
Objective: Transform legal clauses into standalone simple sentences. Each sentence must be a direct legal statement, avoiding introductory fillers or explanatory bridges.
Strict "Directness" Rules:
No Filler Subjects: Do not use phrases like "Một loại hành vi là..." (One type of behavior is...), "Bao gồm các loại..." (Includes types of...), or "Được xác định như sau" (Is defined as follows).
Direct Predication: Connect the main Subject directly to the specific Action or Object.
Incorrect: "Một loại hành vi vi phạm là làm sai lệch hồ sơ."
Correct: "Hành vi vi phạm quy định về hồ sơ bao gồm hành vi làm sai lệch hồ sơ." (Or simply: "Làm sai lệch hồ sơ là hành vi vi phạm quy định về hồ sơ.")
The "Simple Sentence" Constraint:
Exactly one Subject and one Predicate.
No conjunctions (và, hoặc, nhưng, mà, còn, rồi...).
No commas (,) or semicolons (;) to link clauses.
Copy Forward Context: If the input lists sub-items under a heading, integrate the full heading context into every single sub-item to ensure they are legally complete.
Output Format:
Return strictly a JSON object.
If information is insufficient: {"need_more_information": "..."}.
If successful: {"simplified_sentences": ["Direct Sentence 1.", "Direct Sentence 2."]}.
Example Transformation: Input: "Hành vi vi phạm quy định về hồ sơ địa giới bao gồm: (a) Làm sai lệch sơ đồ; (b) Làm sai lệch bảng tọa độ." Output: { "simplified_sentences": [ "Hành vi làm sai lệch sơ đồ là hành vi vi phạm quy định về hồ sơ địa giới.", "Hành vi làm sai lệch bảng tọa độ là hành vi vi phạm quy định về hồ sơ địa giới." ] }
"""

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")

def collect_path(leaf):
    path = []
    current = leaf

    while current:
        path.append(current)
        pid = current.get("parent_id")
        current = id_map.get(pid)

    # reverse to get root → leaf
    path.reverse()
    return path

sections_data = []

def get_gpt_response(user_prompt, system_prompt, api_key, model="gpt-4o"):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def count_chat_tokens(messages):
    """
    Rough but safe token count for chat.completions
    """
    tokens = 0
    for msg in messages:
        tokens += 4  # role + formatting overhead
        tokens += len(encoding.encode(msg["content"]))
    tokens += 2  # assistant reply priming
    return tokens

def normalize_for_json(obj):
    if isinstance(obj, dict):
        return {k: normalize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_for_json(v) for v in obj]
    elif isinstance(obj, tuple):
        return list(obj)
    return obj


def split_text_by_tokens(text: str, max_tokens: int) -> List[str]:
    """
    Split long content into token-safe chunks
    """
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))

    return chunks

# TODO Connect with step 1 and input the correct "so_hieu" values to filter the sections we want to process
so_hieu = ""

# Load only what we need
docs = list(db.legal_sections.find({"so_hieu": so_hieu}))

# Collect all parent_ids that appear
parent_ids = {
    doc["parent_id"]
    for doc in docs
    if doc.get("parent_id") is not None
}

# Leaf nodes = ids that never appear as a parent_id
leaf_nodes = [
    doc for doc in docs
    if doc["_id"] not in parent_ids
]

print(f"Leaf nodes: {len(leaf_nodes)}")

all_docs = list(db.legal_sections.find({}))

id_map = {doc["_id"]: doc for doc in all_docs}

for leaf in leaf_nodes:
    path_nodes = collect_path(leaf)
    if leaf.get("is_phu_luc"):
        continue

    if leaf.get("is_amendment"):
        continue

    result = {
        "leaf_id": leaf["_id"],
        "so_hieu": leaf.get("so_hieu"),
        "full_path": leaf.get("full_path"),
        "combined_content": "\n".join(
            n["content"]
            for n in path_nodes
            if n.get("content") and n["type"] in ["điều", "khoản", "điểm"]
        )
    }

    if not result["combined_content"]:
        continue

    sections_data.append(result)
print(f"Total sections collected: {len(sections_data)}")

tasks = []
for section in sections_data:
    so_hieu = section["so_hieu"]
    section_id = section["leaf_id"]
    full_path = section["full_path"]
    content = clean_text(section["combined_content"])

    # split oversized content first
    content_chunks = split_text_by_tokens(content, MAX_TASK_TOKENS)

    if not section_id:
        print("No section id error")
        break

    for idx, chunk in enumerate(content_chunks, start=1):
        task = {
            "custom_id": section_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SIMPLIFY_SYSTEM_PROMPT},
                    {"role": "user", "content": f'Sentence need simplify:  "{chunk}"'},
                ],
            },
        }

        tokens = count_chat_tokens(task["body"]["messages"])

        if tokens > MAX_FILE_TOKENS:
            raise ValueError(
                f"Task {task['custom_id']} exceeds 2M tokens alone ({tokens})"
            )
        task["_token_count"] = tokens
        tasks.append(task)

files = []
current_file = []
current_tokens = 0

for task in tasks:
    if current_tokens + task["_token_count"] > MAX_FILE_TOKENS:
        files.append(current_file)
        current_file = []
        current_tokens = 0

    current_file.append(task)
    current_tokens += task["_token_count"]

if current_file:
    files.append(current_file)

os.makedirs(OUTPUT_PREFIX, exist_ok=True)
for idx, file_tasks in enumerate(files, start=1):
    filename = f"./{OUTPUT_PREFIX}/{OUTPUT_PREFIX}_part{idx}.jsonl"

    with open(filename, "w", encoding="utf-8") as f:
        for task in file_tasks:
            task_copy = dict(task)
            task_copy.pop("_token_count", None)
            task_copy = normalize_for_json(task_copy)
            f.write(json.dumps(task_copy, ensure_ascii=False) + "\n")

    total_tokens = sum(t["_token_count"] for t in file_tasks)

    print(
        f"✔ {filename} | "
        f"{len(file_tasks)} tasks | "
        f"{total_tokens:,} tokens"
    )

print("\n===== SUMMARY =====")
print(f"Total tasks: {len(tasks)}")
print(f"Total files: {len(files)}")
print(f"Total tokens: {sum(t['_token_count'] for t in tasks):,}")

import os
import time
from openai import OpenAI

gpt_client = OpenAI()

INPUT_SECTIONS_JSONL_FOLDER = r"E:\Github\LawAssistant\src\triplet_extraction\batch_preprocessing\batch_property_law_v2"
RESULT_FOLDER = r"E:\Github\LawAssistant\src\triplet_extraction\batch_preprocessing\batch_property_law_v2\results"

os.makedirs(RESULT_FOLDER, exist_ok=True)

def meta_path(filename):
    return os.path.join(RESULT_FOLDER, f"{filename}.meta.json")

def result_path(filename):
    return os.path.join(RESULT_FOLDER, f"{filename}.result.jsonl")

def process_file(filename):
    input_path = os.path.join(INPUT_SECTIONS_JSONL_FOLDER, filename)
    meta_file = meta_path(filename)
    result_file = result_path(filename)

    if os.path.exists(result_file):
        return

    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        batch_id = meta["batch_id"]
        batch = gpt_client.batches.retrieve(batch_id)
    else:
        file_obj = gpt_client.files.create(
            file=open(input_path, "rb"),
            purpose="batch"
        )
        batch = gpt_client.batches.create(
            input_file_id=file_obj.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(
                {"file_id": file_obj.id, "batch_id": batch.id},
                f,
                indent=2
            )

    while True:
        batch = gpt_client.batches.retrieve(batch.id)
        if batch.status in ("completed", "failed", "expired"):
            break
        print(f"Batch {batch.id} status: {batch.status}. Waiting 5 minutes...")
        time.sleep(300)

    if batch.status != "completed":
        return

    content = gpt_client.files.content(batch.output_file_id)
    with open(result_file, "wb") as f:
        f.write(content.read())

for filename in sorted(os.listdir(INPUT_SECTIONS_JSONL_FOLDER)):
    if not filename.endswith(".jsonl"):
        continue
    try:
        process_file(filename)
    except Exception:
        continue

from knowledge_graph.mongo_helpers import init_mongo
from pathlib import Path
import json
from tqdm import tqdm

# Folder containing all batch result files
RESULT_FOLDER = Path(
    r"E:\Github\LawAssistant\src\triplet_extraction\batch_preprocessing\batch_property_law_v2\results"
)

mongo_client = init_mongo()
if not mongo_client:
    print("Failed to connect to MongoDB. Exiting.")
    exit(1)

db = mongo_client["KB_PROPERTY_LAW"]

section_collection = db["legal_sections"]
collection = db["processed_legal_sections"]

# Collect all JSONL result files
files = sorted(RESULT_FOLDER.glob("*.jsonl"))

total_sentences = 0
missing_sections = 0

# File-level progress bar
for file in tqdm(files, desc="Processing result files", unit="file"):
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Line-level progress bar
    for line in tqdm(lines, desc=file.name, unit="line", leave=False):
        data = json.loads(line)

        if data.get("response", {}).get("status_code") != 200:
            continue

        raw_content = data["response"]["body"]["choices"][0]["message"]["content"].strip()
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            continue

        sentences = parsed.get("simplified_sentences", [])
        if not sentences:
            continue

        section_id = data["custom_id"].split("_part")[0]
        section_doc = section_collection.find_one(
            {"_id": section_id},
            {"so_hieu": 1}
        )

        if not section_doc:
            missing_sections += 1
            continue

        so_hieu = section_doc["so_hieu"]

        sequence = 1
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            collection.update_one(
                {
                    "section_id": section_id,
                    "sequence": sequence
                },
                {
                    "$setOnInsert": {
                        "content": sentence,
                        "so_hieu": so_hieu
                    }
                },
                upsert=True
            )

            total_sentences += 1
            sequence += 1

print(f"Sentences inserted : {total_sentences}")
print(f"Missing sections   : {missing_sections}")
print(f"Files processed    : {len(files)}")
