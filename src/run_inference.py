
import multiprocessing
import time
import pandas as pd
import os
from pathlib import Path
from .pathway_pipeline import ProductionNovelIndexer
from .claim_extraction import extract_claims
from .retrieval import retrieve_evidence
from .reasoning_llm import reason_about_claim
from .aggregation import aggregate_decisions
from .rationale_builder import build_dossier
from .config import RESULTS_CSV, BOOK_MAPPING, RAW_DATA_DIR

def start_pathway_server():
    """Starts the Pathway Vector Store Server in a separate process."""
    print("[Server] Starting Pathway Pipeline...")
    pipeline = ProductionNovelIndexer()
    # This call blocks
    pipeline.run_server()

def run_pipeline(use_train=False):
    """Runs the inference logic."""
    from .config import TRAIN_CSV, TEST_CSV
    
    csv_path = TRAIN_CSV if use_train else TEST_CSV
    print(f"[Client] Reading dataset from {csv_path}...")
    
    if not csv_path.exists():
        print(f"[Client] CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    results = []

    print(f"[Client] Processing {len(df)} stories...")

    for index, row in df.iterrows():
        story_id = row.get("id", str(index))
        book_name = row.get("book_name")
        backstory_text = row.get("content")
        
        print(f"\nProcessing Story {story_id} ({book_name})...")
        
        # 1. Extract Claims
        claims = extract_claims(backstory_text, story_id)
        print(f"  Extracted {len(claims)} claims.")
        
        decisions = []
        for claim in claims:
            # 2. Retrieve Evidence (Adversarial)
            # We pass the full claim object now, which contains 'adversarial_queries'
            evidence_data = retrieve_evidence(claim, story_id)
            
            # Map retrieval result to Evidence type
            evidence_list = []
            for item in evidence_data:
                # Pathway returns 'text' and 'metadata' usually
                evidence_list.append({
                    "text": item.get("text", ""),
                    "score": item.get("score", 0.0),
                    "metadata": item.get("metadata", {})
                })
            
            # 3. Reason
            decision = reason_about_claim(claim, evidence_list)
            decisions.append(decision)
            
        # 4. Aggregate
        result = aggregate_decisions(decisions, story_id)
        print(f"  Prediction: {result['prediction']}, Rationale: {result['rationale']}")
        
        # 5. Save Dossier & Generate Rationale
        final_rationale = build_dossier(story_id, decisions, result["prediction"])
        
        results.append({
            "story_id": story_id,
            "prediction": result["prediction"],
            "rationale": final_rationale
        })

    # Save Results
    # Fix headers to match requirements: Story ID, Prediction, Rationale
    res_df = pd.DataFrame(results)
    res_df.rename(columns={
        "story_id": "Story ID",
        "prediction": "Prediction",
        "rationale": "Rationale"
    }, inplace=True)
    
    res_df.to_csv(RESULTS_CSV, index=False)
    print(f"\n[Client] Results saved to {RESULTS_CSV}")

if __name__ == "__main__":
    # 1. Start Pathway Server
    server_process = multiprocessing.Process(target=start_pathway_server)
    server_process.start()
    
    # Wait for server to initialize (heuristic)
    time.sleep(15) 
    
    try:
        # 2. Run Inference
        import sys
        use_train = "--train" in sys.argv
        run_pipeline(use_train=use_train)
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        # 3. Cleanup
        print("Stopping server...")
        server_process.terminate()
        server_process.join()
