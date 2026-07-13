# `src/update_pipeline`

This folder is the experimental document ingestion pipeline used from `src/`. It can be run directly from the terminal, but it should be treated as a developer workflow rather than the backend production path.

## Setup

Run commands from the repository root:

```bash
cd /path/to/LawAssistant
```

Create a root `.env` from the example in this folder:

```bash
cp src/update_pipeline/.env.example .env
```

Required local files:

- `nlp_models/VnCoreNLP-1.2/`
- `nlp_models/phonlp/`
- `listSameKey.txt`
- `stopwords.csv`

Required services:

- MongoDB
- OpenAI API access
- Google Vision / GCS credentials for PDF OCR

## Recommended Entry Point

Use the integrated pipeline:

```bash
python3 src/update_pipeline/add_document_pipeline.py --step full \
  --so-hieu "45/2013/QH13" \
  --title "Luật Đất Đai 2013" \
  --effective-date "2013-11-29" \
  --file "/abs/path/luat_dat_dai.pdf" \
  --file "/abs/path/phu_luc.docx"
```

This runs:

1. document extraction
2. sentence simplification
3. triplet extraction

## Step-by-Step Commands

Step 1:

```bash
python3 src/update_pipeline/document_extraction.py \
  --so-hieu "45/2013/QH13" \
  --title "Luật Đất Đai 2013" \
  --effective-date "2013-11-29" \
  --file "/abs/path/luat_dat_dai.pdf"
```

Step 2:

```bash
python3 src/update_pipeline/simplify_sentences.py \
  --so-hieu "45/2013/QH13"
```

Step 3:

```bash
python3 src/update_pipeline/triplet_extraction.py \
  --so-hieu "45/2013/QH13"
```

You can also call the same steps through `add_document_pipeline.py`:

```bash
python3 src/update_pipeline/add_document_pipeline.py --step simplify --so-hieu "45/2013/QH13"
python3 src/update_pipeline/add_document_pipeline.py --step triplets --so-hieu "45/2013/QH13"
```

## Resume Behavior

The integrated pipeline now supports resume-oriented reruns:

- Step 1 skips if `extracted_documents` and `legal_sections` already exist for the document.
- Step 2 reuses:
  - the generated batch JSONL
  - saved batch metadata
  - downloaded result JSONL
- Step 3 skips if the pipeline state already marks it complete and triplets exist for that document.
- Per-document state files are written to `pipeline_output/state_<so_hieu>.json`.

Useful flags:

```bash
--force
--no-resume
--output-dir /custom/output/path
```

Use `--force` when you want to ignore saved state and rerun a step.

## Generated Artifacts

By default the pipeline writes to `pipeline_output/`:

- `batch_<so_hieu>.jsonl`
- `batch_<so_hieu>.meta.json`
- `results_<so_hieu>.jsonl`
- `state_<so_hieu>.json`

## Notes

- The GUI mode still exists:

```bash
python3 src/update_pipeline/add_document_pipeline.py
```

- The stage scripts are now thin wrappers around `add_document_pipeline.py`. If you change core behavior, update that file first.
