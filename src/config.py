
# Configuration for KDSH 2026 Track A

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

NOVELS_DIR = RAW_DATA_DIR / "novels"
BACKSTORIES_DIR = RAW_DATA_DIR / "backstories"
TRAIN_CSV = DATA_DIR / "train.csv"
TEST_CSV = DATA_DIR / "test.csv"

CHUNKS_DIR = PROCESSED_DATA_DIR / "chunks"
CLAIMS_DIR = PROCESSED_DATA_DIR / "claims"
DOSSIERS_DIR = PROCESSED_DATA_DIR / "dossiers"

RESULTS_DIR = BASE_DIR / "results"
RESULTS_CSV = RESULTS_DIR / "results.csv"

# Pathway Configuration
PATHWAY_LICENSE_KEY = os.getenv("PATHWAY_LICENSE_KEY", "")

# LLM Configuration
# LLM Configuration
# We use Local DeBERTa, so API keys are technically optional/backup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = "cross-encoder/nli-deberta-v3-small"
USE_DUMMY_LLM = os.getenv("USE_DUMMY_LLM", "False").lower() in ("true", "1", "yes")

# Parameters
CHUNK_SIZE = 1000 # tokens roughly
CHUNK_OVERLAP = 200
RETRIEVAL_K = 10

BOOK_MAPPING = {
    "In Search of the Castaways": "In search of the castaways.txt",
    "The Count of Monte Cristo": "The Count of Monte Cristo.txt"
}

