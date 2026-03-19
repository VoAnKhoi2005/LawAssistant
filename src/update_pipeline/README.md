# Legal Document Processing Pipeline

A unified pipeline for adding new legal documents to the Knowledge Graph. This script integrates three processing steps:

1. **Document Extraction** - Extract text from PDF/DOC/DOCX files
2. **Sentence Simplification** - Simplify complex legal sentences using GPT
3. **Triplet Extraction** - Extract knowledge graph triplets from simplified sentences

## Prerequisites

### Required Environment Variables

Create a `.env` file in the project root with:

```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
OPENAI_API_KEY=your-openai-api-key
MONGO_URI=mongodb://localhost:27017/
```

### Required Dependencies

- Python 3.8+
- MongoDB running locally
- All dependencies from `requirements.txt`
- NLP models in `nlp_models/` directory:
  - `VnCoreNLP-1.2/`
  - `phonlp/`
- Synonym dictionary: `listSameKey.txt`
- Stopwords file: `stopwords.csv`

## Usage

### GUI Mode (Default)

Run with graphical interface:

```bash
python src/update_pipeline/add_document_pipeline.py
```

Or explicitly:

```bash
python src/update_pipeline/add_document_pipeline.py --gui
```

**GUI Features:**
- Form-based input for document metadata
- File browser for selecting documents
- Real-time status updates
- Progress tracking

**Steps:**
1. Fill in document information:
   - Document ID (so_hieu): e.g., "01/2013/QH13"
   - Document Title: e.g., "Luật Đất Đai"
   - Effective Date: YYYY-MM-DD format
2. Add document files (PDF/DOC/DOCX)
3. Click "Start Processing"
4. Wait for completion (may take several minutes to hours depending on document size)

### CLI Mode

Run in command-line mode:

```bash
python src/update_pipeline/add_document_pipeline.py --cli
```

**Interactive prompts will ask for:**
1. Document ID (so_hieu)
2. Document title
3. Effective date (YYYY-MM-DD)
4. File paths (one per line, empty line to finish)

**Example:**
```
Document ID (so_hieu) [e.g., 01/2013/QH13]: 45/2013/QH13
Document title: Luật Đất Đai 2013
Effective date (YYYY-MM-DD): 2013-11-29

File paths (enter one per line, empty line to finish):
File 1: E:\Documents\luat_dat_dai.pdf
File 2: E:\Documents\phu_luc.docx
File 3: 

Proceed with processing? (yes/no): yes
```

## Pipeline Steps

### Step 1: Document Extraction

**What it does:**
- **Checks for duplicate documents** - Stops immediately if so_hieu already exists
- Extracts text from PDF/DOC/DOCX files
- Combines text from multiple files
- Parses document structure (chapters, articles, sections)
- Saves to MongoDB collections:
  - `extracted_documents` - Raw extracted text
  - `legal_sections` - Parsed document structure

**Duplicate Detection:**
The pipeline will stop immediately with an error if a document with the same `so_hieu` already exists in the database. This prevents accidental overwriting of existing documents.

**Supported formats:**
- PDF (using Google Vision OCR)
- DOCX (using python-docx)
- DOC (converted to DOCX automatically)

### Step 2: Sentence Simplification

**What it does:**
- Retrieves document sections from MongoDB
- Creates GPT batch tasks for sentence simplification
- Submits to OpenAI Batch API
- Waits for completion and downloads results
- Saves simplified sentences to `processed_legal_sections` collection

**Note:** This step uses OpenAI's Batch API which is cost-effective but may take up to 24 hours. The script will wait and poll for completion.

### Step 3: Triplet Extraction

**What it does:**
- Processes simplified sentences
- Extracts knowledge graph triplets (subject, relation, object)
- Uses Vietnamese NLP models (VnCoreNLP, PhoNLP)
- Applies synonym normalization
- Saves triplets to MongoDB (collection depends on `insert_triplet_batch_mongo` implementation)

**Example triplet:**
```
("Hành vi làm sai lệch sơ đồ", "là", "hành vi vi phạm quy định về hồ sơ địa giới")
```

## Output

### MongoDB Collections

1. **extracted_documents**
   ```json
   {
     "so_hieu": "01/2013/QH13",
     "title": "Luật Đất Đai",
     "effective_date": "2013-11-29",
     "source_files": "file1.pdf, file2.docx",
     "combined_text": "...",
     "text_length": 123456
   }
   ```

2. **legal_sections**
   ```json
   {
     "_id": "01/2013/QH13_Dieu_1",
     "so_hieu": "01/2013/QH13",
     "type": "điều",
     "content": "...",
     "parent_id": "...",
     "document_title": "Luật Đất Đai",
     "effective_date": "2013-11-29"
   }
   ```

3. **processed_legal_sections**
   ```json
   {
     "section_id": "01/2013/QH13_Dieu_1",
     "sequence": 1,
     "so_hieu": "01/2013/QH13",
     "content": "Simplified sentence..."
   }
   ```

### Files Created

- `pipeline_output/batch_*.jsonl` - Batch input files for OpenAI
- `pipeline_output/results_*.jsonl` - Batch results from OpenAI
- Temporary conversion files (automatically cleaned up)

## Error Handling

The pipeline includes comprehensive error handling with detailed error messages:

### Immediate Stop Conditions
- **Duplicate document detected** - Stops before any processing if so_hieu already exists
- **MongoDB connection failure** - Cannot proceed without database
- **NLP models not found** - Required for triplet extraction
- **No text extracted** - At least one file must be successfully processed

