
import json
import json
from .data_types import Claim, Evidence, ClaimDecision



from .nli_engine import check_local_consistency


from .nli_engine import check_local_consistency

def reason_about_all_claims(claims: list[dict], evidence_map: dict) -> list[ClaimDecision]:
    """
    Fully Local Neuro-Symbolic Reasoning:
    1. Check Local NLI (DeBERTa) for contradictions/entailments.
    2. If NLI is uncertain, fall back to 'Consistent' (Presumption of Innocence).
    
    Status: FAST. No API calls. No Rate Limits.
    """
    final_decisions = []
    
    for c in claims:
        ev_list = evidence_map.get(c["id"], [])
        
        # Default decision: Consistent (1) with Low Confidence
        label = "SUPPORT"
        confidence = 0.5
        analysis = "Default consistency assumption (no strong contradiction found)."
        source = "Heuristic-Default"
        
        if ev_list:
            # Run Local NLI
            nli_result = check_local_consistency(c["text"], ev_list)
            
            if nli_result:
                label = nli_result['label']
                confidence = nli_result['confidence']
                source = "Local-DeBERTa"
                analysis = f"Local NLI Model detected {label} with {confidence:.2f} confidence."
            
            # Simple keyword heuristic as backup/booster
            # If evidence mentions "not" + claim verb? (Too complex for simple regex)
            # Stick to NLI.
        
        else:
             analysis = "No evidence found. Assuming consistency."

        # Construct Evidence Entries
        ev_entries = []
        for e in ev_list:
             ev_entries.append({
                "story_id": c["story_id"],
                "claim_id": c["id"],
                "claim_text": c["text"],
                "excerpt_text": e["text"],
                "relation": label if source == "Local-DeBERTa" else "NONE",
                "analysis": "Evidence used for NLI check."
            })
            
        print(f"  [Local] Claim {c['id']} -> {label} ({confidence:.2f}) via {source}")

        final_decisions.append({
            "claim_id": c["id"],
            "story_id": c["story_id"],
            "label": label,
            "confidence": confidence,
            "analysis": analysis,
            "evidence_entries": ev_entries
        })

    return final_decisions

# Legacy single function (kept just in case, or removed if unused)
def reason_about_claim(claim, evidence):
    # Redirect to batch for simplicity? Or just keep as compat wrapper
    return reason_about_all_claims([claim], {claim["id"]: evidence})[0]
