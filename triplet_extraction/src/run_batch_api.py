"""
Script to run ChatGPT Batch API for processing legal documents.
Based on batch_preprocess.ipynb workflow.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from tqdm import tqdm

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Configuration
MODEL_NAME = "gpt-4o-mini"
MAX_FILE_TOKENS = 2_000_000
MAX_TASK_TOKENS = 500_000
OUTPUT_DIR = Path(__file__).parent
BATCH_PREFIX = "batch_property_law"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "KB_PROPERTY_LAW"
SECTION_COLLECTION_NAME = "legal_sections"
PROCESS_COLLECTION_NAME = "processed_legal_sections"

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")


def clean_text(text: str) -> str:
    """Remove newlines, tabs, extra spaces, punctuation and lowercase."""
    import re
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?]+", "", text)
    return text.strip().lower()


def extract_all_with_parents(collection):
    """Extract all 'Điểm' nodes with their parent chain from MongoDB."""
    diem_nodes = list(collection.find({"title": {"$regex": "điểm", "$options": "i"}}))

    if not diem_nodes:
        return []

    results = []

    for node in diem_nodes:
        parent_chain = []
        current = node
        visited = set()

        # Skip appendix items
        if node.get('is_phu_luc'):
            continue

        # Build parent chain
        while current.get('parent_id') is not None and current.get('parent_id') not in visited:
            visited.add(current['_id'])

            parent = collection.find_one({"_id": current['parent_id']})
            if not parent:
                break

            parent_chain.append(parent)
            current = parent

        results.append({
            "target": node,
            "ancestors": parent_chain[::-1]
        })

    return results


def create_prompt(so_hieu, title, content):
    """Create system and user prompts for GPT."""
    system_prompt_rewrite = """
Bạn là trợ lý AI Tiếng Việt chuyên nghiệp và trung thực.
Bạn là chuyên gia pháp luật Việt Nam, am hiểu các bộ luật, nghị định, và văn bản pháp luật.
Bạn là chuyên gia ngôn ngữ Việt Nam, biết viết câu chuẩn cấu trúc, chính xác, trang trọng, và đúng ngôn ngữ pháp lý.
Luôn trả lời chính xác, hữu ích, ngắn gọn và an toàn.
Không thay đổi ý nghĩa khi viết lại câu.
Luôn dùng ngôn ngữ chính xác như trong văn bản pháp luật, tránh ngôn ngữ thông thường hay không trang trọng.
Định nghĩa 'câu đơn': Một câu đơn là câu có một chủ ngữ (hoặc cụm chủ ngữ) và một vị ngữ (hoặc cụm vị ngữ), biểu đạt một ý trọn vẹn; câu có thể chứa thành tố phụ (tính từ, trạng từ, bổ ngữ) nhưng không được ghép bằng liên từ hoặc dấu câu như dấu ",", ";" để tạo hai hoặc nhiều mệnh đề độc lập.

Quy tắc bắt buộc:
1. Khi viết lại, chỉ trả về các câu đơn theo đúng định nghĩa trên; mỗi câu một dòng nếu có nhiều câu.
2. Được phép tái sử dụng các thành phần câu (chủ ngữ, cụm danh từ, đại từ, cụm tính từ, v.v.) từ vế trước hoặc từ phần khác của câu gốc để hoàn chỉnh vế thiếu, nhằm bảo toàn ý nghĩa sau khi tách.
3. Khi tái sử dụng, ưu tiên giữ nguyên** từ ngữ gốc; chỉ thực hiện điều chỉnh nhỏ cần thiết để tạo câu đơn ngữ pháp đúng, **không** thêm thông tin, suy đoán hay nội dung mới.
4. Tuyệt đối không kèm chú giải, giải thích, danh sách hay bất kỳ nội dung nào khác ngoài các câu viết lại.
5. Nếu câu gốc mơ hồ hoặc thiếu thông tin đến mức không thể tạo câu đơn hoàn chỉnh mà vẫn giữ nguyên ý, hãy yêu cầu thêm thông tin ngắn gọn.
Danh mục liên từ cần loại trừ khi viết câu đơn: và, hoặc, hoặc là, hay, hay là, nhưng, song, tuy nhiên, mà, còn, rồi.
Giữ nguyên thứ tự trước sau của các từ sau khi viết lại câu.
Sau khi viết lại câu không được thiếu từ danh từ nào trong câu gốc và phải độc lập không phụ thuộc vào câu trước đó.
"""

    user_prompt_rewrite = f"""
