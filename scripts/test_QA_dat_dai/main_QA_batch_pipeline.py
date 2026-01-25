import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path

import phonlp
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

from src.db import init_mongo
from src.retrieval.retrieval_pipeline import RetrievalPipeline
from src.retrieval.utils.print_result import format_results_for_llm
from src.triplet_extraction.pos_taging import init_vncorenlp


CURRENT_DIR = os.getcwd()
BASE_DIR = r"E:\Github\LawAssistant"
print(f"Working directory: {CURRENT_DIR}")
print(f"Base directory set to: {BASE_DIR}\n")

# Batch API Configuration
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
mongo_client = init_mongo(MONGODB_URI)
vncorenlp_client = init_vncorenlp(rf"{BASE_DIR}\nlp_models\VnCoreNLP-1.2")
phonlp_model = phonlp.load(save_dir=rf"{BASE_DIR}\nlp_models\phonlp")
MODEL_NAME = "gpt-4.1"
MAX_FILE_TOKENS = 1_500_000
MAX_TASK_TOKENS = 400_000
OUTPUT_DIR = Path(__file__).parent
BATCH_PREFIX = "batch_qa_pipeline"

# Initialize OpenAI client and tokenizer
client = OpenAI(api_key=API_KEY)
encoding = tiktoken.get_encoding("cl100k_base")

def prepare_QA_prompt(question, context):
    """Create system and user prompts for legal advisory QA task."""
    system_prompt = """
Bạn là trợ lý AI chuyên về tư vấn pháp luật. Nhiệm vụ của bạn là đưa ra CÂU TRẢ LỜI MANG TÍNH HƯỚNG DẪN – KHUYẾN NGHỊ
dựa HOÀN TOÀN trên NGỮ CẢNH được cung cấp.

HƯỚNG DẪN THỰC HIỆN:
- Bước 1: Đọc kỹ toàn bộ NGỮ CẢNH.
- Bước 2: Xác định các quy định pháp luật liên quan trực tiếp đến câu hỏi.
- Bước 3: Diễn giải lại nội dung theo cách dễ hiểu, có thể kèm theo lời khuyên về cách áp dụng trong thực tế.
- Bước 4: Khi nêu căn cứ, phải trích dẫn rõ ràng trong dấu ngoặc (ví dụ: điều, khoản, văn bản).
- Bước 5: Nếu có nhiều văn bản, ưu tiên văn bản có hiệu lực pháp lý cao hơn hoặc văn bản mới hơn.
- Bước 6: Nếu NGỮ CẢNH không đủ thông tin, không rõ trường hợp cụ thể, hoặc có mâu thuẫn:
    + Phải nêu rõ là thông tin chưa đủ hoặc chưa xác định được kết luận chính xác
    + KHÔNG được suy đoán hoặc bịa thêm nội dung
- Bước 7: Trong trường hợp không thể đưa ra câu trả lời chắc chắn, hãy hướng dẫn người hỏi liên hệ
    cơ quan nhà nước có thẩm quyền phù hợp (ví dụ: UBND, cơ quan thuế, văn phòng đăng ký đất đai, tòa án, cơ quan công an…).
- Bước 8: Cuối câu trả lời phải liệt kê rõ các nguồn pháp lý đã sử dụng từ NGỮ CẢNH.

QUY TẮC BẮT BUỘC:
- Chỉ sử dụng thông tin có trong NGỮ CẢNH.
- Không sử dụng kiến thức bên ngoài.
- Không trích dẫn nguyên văn quá dài; phải tóm tắt, diễn giải.
- Trả lời bằng tiếng Việt rõ ràng, trung lập, dễ hiểu.
- Câu trả lời mang tính tham khảo, hướng dẫn, không khẳng định thay cho cơ quan có thẩm quyền.
"""

    user_prompt = f"""
NGỮ CẢNH PHÁP LÝ:
{context}

CÂU HỎI:
{question}

Hãy trả lời theo hướng tư vấn, khuyến nghị và tuân thủ đầy đủ các hướng dẫn đã nêu.
"""
    return system_prompt, user_prompt

