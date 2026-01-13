# Legal Document Retrieval System with BM25 Ranking

This system implements a comprehensive retrieval pipeline for legal documents using:
1. **Verb Extraction** - Extract main verbs from questions using PhoNLP
2. **Concept/Relation Matching** - Match entities and relationships in the question
3. **Triplet-based Retrieval** - Find relevant sections using knowledge graph triplets
4. **BM25 Ranking** - Rank sections by text relevance using BM25 algorithm
5. **Hybrid Scoring** - Combine BM25 and triplet scores for optimal results

## Architecture

```
Question → Verb Extraction → Concept/Relation Matching → Triplet Retrieval → BM25 Ranking → Results
```

### Components

#### 1. BM25 Ranker (`src/bm25_ranker.py`)
- Implements BM25 (Best Matching 25) algorithm
- Tokenizes Vietnamese text using VnCoreNLP
- Supports both pure BM25 and hybrid ranking
- Configurable parameters: k1 (term frequency saturation), b (document length normalization)

#### 2. Retrieval System (`src/retrieval_system.py`)
- Main pipeline orchestrator
- Extracts verbs from questions using PhoNLP dependency parsing
- Matches concepts and relations from knowledge base
- Retrieves candidate sections via triplet matching
- Ranks sections using BM25 or hybrid approach

## Usage

### Basic Example

```python
from graph_retrieval.src.retrieval_system import retrieve_and_rank, display_results
from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
import phonlp

# Initialize
mongo_client = init_mongo()
db = mongo_client["KB_PROPERTY_LAW"]
vncorenlp_client = init_vncorenlp("path/to/VnCoreNLP")
phoNLP_model = phonlp.load(save_dir="path/to/phonlp")

# Retrieve and rank
question = "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?"
results = retrieve_and_rank(
    question=question,
    vncorenlp_client=vncorenlp_client,
    phoNLP_model=phoNLP_model,
    sections_col=db["legal_sections"],
    concepts_col=db["concepts"],
    relations_col=db["relations"],
    triplets_col=db["triplets_new"],
    top_k=10,
    use_hybrid=True,
    bm25_weight=0.6,
    triplet_weight=0.4
)

# Display results
display_results(results, db["legal_sections"])
```

### Testing

#### Using Python Script
```bash
cd E:\Github\LawAssistant\retrieval
python main_retrieval.py
```

#### Using Jupyter Notebook
Open `test_bm25_ranking.ipynb` and run cells sequentially.

## BM25 Algorithm

BM25 (Best Matching 25) is a ranking function used in information retrieval. The score for a document D given a query Q is:

```
score(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))
```

Where:
- `qi` = query term i
- `f(qi, D)` = frequency of term qi in document D
- `|D|` = length of document D
- `avgdl` = average document length in corpus
- `k1` = term frequency saturation parameter (default: 1.5)
- `b` = length normalization parameter (default: 0.75)
- `IDF(qi)` = inverse document frequency of term qi

### Parameters

- **k1**: Controls how quickly term frequency saturates
  - Higher values (e.g., 2.0) = less saturation, more weight on term frequency
  - Lower values (e.g., 1.2) = faster saturation
  - Default: 1.5

- **b**: Controls document length normalization
  - b = 1: Full normalization (longer documents penalized)
  - b = 0: No normalization
  - Default: 0.75

## Hybrid Ranking

Combines two scoring approaches:

1. **BM25 Score**: Text-based relevance using keyword matching
2. **Triplet Score**: Knowledge graph-based relevance using concepts and relations

```
hybrid_score = (bm25_weight × normalized_bm25) + (triplet_weight × normalized_triplet)
```

Default weights:
- `bm25_weight = 0.6` (60% weight on text matching)
- `triplet_weight = 0.4` (40% weight on knowledge graph)

### Triplet Scoring

Sections are scored based on matched triplets:
- Full triplet match (subject + relation + object): 10 points
- Concept + relation match: 5 points
- Both concepts match: 4 points
- Single concept match: 2 points
- Relation only: 1 point

## Files

```
retrieval/
├── src/
│   ├── __init__.py
│   ├── bm25_ranker.py           # BM25 implementation
│   └── retrieval_system.py      # Main retrieval pipeline
├── test_bm25_retrieval.py       # Python test script
├── test_bm25_ranking.ipynb      # Jupyter notebook for testing
└── README.md                     # This file
```

## Requirements

- Python 3.8+
- MongoDB with populated collections:
  - `legal_sections` - Legal document sections
  - `concepts` - Extracted concepts from documents
  - `relations` - Extracted relations
  - `triplets` - Knowledge graph triplets
- VnCoreNLP 1.2
- PhoNLP
- pymongo
- pandas

## Future Enhancements

1. **Semantic Search**: Add word embeddings (PhoBERT) for semantic similarity
2. **Query Expansion**: Expand queries using synonyms and related terms
3. **Re-ranking**: Add neural re-ranking model (cross-encoder)
4. **Caching**: Cache BM25 scores for frequent queries
5. **Feedback Loop**: Learn from user feedback to adjust weights
6. **Multi-field BM25**: Score different fields (title, content, path) separately

## References

- BM25: Robertson, S., & Zaragoza, H. (2009). "The Probabilistic Relevance Framework: BM25 and Beyond"
- VnCoreNLP: Vu et al. (2018). "VnCoreNLP: A Vietnamese Natural Language Processing Toolkit"
- PhoNLP: Nguyen & Nguyen (2020). "PhoNLP: A joint multi-task learning model for Vietnamese part-of-speech tagging, named entity recognition and dependency parsing"