### Detailed Error Messages
All errors provide:
- Clear description of what went wrong
- Which step failed (initialization, extraction, simplification, or triplet extraction)
- Specific error details (file names, API errors, etc.)
- Suggestions for resolution

### Error Display
- **CLI Mode**: Errors printed to console with clear formatting
- **GUI Mode**: 
  - Error dialogs with detailed messages
  - Full error log in status window
  - Stack traces for debugging

### Error Categories

**1. Duplicate Document Error**
```
DUPLICATE DOCUMENT ERROR: A document with so_hieu '01/2013/QH13' already exists in the database.
Existing document title: Luật Đất Đai
Effective date: 2013-11-29
Please use a different so_hieu or remove the existing document first.
```

**2. File Processing Errors**
- File not found
- Unsupported file format
- DOC to DOCX conversion failure
- OCR extraction failure
- PDF processing errors

**3. API Errors**
- OpenAI API key missing or invalid
- Batch submission failure
- Batch processing timeout (24 hours)
- Google Vision API errors

**4. MongoDB Errors**
- Connection failure
- Write operation failure
- Collection access errors

**5. Configuration Errors**
- Missing environment variables
- Invalid file paths
- Missing NLP models

### Error Recovery
- File-level errors: Pipeline continues with remaining files
- Sentence-level errors: Logged but processing continues
- Critical errors: Pipeline stops immediately with detailed message

## Performance

**Typical processing times:**
- Small document (10-20 pages): 5-30 minutes
- Medium document (50-100 pages): 30 minutes - 2 hours
- Large document (200+ pages): 2-24 hours

**Bottlenecks:**
- Step 1: PDF OCR (if documents are scanned images)
- Step 2: OpenAI Batch API (24-hour completion window)
- Step 3: NLP processing (depends on sentence count)

## Troubleshooting

### Common Issues

**1. Duplicate Document Error**
```
DUPLICATE DOCUMENT ERROR: A document with so_hieu '01/2013/QH13' already exists
```
**Solution:**
- Use a different so_hieu for the new document
- Or remove the existing document: `db.extracted_documents.deleteOne({"so_hieu": "01/2013/QH13"})`
- Or check if you're trying to re-process the same document

**2. MongoDB Connection Error**
```
MongoDB initialization failed: Failed to connect to MongoDB
```
**Solution:**
- Ensure MongoDB is running: `mongod --dbpath <path>`
- Check MONGO_URI in .env file
- Verify MongoDB is accessible on localhost:27017

**3. Google Vision OCR Error**
```
Failed to save extracted document to MongoDB: GOOGLE_APPLICATION_CREDENTIALS not set
```
**Solution:**
- Set GOOGLE_APPLICATION_CREDENTIALS in .env file
- Verify the credential file path exists
- Check GCS bucket permissions

**4. OpenAI API Error**
```
Failed to create batch job: Invalid API key
```
**Solution:**
- Verify OPENAI_API_KEY in .env file
- Check API key is valid and has quota
- Ensure you have access to Batch API

**5. NLP Model Not Found**
```
NLP models initialization failed: VnCoreNLP initialization returned None
```
**Solution:**
- Ensure `nlp_models/VnCoreNLP-1.2/` directory exists
- Ensure `nlp_models/phonlp/` directory exists
- Download models if missing

**6. No Text Extracted**
```
TEXT EXTRACTION FAILED: No text was extracted from any files
```
**Solution:**
- Check file paths are correct
- Verify files are valid PDF/DOC/DOCX
- Check file permissions
- Review extraction errors in the log

**7. Tkinter Import Error (GUI mode)**
```
Error: tkinter not available
```
**Solution:**
- Use `--cli` mode instead
- Or install tkinter:
  - Ubuntu: `sudo apt-get install python3-tk`
  - Windows: Included in standard Python installation

## Advanced Usage

### Processing Multiple Documents

Create a batch script:

```python
from add_document_pipeline import DocumentPipeline

pipeline = DocumentPipeline()
pipeline.initialize()

documents = [
    {
        "so_hieu": "01/2013/QH13",
        "title": "Luật Đất Đai",
        "effective_date": "2013-11-29",
        "files": ["file1.pdf"]
    },
    {
        "so_hieu": "45/2019/QH14",
        "title": "Luật Đầu Tư",
        "effective_date": "2019-06-01",
        "files": ["file2.pdf"]
    }
]

for doc in documents:
    result = pipeline.run_full_pipeline(doc)
    print(f"Processed {doc['so_hieu']}: {result['success']}")
```

### Running Individual Steps

```python
from add_document_pipeline import DocumentPipeline

pipeline = DocumentPipeline()
pipeline.initialize()

document_info = {
    "so_hieu": "01/2013/QH13",
    "title": "Luật Đất Đai",
    "effective_date": "2013-11-29",
    "files": ["file.pdf"]
}

# Run only Step 1
so_hieu = pipeline.step1_extract_document(document_info)

# Run only Step 2 (requires Step 1 data in MongoDB)
so_hieu = pipeline.step2_simplify_sentences("01/2013/QH13")

# Run only Step 3 (requires Step 2 data in MongoDB)
stats = pipeline.step3_extract_triplets("01/2013/QH13")
```

## Configuration

Default configuration can be modified in the `_load_config()` method:

- `model_name`: OpenAI model for simplification (default: "gpt-4o-mini")
- `max_file_tokens`: Max tokens per batch file (default: 2,000,000)
- `max_task_tokens`: Max tokens per task (default: 500,000)
- `db_name`: MongoDB database name (default: "KB_PROPERTY_LAW")

## License

This is part of the LawAssistant project.
