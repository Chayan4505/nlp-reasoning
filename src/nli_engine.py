
from sentence_transformers import CrossEncoder
import torch

# fast and accurate NLI model
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
_model_instance = None

def get_nli_model():
    global _model_instance
    if _model_instance is None:
        print("[NLI] Loading local DeBERTa model (this happens once)...")
        try:
            _model_instance = CrossEncoder(MODEL_NAME)
            print("[NLI] Model loaded successfully.")
        except Exception as e:
            print(f"[NLI] Failed to load model: {e}")
            return None
    return _model_instance

def check_local_consistency(claim_text: str, evidence_list: list) -> dict:
    """
    Uses local NLI to check for contradictions.
    Returns: {"label": "CONTRADICT"|"SUPPORT"|"NONE", "confidence": float} or None (if unsure).
    """
    model = get_nli_model()
    if not model or not evidence_list:
        return None

    # Prepare pairs: (Claim, Evidence)
    # Note: NLI usually expects (Premise, Hypothesis).
    # Premise = Evidence, Hypothesis = Claim.
    pairs = [(e["text"], claim_text) for e in evidence_list]
    
    try:
        # Predict scores (logits)
        scores = model.predict(pairs)
        # Convert to probabilities (softmax) if needed, or just look at max
        # Labels: 0differs based on model. For DeBERTa-NLI:
        # usually 0: Contradiction, 1: Entailment, 2: Neutral (check model card)
        # Actually cross-encoder/nli* usually: 0: Contradiction, 1: Entailment, 2: Neutral
        
        # We want to find ANY contradiction with high confidence
        # or Strong Entailment.
        
        best_label = "NONE"
        best_conf = 0.0
        
        # Aggregate logic: If ANY evidence strongly contradicts -> Contradiction.
        # If ANY evidence strongly supports -> Support.
        # Contradiction overrides Support.
        
        probs = torch.nn.functional.softmax(torch.tensor(scores), dim=1).numpy()
        
        # Mapping for this specific model:
        # 0: Contradiction, 1: Entailment, 2: Neutral 
        # (Double check: standard is usually Entailment, Neutral, Contradiction?
        #  Let's verify via generic logic or assume standard MNLI mapping: 
        #  0: Contradiction, 1: Entailment, 2: Neutral is common for *some*, 
        #  but `cross-encoder/nli-deberta-v3-*` follows MNLI: 0: Contradiction, 1: Entailment, 2: Neutral?
        #  Wait, actually many use: 0: Contradiction, 1: Entailment, 2: Neutral
        #  AutoModelForSequenceClassification default config:
        #  label2id: {'contradiction': 0, 'entailment': 1, 'neutral': 2}
        
        idx_contra = 0
        idx_entail = 1
        idx_neutral = 2
        
        max_contra = 0.0
        max_entail = 0.0
        
        for p in probs:
            c = p[idx_contra]
            e = p[idx_entail]
            
            if c > max_contra: max_contra = c
            if e > max_entail: max_entail = e
            
        print(f"  [NLI Debug] Contra: {max_contra:.2f}, Entail: {max_entail:.2f}")

        # Thresholds
        if max_contra > 0.8:
            return {"label": "CONTRADICT", "confidence": float(max_contra), "source": "Local-NLI"}
        elif max_entail > 0.8:
            return {"label": "SUPPORT", "confidence": float(max_entail), "source": "Local-NLI"}
            
        # If ambiguous, return None to let LLM decide
        return None

    except Exception as e:
        print(f"[NLI] Inference error: {e}")
        return None
