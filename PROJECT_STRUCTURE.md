# LawAssistant - Recommended Project Structure

## Current Issues
1. Inconsistent naming (`retrieval/` contains `semantic_retrieval/`)
2. Mix of development files in root (notebooks, test files, zip files)
3. No clear separation between source code, data, configs, and outputs
4. Multiple virtual environment directories (`.venv`, `venv`)
5. Credentials and temp files in project directories

## Recommended Structure

```
LawAssistant/
│
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── setup.py                        # Package installation script
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── docs/                           # Documentation
│   ├── RETRIEVAL_PIPELINE.md      # Pipeline documentation
│   ├── API.md                      # API documentation
│   ├── SETUP.md                    # Setup instructions
│   └── ARCHITECTURE.md             # System architecture
│
├── configs/                        # Configuration files
│   ├── retrieval_config.yaml      # Retrieval settings
│   ├── models_config.yaml         # Model configurations
│   └── database_config.yaml       # Database settings
│
├── src/                            # Main source code
│   ├── __init__.py
│   │
│   ├── core/                       # Core modules
│   │   ├── __init__.py
│   │   └── retrieval_pipeline.py  # Main unified pipeline
│   │
│   ├── preprocess/                 # Query preprocessing
│   │   ├── __init__.py
│   │   ├── query_preprocessor.py
│   │   ├── normalizer.py
│   │   └── llm_refiner.py
│   │
│   ├── retrieval/                  # Retrieval modules
│   │   ├── __init__.py
│   │   │
│   │   ├── graph/                  # Graph-based retrieval
│   │   │   ├── __init__.py
│   │   │   ├── retrieval_system.py
│   │   │   ├── bm25_ranker.py
│   │   │   ├── dpr_ranker.py
│   │   │   └── graph_traversal.py
│   │   │
│   │   └── semantic/               # Semantic retrieval
│   │       ├── __init__.py
│   │       ├── hybrid_search.py
│   │       ├── faiss_index.py
│   │       ├── bm25_index.py
│   │       ├── embedding_service.py
│   │       ├── text_processor.py
│   │       ├── models.py
│   │       └── config.py
│   │
│   ├── extraction/                 # Knowledge extraction
│   │   ├── __init__.py
│   │   ├── triplet_extraction.py
│   │   ├── entity_extraction.py
│   │   └── relation_extraction.py
│   │
│   ├── database/                   # Database operations
│   │   ├── __init__.py
│   │   ├── mongodb_client.py
│   │   ├── db_manager.py
│   │   └── schema.py
│   │
│   ├── scraper/                    # Web scraping
│   │   ├── __init__.py
│   │   ├── legal_scraper.py
│   │   └── parser.py
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── nlp_utils.py
│       ├── text_utils.py
│       └── logger.py
│
├── models/                         # NLP Models (gitignored)
│   ├── vncorenlp/
│   │   └── VnCoreNLP-1.2/
│   ├── phonlp/
│   └── custom_models/
│
├── data/                           # Data files (gitignored)
│   ├── raw/                        # Raw scraped data
│   │   ├── legal_documents/
│   │   └── qna_data/
│   │
│   ├── processed/                  # Processed data
│   │   ├── cleaned_documents/
│   │   └── extracted_triplets/
│   │
│   ├── dictionaries/               # Reference dictionaries
│   │   ├── abbreviations.json
│   │   ├── stopwords.csv
│   │   └── legal_terms.json
│   │
│   └── indexes/                    # Search indexes
│       ├── semantic_index/
│       └── graph_index/
│
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_retrieval_pipeline.py
│   ├── test_graph_retrieval.py
│   ├── test_semantic_retrieval.py
│   ├── test_preprocessing.py
│   └── fixtures/
│       └── sample_data.json
│
├── examples/                       # Usage examples
│   ├── basic_retrieval.py
│   ├── custom_pipeline.py
│   ├── batch_processing.py
│   └── api_usage.py
│
├── notebooks/                      # Jupyter notebooks
│   ├── exploration/
│   │   ├── data_analysis.ipynb
│   │   └── model_experiments.ipynb
│   │
│   ├── evaluation/
│   │   ├── retrieval_evaluation.ipynb
│   │   └── check_answer.ipynb
│   │
│   └── development/
│       ├── test_triplet_extraction.ipynb
│       └── test_google_ocr.ipynb
│
├── scripts/                        # Utility scripts
│   ├── build_index.py             # Build semantic index
│   ├── import_data.py             # Import to MongoDB
│   ├── extract_triplets.py        # Extract knowledge graph
│   ├── scrape_documents.py        # Scrape legal documents
│   └── export_results.py          # Export results
│
├── api/                            # API service (if applicable)
│   ├── __init__.py
│   ├── app.py                      # FastAPI/Flask app
│   ├── routes/
│   │   ├── retrieval.py
│   │   └── health.py
│   └── middleware/
│       └── auth.py
│
├── outputs/                        # Generated outputs (gitignored)
│   ├── logs/
│   ├── results/
│   └── evaluations/
│
└── deployment/                     # Deployment files
    ├── Dockerfile
    ├── docker-compose.yml
    ├── kubernetes/
    │   └── deployment.yaml
    └── requirements/
        ├── base.txt
        ├── dev.txt
        └── prod.txt
```

