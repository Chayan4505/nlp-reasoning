
import multiprocessing
import time
import pandas as pd
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.pathway_pipeline import ProductionNovelIndexer
from src.claim_extraction import extract_claims
from src.retrieval import retrieve_evidence
from src.reasoning_llm import reason_about_claim
from src.aggregation import aggregate_decisions
from src.rationale_builder import build_dossier
from src.config import RESULTS_CSV, TRAIN_CSV, TEST_CSV

def start_pathway_server():
    """Starts the Pathway Vector Store Server."""
    print("[Server] Starting Pathway Pipeline...")
    try:
        pipeline = ProductionNovelIndexer()
        pipeline.run_server()
    except Exception as e:
        print(f"[Server] Failed to start Pathway: {e}")
        # Identify if it is a mock/fallback scenario
        pass

def run_full_pipeline():
    """Runs inference on ALL data (Train + Test) with RESUME capability."""
    
    # Load Data
    print("[Client] Loading datasets...")
    dfs = []
    if TRAIN_CSV.exists():
        dfs.append(pd.read_csv(TRAIN_CSV))
    if TEST_CSV.exists():
        dfs.append(pd.read_csv(TEST_CSV))
        
    if not dfs:
        print("No data found!")
        return

    full_df = pd.concat(dfs, ignore_index=True)
    if 'id' in full_df.columns:
        full_df.drop_duplicates(subset=['id'], inplace=True)
        
    # Checkpoint Logic: Load existing results
    processed_ids = set()
    if RESULTS_CSV.exists():
        try:
            existing_df = pd.read_csv(RESULTS_CSV)
            # Check if valid columns
            if "Story ID" in existing_df.columns:
                processed_ids = set(existing_df["Story ID"].astype(str))
                print(f"[Client] Resuming: Found {len(processed_ids)} already processed stories.")
        except Exception as e:
            print(f"[Client] Warning reading existing results: {e}")

    # Prepare file for appending
    write_header = not RESULTS_CSV.exists() or os.stat(RESULTS_CSV).st_size == 0
    if not write_header:
        # If file exists but we are resuming, verify header is there? 
        # Assume yes if we read it successfully above.
        pass

    total_stories = len(full_df)
    print(f"[Client] Total stories: {total_stories}. Remaining: {total_stories - len(processed_ids)}")
    
    for index, row in full_df.iterrows():
        story_id = str(row.get("id", index))
        
        if story_id in processed_ids:
            continue
            
        book_name = row.get("book_name")
        backstory_text = row.get("content")
        
        print(f"\nProcessing Story {story_id} ({book_name})...")
        
        try:
            # 1. Extract Claims
            claims = extract_claims(backstory_text, story_id)
            print(f"  Extracted {len(claims)} claims.")
            
            # 2. Retrieve Evidence (IO Bound, Local BM25 is fast)
            evidence_map = {}
            for claim in claims:
                evidence_data = retrieve_evidence(claim, story_id)
                evidence_list = []
                for item in evidence_data:
                    evidence_list.append({
                        "text": item.get("text", ""),
                        "score": item.get("score", 0.0),
                        "metadata": item.get("metadata", {})
                    })
                evidence_map[claim["id"]] = evidence_list

            # 3. Reason (Batch Mode - FAST)
            from src.reasoning_llm import reason_about_all_claims
            decisions = reason_about_all_claims(claims, evidence_map)
            print(f"  Reasoned about {len(decisions)} claims in batch.")
                
            # 4. Aggregate
            result = aggregate_decisions(decisions, story_id)
            
            # 5. Build Rationale
            final_rationale = build_dossier(story_id, decisions, result["prediction"])
            
            # 6. Save IMMEDIATE (Incremental)
            result_row = {
                "Story ID": story_id,
                "Prediction": result["prediction"],
                "Rationale": final_rationale
            }
            
            pd.DataFrame([result_row]).to_csv(RESULTS_CSV, mode='a', header=write_header, index=False)
            write_header = False # Next rows won't need header
            
            print(f"  > Saved result for {story_id}.")
            
            # Proactive cooldown (Reduced to 5s since calls are vastly fewer)
            time.sleep(5)
            
        except Exception as e:
            print(f"  ERROR processing story {story_id}: {e}")
            # Optional: Save error state? 
            # For now, we just skip saving so it can be retried.

    print("\n[Client] Processing complete.")

if __name__ == "__main__":
    # 1. Start Pathway Server
    server_process = multiprocessing.Process(target=start_pathway_server)
    server_process.start()
    
    # Wait for server
    print("Waiting 10s for server...")
    time.sleep(10) 
    
    try:
        run_full_pipeline()
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        print("Stopping server...")
        server_process.terminate()
        server_process.join()