Ngữ cảnh: Bộ luật số {so_hieu} trong luật Việt Nam, {title}
Nhiệm vụ: Viết lại câu sau để hoàn chỉnh cấu trúc với đầy đủ chủ ngữ và vị ngữ, giữ nguyên ý nghĩa. Mỗi câu xuất ra phải là một câu đơn đầy đủ (một dòng một câu nếu có nhiều câu).
Câu cần viết lại: "{content}"
"""
    return system_prompt_rewrite, user_prompt_rewrite


def count_chat_tokens(messages):
    """Rough but safe token count for chat.completions"""
    tokens = 0
    for msg in messages:
        tokens += 4  # role + formatting overhead
        tokens += len(encoding.encode(msg["content"]))
    tokens += 2  # assistant reply priming
    return tokens


def split_text_by_tokens(text: str, max_tokens: int):
    """Split long content into token-safe chunks"""
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))

    return chunks


def normalize_for_json(obj):
    """Normalize MongoDB objects for JSON serialization"""
    from bson import ObjectId
    
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: normalize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_for_json(v) for v in obj]
    return obj


def extract_diem_data_from_mongodb():
    """Extract and prepare data from MongoDB."""
    print("Connecting to MongoDB...")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    collection = db[SECTION_COLLECTION_NAME]

    print("Extracting 'Điểm' data with parent chains...")
    diem_db_data = extract_all_with_parents(collection)
    diem_data = {}

    for diem in diem_db_data:
        content = ""
        title = ""

        for r in diem["ancestors"]:
            title += r['title'] + " "
            title_lower = r['title'].strip().lower()
            # Skip structural headers that don't contain substantive content
            if not (title_lower.startswith("phần thứ")
                    or title_lower.startswith("chương")
                    or title_lower.startswith("mục")
                    or title_lower.startswith("tiểu mục")
                    or title_lower.startswith("điều")
            ):
                content += (r.get('content') or "") + "\n"

        title += diem['target']["title"]
        content += diem['target'].get("content") or ""

        so_hieu = diem['target']['so_hieu']
        ID = str(diem['target']['_id'])

        if not content.strip():
            continue

        diem_data[ID] = {
            "so_hieu": so_hieu,
            "title": title,
            "content": content
        }

    print(f"Extracted {len(diem_data)} entries")
    mongo_client.close()
    return diem_data


def create_batch_files(diem_data):
    """Create JSONL batch files from data."""
    print("\nCreating batch tasks...")
    tasks = []

    for key, value in tqdm(diem_data.items(), desc="Creating tasks"):
        so_hieu = value["so_hieu"]
        title = value["title"]
        content = clean_text(value["content"])

        # Split oversized content
        content_chunks = split_text_by_tokens(content, MAX_TASK_TOKENS)

        for idx, chunk in enumerate(content_chunks, start=1):
            system_prompt, user_prompt = create_prompt(
                so_hieu,
                f"{title} (part {idx}/{len(content_chunks)})" if len(content_chunks) > 1 else title,
                chunk,
            )

            task = {
                "custom_id": key,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
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

    # Split tasks into multiple files based on token limit
    print("\nSplitting into batch files...")
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

    # Write files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_paths = []

    for idx, file_tasks in enumerate(files, start=1):
        filename = OUTPUT_DIR / f"{BATCH_PREFIX}_{timestamp}_part{idx}.jsonl"

        with open(filename, "w", encoding="utf-8") as f:
            for task in file_tasks:
                task_copy = dict(task)
                task_copy.pop("_token_count", None)
                task_copy = normalize_for_json(task_copy)
                f.write(json.dumps(task_copy, ensure_ascii=False) + "\n")

        total_tokens = sum(t["_token_count"] for t in file_tasks)
        file_paths.append(filename)

        print(
            f"✔ {filename.name} | "
            f"{len(file_tasks)} tasks | "
            f"{total_tokens:,} tokens"
        )

    print("\n===== SUMMARY =====")
    print(f"Total tasks: {len(tasks)}")
    print(f"Total files: {len(files)}")
    print(f"Total tokens: {sum(t['_token_count'] for t in tasks):,}")

    return file_paths


def check_existing_output(part_num):
    """Check if output file already exists for this part."""
    output_path = OUTPUT_DIR / f"batch_part{part_num}_output.jsonl"
    return output_path if output_path.exists() else None


def find_existing_batch_for_file(file_path):
    """Find existing batch job for a given input file."""
    # Check progress files for existing batch info
    progress_files = sorted(OUTPUT_DIR.glob("batch_progress_*.json"), reverse=True)
    
    for progress_file in progress_files:
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                results = json.load(f)
                
            for result in results:
                if result.get("file_path") == str(file_path):
                    return result
        except:
            continue
    
    return None


def submit_and_monitor_single_batch(file_path, part_num, total_parts):
    """Submit a single batch file and monitor until completion."""
    print(f"\n{'='*50}")
    print(f"PROCESSING PART {part_num}/{total_parts}: {file_path.name}")
    print(f"{'='*50}")

    # Check if output already exists
    existing_output = check_existing_output(part_num)
    if existing_output:
        print(f"  ✓ Output file already exists: {existing_output.name}")
        return {
            "part": part_num,
            "file_path": str(file_path),
            "status": "completed",
            "output_path": str(existing_output),
            "resumed": True
        }

    # Check if batch already submitted
    existing_batch = find_existing_batch_for_file(file_path)
    if existing_batch and existing_batch.get("batch_id"):
        batch_id = existing_batch["batch_id"]
        print(f"  ✓ Found existing batch: {batch_id}")
        
        # Check current status
        batch = client.batches.retrieve(batch_id)
        print(f"  ✓ Current status: {batch.status}")
        
        if batch.status == "completed" and batch.output_file_id:
            # Download existing results
            output_path = OUTPUT_DIR / f"batch_part{part_num}_output.jsonl"
            print(f"  → Downloading existing results...")
            file_response = client.files.content(batch.output_file_id)
            with open(output_path, "wb") as f:
                f.write(file_response.content)
            print(f"  ✓ Results downloaded: {output_path.name}")
            
            return {
                "part": part_num,
                "file_path": str(file_path),
                "file_id": existing_batch.get("file_id"),
                "batch_id": batch_id,
                "status": "completed",
                "output_path": str(output_path),
                "completed_at": datetime.now().isoformat(),
                "resumed": True
            }
    else:
        # Upload file
        print("  → Uploading file...")
        with open(file_path, "rb") as f:
            batch_input_file = client.files.create(
                file=f,
                purpose="batch"
            )
        print(f"  ✓ File ID: {batch_input_file.id}")

        # Create batch
        print("  → Creating batch job...")
        batch = client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": f"Legal document processing - Part {part_num}/{total_parts}"
            }
        )
        print(f"  ✓ Batch ID: {batch.id}")
        print(f"  ✓ Status: {batch.status}")
        batch_id = batch.id

    # Monitor until completion
    print(f"\n  → Monitoring batch progress...")
    while True:
        batch = client.batches.retrieve(batch_id)
        status = batch.status
        
        print(f"    [{datetime.now().strftime('%H:%M:%S')}] Status: {status}")
        
        if status == "completed":
            print(f"  ✓ Batch completed!")
            
            # Download results
            output_path = OUTPUT_DIR / f"batch_part{part_num}_output.jsonl"
            print(f"  → Downloading results...")
            
            if batch.output_file_id:
                file_response = client.files.content(batch.output_file_id)
                with open(output_path, "wb") as f:
                    f.write(file_response.content)
                print(f"  ✓ Results saved to: {output_path.name}")
                
                return {
                    "part": part_num,
                    "file_path": str(file_path),
                    "file_id": existing_batch.get("file_id") if existing_batch else batch_input_file.id,
                    "batch_id": batch_id,
                    "status": "completed",
                    "output_path": str(output_path),
                    "completed_at": datetime.now().isoformat()
                }
            else:
                print(f"  ⚠ No output file found!")
                return None
                
        elif status == "failed":
            print(f"  ✗ Batch failed!")
            return {
                "part": part_num,
                "file_path": str(file_path),
                "file_id": existing_batch.get("file_id") if existing_batch else batch_input_file.id,
                "batch_id": batch_id,
                "status": "failed",
                "failed_at": datetime.now().isoformat()
            }
            
        elif status in ["validating", "in_progress", "finalizing"]:
            print(f"    Waiting 60 seconds...")
            time.sleep(60)
        else:
            print(f"  ⚠ Unexpected status: {status}")
            time.sleep(60)


def check_batch_status(batch_id):
    """Check status of a batch job."""
    batch = client.batches.retrieve(batch_id)
    return batch


def download_batch_results(batch_id, output_path):
    """Download results from completed batch."""
    batch = client.batches.retrieve(batch_id)
    
    if batch.status != "completed":
        print(f"Batch {batch_id} is not completed yet. Status: {batch.status}")
        return None

    if not batch.output_file_id:
        print(f"No output file found for batch {batch_id}")
        return None

    print(f"Downloading results for batch {batch_id}...")
    file_response = client.files.content(batch.output_file_id)
    
    with open(output_path, "wb") as f:
        f.write(file_response.content)
    
    print(f"✓ Results saved to: {output_path}")
    return output_path


def monitor_batches(batch_info_path):
    """Monitor batch jobs until completion."""
    with open(batch_info_path, "r", encoding="utf-8") as f:
        batch_jobs = json.load(f)

    print("\n" + "="*50)
    print("MONITORING BATCH JOBS")
    print("="*50)

    all_completed = False
    while not all_completed:
        all_completed = True
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")

        for job in batch_jobs:
            batch = check_batch_status(job["batch_id"])
            job["status"] = batch.status

            print(f"  {Path(job['file_path']).name}: {batch.status}")

            if batch.status in ["validating", "in_progress", "finalizing"]:
                all_completed = False
            elif batch.status == "completed":
                # Download if not already downloaded
                output_path = OUTPUT_DIR / f"batch_{job['batch_id']}_output.jsonl"
                if not output_path.exists():
                    download_batch_results(job["batch_id"], output_path)
                    job["output_path"] = str(output_path)
            elif batch.status == "failed":
                print(f"    ⚠ Batch failed!")

        if not all_completed:
            print("\n  Waiting 60 seconds before next check...")
            time.sleep(60)

    print("\n✓ All batches completed!")
    
    # Update batch info file
    with open(batch_info_path, "w", encoding="utf-8") as f:
        json.dump(batch_jobs, f, indent=2, ensure_ascii=False, default=str)


def save_results_to_mongodb(output_files):
    """Process batch output files and save results to MongoDB."""
    print("\n" + "="*50)
    print("SAVING RESULTS TO MONGODB")
    print("="*50)

    # Connect to MongoDB
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    
    # Create/get rewritten sentences collection
    sentences_collection = db[PROCESS_COLLECTION_NAME]
    sections_collection = db[SECTION_COLLECTION_NAME]
    
    total_inserted = 0
    total_updated = 0
    total_missing = 0

    for output_file in output_files:
        if not Path(output_file).exists():
            print(f"⚠ Output file not found: {output_file}")
            continue

        print(f"\nProcessing: {Path(output_file).name}")
        
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in tqdm(lines, desc="  Processing entries"):
            try:
                data = json.loads(line)
                
                # Check response status
                if data.get("response", {}).get("status_code") != 200:
                    continue

                # Extract content
                content = data["response"]["body"]["choices"][0]["message"]["content"]
                content = content.strip()
                
                # Split into sentences
                sentences = [s.strip() for s in content.split("\n") if s.strip()]
                
                section_id = data["custom_id"]
                
                # Get original section info from MongoDB
                from bson import ObjectId
                
                try:
                    original_section = sections_collection.find_one({"_id": ObjectId(section_id)})
                except:
                    # If not ObjectId, try as string
                    original_section = sections_collection.find_one({"_id": section_id})
                
                if not original_section:
                    total_missing += 1
                    continue

                so_hieu = original_section.get("so_hieu", "unknown")
                title = original_section.get("title", "")
                full_path = original_section.get("full_path", "")
                
                # Insert or update sentences
                for seq, sentence in enumerate(sentences, start=1):
                    doc = {
                        "section_id": section_id,
                        "so_hieu": so_hieu,
                        "title": title,
                        "full_path": full_path,
                        "sequence": seq,
                        "content": sentence,
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    result = sentences_collection.update_one(
                        {"section_id": section_id, "sequence": seq},
                        {"$set": doc, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
                        upsert=True
                    )
                    
                    if result.upserted_id:
                        total_inserted += 1
                    elif result.modified_count > 0:
                        total_updated += 1
                    
            except Exception as e:
                print(f"    ⚠ Error processing line: {e}")
                continue

    mongo_client.close()
    
    print(f"\n{'='*50}")
    print("MONGODB SAVE COMPLETE")
    print(f"{'='*50}")
    print(f"Sentences inserted : {total_inserted}")
    print(f"Sentences updated  : {total_updated}")
    print(f"Missing sections   : {total_missing}")


def main():
    """Main execution flow - process each batch sequentially."""
    print("="*50)
    print("CHATGPT BATCH API - LEGAL DOCUMENT PROCESSING")
    print("="*50)

    # Step 1: Extract data from MongoDB
    diem_data = extract_diem_data_from_mongodb()

    # Step 2: Create batch files
    file_paths = create_batch_files(diem_data)

    # Step 3: Process each batch sequentially
    total_parts = len(file_paths)
    all_results = []
    
    for idx, file_path in enumerate(file_paths, start=1):
        result = submit_and_monitor_single_batch(file_path, idx, total_parts)
        if result:
            all_results.append(result)
            
            # Save progress after each batch
            progress_path = OUTPUT_DIR / f"batch_progress_latest.json"
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Progress saved to: {progress_path.name}\n")
        else:
            print(f"  ⚠ Part {idx} had issues, continuing to next part...\n")

    # Final summary
    print(f"\n{'='*50}")
    print("ALL BATCHES COMPLETE")
    print(f"{'='*50}")
    print(f"\nTotal parts processed: {len(all_results)}/{total_parts}")
    print(f"Successful: {sum(1 for r in all_results if r.get('status') == 'completed')}")
    print(f"Failed: {sum(1 for r in all_results if r.get('status') == 'failed')}")
    
    # Save final results
    final_path = OUTPUT_DIR / f"batch_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nFinal results saved to: {final_path.name}")
    
    # Step 4: Save to MongoDB if all results available
    completed_results = [r for r in all_results if r.get("status") == "completed"]
    if len(completed_results) == total_parts:
        output_files = [r["output_path"] for r in completed_results if r.get("output_path")]
        if output_files:
            save_results_to_mongodb(output_files)
        else:
            print("\n⚠ No output files to save to MongoDB")
    else:
        print(f"\n⚠ Not all batches completed ({len(completed_results)}/{total_parts}), skipping MongoDB save")
        print("  Run script again to resume incomplete batches")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        if len(sys.argv) < 3:
            print("Usage: python run_batch_api.py --monitor <batch_info_path>")
            sys.exit(1)
        monitor_batches(sys.argv[2])
    else:
        main()
