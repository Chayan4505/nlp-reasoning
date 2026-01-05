
import json
import os
from .config import DOSSIERS_DIR
from .data_types import ClaimDecision

def build_submission_rationale(dossier_entries, prediction):
    """Generate Track A compliant rationale"""
    
    if prediction == 1:
        # Consistent: highlight supporting evidence
        # We assume dossier_entries are dicts (DossierEntry)
        support_entries = [e for e in dossier_entries if e.get("relation") == "SUPPORT"]
        if support_entries:
            key_support = support_entries[0]
            # Truncate analysis to be concise
            analysis = key_support.get("analysis", "")
            return f"Backstory consistent. {analysis[:100]}..."
        return "Backstory consistent with narrative constraints."
    
    else:
        # Contradict: highlight key contradiction (REQUIRED format)
        contradict_entries = [e for e in dossier_entries if e.get("relation") == "CONTRADICT"]
        if contradict_entries:
            # Heuristic: pick one with longest analysis or just first
            key_contradict = contradict_entries[0] 
            analysis = key_contradict.get("analysis", "")
            return f"Backstory contradicts narrative. {analysis[:120]}"
        return "Backstory contradicts established narrative constraints."

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
