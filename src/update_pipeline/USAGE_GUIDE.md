# Quick Start Guide - Legal Document Pipeline

## How to Use the Pipeline

### Option 1: GUI Mode (Easiest - Recommended for First Time)

1. **Open Command Prompt/Terminal** in the project directory:
   ```bash
   cd E:\Github\LawAssistant
   ```

2. **Run the pipeline**:
   ```bash
   python src\update_pipeline\add_document_pipeline.py
   ```
   Or explicitly:
   ```bash
   python src\update_pipeline\add_document_pipeline.py --gui
   ```

3. **Fill in the form** that appears:
   - **Document ID**: Enter the document identifier (e.g., `01/2013/QH13`)
   - **Document Title**: Enter the full title (e.g., `Luật Đất Đai 2013`)
   - **Effective Date**: Enter date in format `YYYY-MM-DD` (e.g., `2013-11-29`)

4. **Add your files**:
   - Click "Add Files" button
   - Select your PDF, DOC, or DOCX files
   - You can add multiple files for the same document
   - Click "Remove" to remove a selected file
   - Click "Clear All" to remove all files

5. **Start processing**:
   - Click "Start Processing" button
   - A confirmation dialog will appear - click "Yes" to proceed
   - Watch the status window for progress updates
   - Processing may take from minutes to hours depending on document size

6. **Wait for completion**:
   - The status window will show progress through all 3 steps
   - A success dialog will appear when done
   - If errors occur, detailed error messages will be displayed

---

### Option 2: CLI Mode (Command Line)

1. **Open Command Prompt/Terminal**:
   ```bash
   cd E:\Github\LawAssistant
   ```

2. **Run the pipeline in CLI mode**:
   ```bash
   python src\update_pipeline\add_document_pipeline.py --cli
   ```

3. **Answer the prompts**:
   ```
   Document ID (so_hieu) [e.g., 01/2013/QH13]: 45/2013/QH13
   Document title: Luật Đất Đai 2013
   Effective date (YYYY-MM-DD): 2013-11-29
   
   File paths (enter one per line, empty line to finish):
   File 1: E:\Documents\luat_dat_dai.pdf
   File 2: E:\Documents\phu_luc.docx
   File 3: [Press Enter with no input to finish]
   ```

4. **Confirm and start**:
   ```
   Proceed with processing? (yes/no): yes
   ```

5. **Monitor progress** in the console output

---

## Step-by-Step Example

### Example: Adding "Luật Đất Đai 2013"

**Scenario**: You have a legal document about land law with 2 files:
- Main document: `luat_dat_dai_2013.pdf` (200 pages)
- Appendix: `phu_luc.docx` (50 pages)

**Steps**:

