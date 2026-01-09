# 🏆 Kharagpur Data Science Hackathon 2026 - Track A Submission

## Team: [Your Team Name]

## Track: A (Systems Reasoning with NLP and Generative AI)

### 1. Overall Approach

Our system, **Narrative-Guard**, addresses the challenge of global consistency in long narratives through a **Hybrid Neuro-Symbolic Architecture**. We recognized that Large Language Models (LLMs) often hallucinate or fail to track long-term constraints. Therefore, we engineered a pipeline that decouples **Evidence Retrieval** from **Reasoning**.

**Core Pipeline:**

1. **Ingestion & Indexing (Pathway)**: We use the `pathway` framework to ingest full novel texts (100k+ words). We chunk the text into 1000-token segments to preserve context, indexed using a **Hybrid Search** mechanism (BM25 + Semantic Vector Search).
2. **Claim Extraction**: We parse the hypothetical backstory into atomic, verifiable claims using `gemini-2.0-flash`.
3. **Adversarial Evidence Retrieval**: For each claim (e.g., "He was a pacifist"), we generate adversarial queries (e.g., "He fought", "He punched") to actively hunt for contradictions in the novel.
4. **Hybrid Reasoning (Novelty)**:
   * **Level 1 (Symbolic/NLI)**: A local DeBERTa-based Natural Language Inference (NLI) model checks each Claim-Evidence pair. If a clear contradiction is found (Confidence > 0.8), we reject the backstory *without* invoking the LLM. This ensures robustness and speed.
   * **Level 2 (Generative)**: Ambiguous claims are sent to `gemini-2.0-flash` with a strict prompt to evaluate causal logic, not just semantic similarity.

### 2. Handling Long Context

Instead of feeding the entire novel to the LLM (which dilutes attention), we use **Precision Retrieval**.

* **chunking**: 1000-token windows with 200-token overlap ensure no narrative event is split mid-sentence.
* **Global Search**: Our BM25 index allows us to find keywords like specific character names or locations anywhere in the book, maintaining *global* consistency checks even if the events are hundreds of pages apart.

### 3. Distinguishing Causal Signals from Noise

We explicitly prompt our system to ignore "narrative similarity."

* **Fact vs. Vibe**: If the backstory says "He loves the ocean" and the book says "He stood by the sea," standard RAG might call this 'Consistent'. Our NLI engine requires *entailment*.
* **Contradiction Priority**: Our logic prioritizes *one* contradiction over *ten* supporting facts. If the character dies in Chapter 5 but the backstory claims they visited Paris in Chapter 10, the system flags this as **Inconsistent (0)** immediately.

### 4. Key Limitations

* **Inferred Knowledge**: Constraints that are purely implicit (e.g., social etiquette of the 1800s) might be missed if not explicitly stated in the text.
* **Irony/Sarcasm**: The NLI model may struggle with dialogue where a character says something they don't mean.

### 5. Tech Stack

* **Framework**: Pathway (Python)
* **LLM**: Gemini 2.0 Flash (via Google GenAI)
* **Local NLI**: `cross-encoder/nli-deberta-v3-small`
* __Search__: `rank_bm25` + Vector Embeddings

---

## Run Instructions

1. **Install**: `pip install -r requirements.txt`
2. __Run Pipeline__: `python src/run_all.py`
3. __View Dashboard__: `python -m streamlit run streamlit_app.py`