## Migration Plan

### Step 1: Restructure Source Code

```bash
# Create new directory structure
mkdir -p src/{core,preprocess,retrieval/{graph,semantic},extraction,database,scraper,utils}
mkdir -p docs configs tests examples notebooks/{exploration,evaluation,development}
mkdir -p scripts api outputs data/{raw,processed,dictionaries,indexes}
mkdir -p models deployment

# Move retrieval modules
mv retrieval_pipeline.py src/core/
mv preprocess_query/src/* src/preprocess/
mv graph/src/* src/retrieval/graph/
mv retrieval/semantic/src/* src/retrieval/semantic/

# Move extraction module
mv triplet_extraction/src/* src/extraction/

# Move data files
mv preprocess_query/dictionary.json data/dictionaries/
mv triplet_extraction/stopwords.csv data/dictionaries/
mv data/* data/raw/ 2>/dev/null || true

# Move models
mv triplet_extraction/nlp_models/* models/

# Move notebooks
mv check_answer.ipynb notebooks/evaluation/
mv triplet_extraction/*.ipynb notebooks/development/
mv scrape/*.ipynb notebooks/exploration/

# Move examples
mv example_retrieval.py examples/basic_retrieval.py
```

### Step 2: Update Import Paths

Update all imports from:
```python
from preprocess_query.src.query_preprocessor import QueryPreprocessor
from graph_retrieval.src.retrieval_system import retrieve_and_rank
from semantic_retrieval.src.hybrid_search import HybridSearchEngine
```

To:
```python
from src.preprocess.query_preprocessor import QueryPreprocessor
from src.retrieval.graph.retrieval_system import retrieve_and_rank
from src.retrieval.semantic.hybrid_search import HybridSearchEngine
```

### Step 3: Create Configuration Files

**configs/retrieval_config.yaml**
```yaml
retrieval:
  top_k: 20
  k_hops: 2
  weights:
    graph: 0.3
    semantic: 0.3
    dpr: 0.4

preprocessing:
  enabled: true
  openai_model: "gpt-4o-mini"
  dictionary_path: "data/dictionaries/abbreviations.json"

graph:
  enabled: true
  max_concepts: 500
  max_phrase_length: 3

semantic:
  enabled: true
  index_dir: "data/indexes/semantic_index"
  embedding_model: "bkai-foundation-models/vietnamese-bi-encoder"
  batch_size: 256

dpr:
  enabled: true
  model_name: "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
  use_fp16: true
```