def count_chat_tokens(messages):
    """Rough but safe token count for chat.completions"""
    tokens = 0
    for msg in messages:
        tokens += 4  # role + formatting overhead
        tokens += len(encoding.encode(msg["content"]))
    tokens += 2  # assistant reply priming
    return tokens


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


def create_batch_files_from_questions(questions_file_path, top_k=5):
    """Create JSONL batch files from questions."""
    print("="*50)
    print("CREATING BATCH FILES FROM QUESTIONS")
    print("="*50)
    
    # Read questions
    questions = []
    with open(questions_file_path, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            questions.append(obj["question"])
    
    print(f"Loaded {len(questions)} questions\n")

    # Create pipeline with custom settings
    pipeline = RetrievalPipeline(
        # Query preprocessing config
        openai_api_key=API_KEY,
        openai_model="gpt-4.1-mini",
        dictionary_path=rf"{BASE_DIR}\src\retrieval\preprocess_query\dictionary.json",

        # Graph retrieval config
        mongo_client=mongo_client,
        db_name="KB_PROPERTY_LAW",
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,

        # Semantic retrieval config
        semantic_index_dir=rf"{BASE_DIR}\src\retrieval\semantic\search_index",
        semantic_embedding_model="bkai-foundation-models/vietnamese-bi-encoder",

        # DPR config
        dpr_model_name="VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
        use_dpr=True,

        # Enable/disable components
        use_query_preprocessing=True,
        use_graph_retrieval=True,
        use_semantic_retrieval=True,

        # Graph traversal depth
        k_hops=1,

        # Custom scoring weights (will be normalized)
        graph_weight=0.3,
        semantic_weight=0.3,
        dpr_weight=0.4
    )

    # Process each question to get context and create tasks
    tasks = []
    
    for i, question in enumerate(tqdm(questions, desc="Processing questions")):
        try:
            # Run retrieval pipeline to get context
            results = pipeline.retrieve(question, top_k=top_k)
            contexts = format_results_for_llm(results)
            
            # Create prompt
            system_prompt, user_prompt = prepare_QA_prompt(question, contexts)
            
            # Create task
            task = {
                "custom_id": f"question_{i+1}",
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
            
            # Count tokens
            tokens = count_chat_tokens(task["body"]["messages"])
            
            if tokens > MAX_FILE_TOKENS:
                print(f"\n⚠ Question {i+1} exceeds 2M tokens ({tokens}), skipping")
                continue
            
            task["_token_count"] = tokens
            task["_question"] = question
            tasks.append(task)
            
        except Exception as e:
            print(f"\n⚠ Error processing question {i+1}: {e}")
            continue
    
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
                task_copy.pop("_question", None)
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


def submit_and_monitor_single_batch(file_path, part_num, total_parts):
    """Submit a single batch file and monitor until completion."""
    print(f"\n{'='*50}")
    print(f"PROCESSING PART {part_num}/{total_parts}: {file_path.name}")
    print(f"{'='*50}")

    # Check if output already exists
    output_path = OUTPUT_DIR / f"batch_part{part_num}_output.jsonl"
    if output_path.exists():
        print(f"  ✓ Output file already exists: {output_path.name}")
        return {
            "part": part_num,
            "file_path": str(file_path),
            "status": "completed",
            "output_path": str(output_path),
            "resumed": True
        }

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
            "description": f"QA Pipeline - Part {part_num}/{total_parts}"
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
            print(f"  → Downloading results...")
            
            if batch.output_file_id:
                file_response = client.files.content(batch.output_file_id)
                with open(output_path, "wb") as f:
                    f.write(file_response.content)
                print(f"  ✓ Results saved to: {output_path.name}")
                
                return {
                    "part": part_num,
                    "file_path": str(file_path),
                    "file_id": batch_input_file.id,
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
                "file_id": batch_input_file.id,
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


def save_results_to_file(output_files):
    """Process batch output files and save Q&A results to a text file."""
    print("\n" + "="*50)
    print("SAVING RESULTS TO FILE")
    print("="*50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"qa_results_{timestamp}.txt"
    
    with open(results_file, "w", encoding="utf-8") as out_f:
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
                    answer = data["response"]["body"]["choices"][0]["message"]["content"]
                    answer = answer.strip()
                    
                    custom_id = data["custom_id"]
                    
                    # Write to file
                    out_f.write(f"\n{'='*70}\n")
                    out_f.write(f"ID: {custom_id}\n")
                    out_f.write(f"{'='*70}\n")
                    out_f.write(f"{answer}\n")
                    
                except Exception as e:
                    print(f"    ⚠ Error processing line: {e}")
                    continue
    
    print(f"\n✓ Results saved to: {results_file.name}")
    return results_file

def save_results_to_csv(output_files):
    """Process batch output files and save Q&A results to a CSV file."""
    print("\n" + "=" * 50)
    print("SAVING RESULTS TO CSV")
    print("=" * 50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"qa_results_{timestamp}.csv"

    with open(results_file, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.writer(out_f)

        # CSV header
        writer.writerow(["id", "answer"])

        for output_file in output_files:
            output_file = Path(output_file)

            if not output_file.exists():
                print(f"⚠ Output file not found: {output_file}")
                continue

            print(f"\nProcessing: {output_file.name}")

            with open(output_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in tqdm(lines, desc="  Processing entries"):
                try:
                    data = json.loads(line)

                    # Check response status
                    if data.get("response", {}).get("status_code") != 200:
                        continue

                    answer = (
                        data["response"]["body"]["choices"][0]["message"]["content"]
                        .strip()
                    )

                    custom_id = data.get("custom_id", "")

                    writer.writerow([custom_id, answer])

                except Exception as e:
                    print(f"    ⚠ Error processing line: {e}")
                    continue

    print(f"\n✓ Results saved to: {results_file.name}")
    return results_file

def main():
    """Main execution flow - process questions with batch API."""
    print("="*50)
    print("CHATGPT BATCH API - QA PIPELINE")
    print("="*50)

    # Step 1: Read questions and create batch files
    question_file_path = rf"{BASE_DIR}\data\facebook_questions.jsonl"
    file_paths = create_batch_files_from_questions(question_file_path, top_k=10)

    if not file_paths:
        print("\nNo batch files created. Exiting.")
        return

    # file_paths = [
    #     r"E:\Github\LawAssistant\scripts\batch_qa_pipeline_20260114_065327_part1.jsonl",
    #     r"E:\Github\LawAssistant\scripts\batch_qa_pipeline_20260114_065327_part2.jsonl",
    #     r"E:\Github\LawAssistant\scripts\batch_qa_pipeline_20260114_065327_part3.jsonl"
    # ]

    # Step 2: Process each batch sequentially
    total_parts = len(file_paths)
    all_results = []
    
    for idx, file_path in enumerate(file_paths, start=1):
        result = submit_and_monitor_single_batch(Path(file_path), idx, total_parts)
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
    
    # Step 3: Save Q&A results to text file
    completed_results = [r for r in all_results if r.get("status") == "completed"]
    if len(completed_results) == total_parts:
        output_files = [r["output_path"] for r in completed_results if r.get("output_path")]
        if output_files:
            # save_results_to_file(output_files)
            save_results_to_csv(output_files)
        else:
            print("\n⚠ No output files to save")
    else:
        print(f"\n⚠ Not all batches completed ({len(completed_results)}/{total_parts}), skipping file save")
        print("  Run script again to resume incomplete batches")


if __name__ == "__main__":
    main()