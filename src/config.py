
# Configuration for KDSH 2026 Track A

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_secret(key, default=""):
    """Get secret from Streamlit secrets (cloud) or environment variable (local)"""
    if HAS_STREAMLIT:
        try:
            value = st.secrets.get(key, os.getenv(key, default))
            # Convert to string to handle boolean values from TOML
            return str(value) if value is not None else default
        except (FileNotFoundError, KeyError):
            return os.getenv(key, default)
    return os.getenv(key, default)

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
PATHWAY_LICENSE_KEY = get_secret("PATHWAY_LICENSE_KEY", "")

# LLM Configuration
# We use Local DeBERTa, so API keys are technically optional/backup
OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
LLM_MODEL = "cross-encoder/nli-deberta-v3-small"
USE_DUMMY_LLM = get_secret("USE_DUMMY_LLM", "False").lower() in ("true", "1", "yes")

# Parameters
CHUNK_SIZE = 1000 # tokens roughly
CHUNK_OVERLAP = 200
RETRIEVAL_K = 10

BOOK_MAPPING = {
    "In Search of the Castaways": "In search of the castaways.txt",
    "The Count of Monte Cristo": "The Count of Monte Cristo.txt"
}