**configs/models_config.yaml**
```yaml
models:
  vncorenlp:
    path: "models/vncorenlp/VnCoreNLP-1.2"
    annotators: ["wseg"]
  
  phonlp:
    path: "models/phonlp"
  
  embedding:
    model_name: "bkai-foundation-models/vietnamese-bi-encoder"
    dimension: 768
    device: "cuda"
```

**configs/database_config.yaml**
```yaml
mongodb:
  host: "localhost"
  port: 27017
  database: "KB_PROPERTY_LAW"
  collections:
    sections: "legal_sections"
    concepts: "concepts"
    relations: "relations"
    triplets: "triplets_new"
```

### Step 4: Create setup.py

```python
from setuptools import setup, find_packages

setup(
    name="law-assistant",
    version="1.0.0",
    description="Legal Document Retrieval System with Graph and Semantic Search",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pymongo>=4.0.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.4",
        "phonlp>=0.3.0",
        "vncorenlp>=1.0.3",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "gpu": [
            "faiss-gpu>=1.7.4",
        ]
    },
    python_requires=">=3.8",
)
```

### Step 5: Update .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
.venv/
env/
ENV/

# Models (large files)
models/
*.bin
*.pt
*.pth
*.onnx

# Data
data/raw/
data/processed/
data/indexes/
*.db
*.sqlite

# Outputs
outputs/
logs/
*.log

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Environment
.env
*.key
credentials.json

# Temporary files
*.zip
*.tar.gz
*.csv
*.xlsx
!requirements*.txt

# OS
.DS_Store
Thumbs.db

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Testing
.pytest_cache/
.coverage
htmlcov/
```

### Step 6: Create Package __init__ Files

**src/__init__.py**
```python
"""LawAssistant - Legal Document Retrieval System"""

__version__ = "1.0.0"

from src.core.retrieval_pipeline import RetrievalPipeline, create_pipeline

__all__ = ["RetrievalPipeline", "create_pipeline"]
```

**src/retrieval/__init__.py**
```python
"""Retrieval modules"""

from src.retrieval.graph.retrieval_system import retrieve_and_rank
from src.retrieval.semantic.hybrid_search import HybridSearchEngine

__all__ = ["retrieve_and_rank", "HybridSearchEngine"]
```

## Benefits of New Structure

### 1. **Clarity and Organization**
- Clear separation of concerns (preprocessing, retrieval, extraction)
- Easy to locate and modify specific components
- Standardized naming conventions

### 2. **Scalability**
- Easy to add new retrieval methods or features
- Modular design allows independent development
- Clear extension points for new functionality

### 3. **Development Workflow**
- Separate test files from source code
- Notebooks organized by purpose
- Development artifacts isolated

### 4. **Deployment Ready**
- Clean source structure for packaging
- Configuration externalized
- Docker/Kubernetes support

### 5. **Collaboration**
- Clear contribution guidelines
- Standard Python package structure
- Better IDE support and navigation

## Implementation Commands

```bash
# Create all directories
python scripts/create_structure.py

# Move files (use migration script)
python scripts/migrate_files.py

# Update imports
python scripts/update_imports.py

# Install package
pip install -e .

# Run tests
pytest tests/

# Build documentation
cd docs && make html
```

## Notes

1. **Large Files**: Keep models and data out of git (use Git LFS or external storage)
2. **Credentials**: Never commit `.env` files (use `.env.example` as template)
3. **Virtual Env**: Use only one venv directory (recommend `.venv`)
4. **Notebooks**: Keep experimental notebooks separate from production code
5. **Config Files**: Use YAML/JSON for configurations instead of hardcoded values

## Next Steps

1. Create migration script to automate file moves
2. Update all import statements
3. Create comprehensive tests
4. Set up CI/CD pipeline
5. Add API layer for serving predictions
6. Document all modules with docstrings
7. Create Docker container for deployment