1. **Prepare your files** in a folder (e.g., `E:\Documents\legal\`)

2. **Check MongoDB is running**:
   ```bash
   # In a separate terminal
   mongod --dbpath E:\data\mongodb
   ```

3. **Run the GUI**:
   ```bash
   cd E:\Github\LawAssistant
   python src\update_pipeline\add_document_pipeline.py
   ```

4. **Fill in the form**:
   - Document ID: `45/2013/QH13`
   - Title: `Luật Đất Đai 2013`
   - Effective Date: `2013-11-29`

5. **Add files**:
   - Click "Add Files"
   - Navigate to `E:\Documents\legal\`
   - Select both `luat_dat_dai_2013.pdf` and `phu_luc.docx`
   - Click Open

6. **Start processing**:
   - Click "Start Processing"
   - Confirm when prompted

7. **Watch progress** (estimated time: 2-4 hours):
   ```
   Step 1: Document Extraction (5-15 minutes)
   ✓ Checking for duplicates
   ✓ Extracting PDF (OCR)
   ✓ Extracting DOCX
   ✓ Parsing into sections
   
   Step 2: Sentence Simplification (1-24 hours)
   ✓ Creating batch tasks
   ✓ Submitting to OpenAI
   ⏳ Waiting for batch completion...
   ✓ Processing results
   
   Step 3: Triplet Extraction (30-60 minutes)
   ✓ Extracting knowledge triplets
   ✓ Saving to database
   ```

8. **Success!**:
   ```
   Document processed successfully!
   Document: 45/2013/QH13
   Triplets: 2,547
   Time: 123.4 minutes
   ```

---

## What Each Step Does

### Step 1: Document Extraction (5-15 minutes)
- Checks if document already exists (stops if duplicate)
- Extracts text from all your files
- Combines text from multiple files
- Parses document structure (chapters, articles, sections)
- Saves to MongoDB

**You'll see**:
```
STEP 1: Document Text Extraction
Checking for existing document with so_hieu: 45/2013/QH13...
✓ No duplicate found

Processing luat_dat_dai_2013.pdf... ✓ Extracted 245,678 characters
Processing phu_luc.docx... ✓ Extracted 45,123 characters

Parsing document into sections...
✓ Total: 290,801 characters from 2 file(s)
✓ Parsed into 156 sections
✓ Saved to MongoDB
```

### Step 2: Sentence Simplification (1-24 hours)
- Breaks complex legal sentences into simple ones
- Uses OpenAI's Batch API (cost-effective)
- Waits for OpenAI to process (can take up to 24 hours)
- Saves simplified sentences to MongoDB

**You'll see**:
```
STEP 2: Sentence Simplification
Found 156 total sections, 78 leaf nodes
Collected 78 sections for simplification
Created 234 batch tasks

Submitting batch to OpenAI...
✓ Batch submitted: batch_xyz123
Status: validating

Waiting for batch to complete...
Status: in_progress - 50/234 completed
Status: in_progress - 150/234 completed
Status: completed - 234/234 completed

✓ Results downloaded
✓ Processed 1,247 simplified sentences
```

### Step 3: Triplet Extraction (30-60 minutes)
- Extracts knowledge graph triplets from sentences
- Uses Vietnamese NLP models
- Creates relationships between legal concepts
- Saves to MongoDB for querying

**You'll see**:
```
STEP 3: Triplet Extraction
Found 1,247 sentences to process

Processed: 100/1247 | Triplets: 345 | No triplets: 12 | Errors: 2
Processed: 200/1247 | Triplets: 723 | No triplets: 25 | Errors: 3
...
Processed: 1247/1247 | Triplets: 2,547 | No triplets: 156 | Errors: 8

✓ Extraction complete!
```

---

## Before You Start - Checklist

### ✅ Required:
- [ ] MongoDB is running
- [ ] `.env` file exists with:
  - `GOOGLE_APPLICATION_CREDENTIALS` (for PDF OCR)
  - `OPENAI_API_KEY` (for sentence simplification)
  - `MONGO_URI` (usually `mongodb://localhost:27017/`)
- [ ] NLP models are present:
  - [ ] `nlp_models/VnCoreNLP-1.2/`
  - [ ] `nlp_models/phonlp/`
- [ ] Dictionary files exist:
  - [ ] `listSameKey.txt`
  - [ ] `stopwords.csv`
- [ ] Your document files are ready (PDF/DOC/DOCX)

### ℹ️ Optional:
- [ ] Google Cloud Storage bucket (for PDF processing)
- [ ] Sufficient OpenAI API credits
- [ ] Free disk space for temporary files

---

## Common Commands

### Start GUI:
```bash
python src\update_pipeline\add_document_pipeline.py
```

### Start CLI:
```bash
python src\update_pipeline\add_document_pipeline.py --cli
```

### Check MongoDB is running:
```bash
# Windows
tasklist | findstr mongod

# Linux/Mac
ps aux | grep mongod
```

### Start MongoDB:
```bash
# Windows
mongod --dbpath E:\data\mongodb

# Linux/Mac
mongod --dbpath /data/db
```

### View MongoDB data:
```bash
# Open MongoDB shell
mongo

# Switch to database
use KB_PROPERTY_LAW

# View documents
db.extracted_documents.find().pretty()
db.legal_sections.count()
db.processed_legal_sections.count()
```

---

## Tips for Success

### 1. **File Preparation**
- Use clear, descriptive filenames
- Ensure files are not corrupted
- Test with a small document first

### 2. **Document ID (so_hieu)**
- Use a unique identifier
- Common format: `XX/YYYY/QHN` (e.g., `45/2013/QH13`)
- Cannot duplicate existing documents

### 3. **Processing Time**
- Small docs (10-20 pages): 5-30 minutes
- Medium docs (50-100 pages): 30 min - 2 hours
- Large docs (200+ pages): 2-24 hours
- Most time is spent on Step 2 (OpenAI batch processing)

### 4. **Cost Estimates**
- OpenAI Batch API: ~50% cheaper than regular API
- Typical document: $0.50 - $5.00 depending on size
- PDF OCR with Google Vision: ~$1.50 per 1,000 pages

### 5. **If Something Goes Wrong**
- Check the error message carefully
- Review the status log in GUI mode
- See README.md "Troubleshooting" section
- Most common issue: MongoDB not running

---

## What Happens to Your Data

### MongoDB Collections Created:

1. **extracted_documents**
   - Raw extracted text from your files
   - Metadata (title, date, source files)

2. **legal_sections**
   - Parsed document structure
   - Chapters, articles, sections, clauses
   - Hierarchical relationships

3. **processed_legal_sections**
   - Simplified sentences
   - Ready for triplet extraction

4. **triplets** (or similar - depends on your setup)
   - Knowledge graph triplets
   - Subject-Relation-Object format
   - Used for legal queries

### Files Created:

- `pipeline_output/batch_*.jsonl` - OpenAI batch input
- `pipeline_output/results_*.jsonl` - OpenAI batch results
- Temporary conversion files (auto-cleaned)

---

## Need Help?

### Error Messages
- All errors include suggestions for fixing
- Check README.md "Troubleshooting" section
- Review status log for details

### Testing
Start with a small document (5-10 pages) to:
- Verify setup is correct
- Understand the process
- Estimate time for larger documents

### Support Files
- **README.md** - Full documentation
- **add_document_pipeline.py** - The main script
- Log files in `logs/` directory

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Start GUI | `python src\update_pipeline\add_document_pipeline.py` |
| Start CLI | `python src\update_pipeline\add_document_pipeline.py --cli` |
| Check MongoDB | `tasklist \| findstr mongod` (Windows) |
| Start MongoDB | `mongod --dbpath <path>` |
| View database | `mongo` then `use KB_PROPERTY_LAW` |
| Check status | Look at status window (GUI) or console (CLI) |

---

## That's It!

You're ready to start adding legal documents to your knowledge graph. Start with the GUI mode for the easiest experience!

For more details, see the full **README.md** in the same directory.
