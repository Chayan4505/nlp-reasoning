
import requests
from .config import RETRIEVAL_K

def retrieve_evidence(claim: dict, story_id: str, k: int = RETRIEVAL_K):
    """
    Queries the running Pathway Vector Store for relevant chunks.
    Uses 'adversarial_queries' if present to find contradictions.
    """
    url = "http://127.0.0.1:8765/v1/retrieve"
    
    from .config import USE_DUMMY_LLM
    if USE_DUMMY_LLM:
        print(f"[Mock] Retrieving evidence for claim: {claim.get('text', '')[:30]}...")
        return [
            {"text": f"Mock evidence text for query: {claim.get('text')}", "score": 0.85, "metadata": {"story_id": story_id}}
        ]

    # Combine claim text with adversarial queries for broader recall
    queries = [claim["text"]] + claim.get("adversarial_queries", [])
    
    unique_results = {}
    
    for q in queries:
        full_query = f"BOOK_CONTEXT. {q}" # Simple prefix
        payload = {
            "query": full_query,
            "k": k,
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                results = response.json()
                for res in results:
                    # Deduplicate by text content (simple heuristic)
                    if res["text"] not in unique_results:
                        unique_results[res["text"]] = res
            else:
                print(f"Retrieval failed for query '{q}': {response.status_code}")
        except Exception as e:
            print(f"Error connecting to Vector Store: {e}")
            
    
    # 3. Hybrid Reranking (Novelty)
    # If we have results, we refine them.
    # Note: efficient BM25 requires the whole corpus. 
    # Here we simulate reranking top-k or use a second-stage pass if we had the full text accessible easily.
    # For this implementation, we will act on the retrieved 'semantic_chunks' (sorted_results)
    
    try:
        from rank_bm25 import BM25Okapi
        import numpy as np
        
        if not unique_results:
            return []
            
        # Convert to list and sort by score (descending)
        sorted_results = sorted(unique_results.values(), key=lambda x: x.get("score", 0), reverse=True)

        semantic_chunks = sorted_results[:k*2] # Get more candidates for reranking
        if not semantic_chunks:
            return []
            
        # BM25 Scoring on Candidate Chunks
        tokenized_chunks = [c.get("text", "").split() for c in semantic_chunks]
        bm25 = BM25Okapi(tokenized_chunks)
        query = claim.get("text", "")
        if claim.get("adversarial_queries"):
             query += " " + " ".join(claim.get("adversarial_queries"))
        
        bm25_scores = bm25.get_scores(query.split())
        
        # Temporal Scoring (Mocking position if missing, else use metadata)
        # Assuming metadata might contain 'chunk_id' or strict 'position'. 
        # We'll default to 0.5 if missing.
        temporal_scores = []
        for c in semantic_chunks:
            meta = c.get("metadata", {})
            # Normalized position from 0 to 1
            pos = meta.get("position", 0) 
            temporal_scores.append(min(pos / 100000.0, 1.0)) # Normalize assumption
        
        temporal_scores = np.array(temporal_scores)
        
        # Hybrid Score Calculation
        # Weights: Semantic (0.6) + BM25 (0.25) + Temporal (0.15)
        semantic_scores = np.array([c.get("score", 0) for c in semantic_chunks])
        
        # Normalize bm25
        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()
            
        hybrid_scores = (0.6 * semantic_scores) + (0.25 * bm25_scores) + (0.15 * temporal_scores)
        
        # Sort by hybrid score
        ranked_indices = np.argsort(hybrid_scores)[::-1][:k]
        final_results = [semantic_chunks[i] for i in ranked_indices]
        return final_results

    except ImportError:
        # Fallback if dependencies missing
        return sorted_results[:k]
    except Exception as e:
        print(f"Reranking error: {e}")
        return sorted_results[:k]
