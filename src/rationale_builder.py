
import json
import os
from .config import DOSSIERS_DIR
from .data_types import ClaimDecision


def build_submission_rationale(dossier_entries, prediction):
    """Generate Track A compliant rationale (Section 5 Structure)"""
    
    if not dossier_entries:
        return "No sufficient evidence found to contradict/support."

    # Select the most significant entry (High Confidence Contradiction or Strong Support)
    # Priority: Contradiction > Support
    
    selected_entry = None
    # Flexible matching for relation (str or int)
    contradictions = [e for e in dossier_entries if str(e.get("relation")).upper() == "CONTRADICT"]
    supports = [e for e in dossier_entries if str(e.get("relation")).upper() == "SUPPORT"]
    
    if prediction == 0 and contradictions:
        selected_entry = contradictions[0]
    elif prediction == 1 and supports:
        selected_entry = supports[0]
    elif dossier_entries:
        selected_entry = dossier_entries[0]
        
    if selected_entry:
        claim_text = selected_entry.get("claim_text", "")
        excerpt = selected_entry.get("excerpt_text", "")[:150].replace("\n", " ") # Clean formatting
        analysis = selected_entry.get("analysis", "")
        
        # Strict Format as per Section 5
        return f"[Claim]: {claim_text} | [Evidence]: \"{excerpt}...\" | [Analysis]: {analysis}"
        
    return "Rationale classification ambiguous based on available evidence."


def build_dossier(story_id: str, decisions: list[ClaimDecision], prediction: int = None):
    """
    Saves the detailed claim decisions as a JSON dossier and returns the final rationale.
    """
    dossier_path = DOSSIERS_DIR / f"story_{story_id}_dossier.json"
    
    # Ensure directory exists
    os.makedirs(DOSSIERS_DIR, exist_ok=True)
    
    dossier_entries = []
    for decision in decisions:
        if "evidence_entries" in decision:
            dossier_entries.extend(decision["evidence_entries"])
            
    dossier_data = {
        "story_id": story_id,
        "prediction": prediction,
        "dossier": dossier_entries # Full evidence dossier
    }
    
    with open(dossier_path, "w", encoding="utf-8") as f:
        json.dump(dossier_data, f, indent=2)

    # Return the compliant Rationale string
    return build_submission_rationale(dossier_entries, prediction)
