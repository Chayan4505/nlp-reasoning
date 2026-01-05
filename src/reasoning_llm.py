
import json
import google.generativeai as genai
from .config import GEMINI_API_KEY, LLM_MODEL
from .data_types import Claim, Evidence, ClaimDecision

# Configure Gemini (safe to call multiple times)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def reason_about_claim(claim: Claim, evidence_list: list[Evidence]) -> ClaimDecision:
    """
    Determines if the evidence supports or contradicts the claim using Gemini.
    """
    evidence_text = "\n\n".join([f"Excerpt {i+1}: {e['text']}" for i, e in enumerate(evidence_list)])
    
    from .config import USE_DUMMY_LLM
    if USE_DUMMY_LLM:
        import random
        return {
            "claim_id": claim["id"],
            "story_id": claim["story_id"],
            "label": random.choice(["SUPPORT", "CONTRADICT", "NONE"]),
            "confidence": 0.9,
            "analysis": "Dummy analysis from mock LLM.",
            "evidence_used": [e["text"][:50]+"..." for e in evidence_list]
        }

    prompt = f"""
    You are a judge of consistency in a story.
    
    CLAIM: "{claim['text']}"
    
    EVIDENCE FROM NOVEL:
    {evidence_text}
    
    Task: Determine if the evidence explicitly SUPPORTS, CONTRADICTS, or is UNRELATED (NONE) to the claim.
    Focus on causal logic and narrative facts.
    
    Output JSON:
    {{
        "label": "SUPPORT" | "CONTRADICT" | "NONE",
        "confidence": <float 0.0 to 1.0>,
        "analysis": "<short explanation>"
    }}
    IMPORTANT: Return ONLY the JSON. No markdown code blocks.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Clean potential markdown
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        result_json = json.loads(content)
        
        # Construct Dossier Entries
        dossier_entries = []
        for e in evidence_list:
            dossier_entries.append({
                "story_id": claim["story_id"],
                "claim_id": claim["id"],
                "claim_text": claim["text"],
                "excerpt_text": e["text"], # Verbatim excerpt
                "relation": result_json.get("label", "NONE"),
                "analysis": result_json.get("analysis", "") # Analysis of constraint/refutation
            })

        return {
            "claim_id": claim["id"],
            "story_id": claim["story_id"],
            "label": result_json.get("label", "NONE"),
            "confidence": result_json.get("confidence", 0.0),
            "analysis": result_json.get("analysis", ""),
            "evidence_entries": dossier_entries
        }
    except Exception as e:
        print(f"Error in reasoning with Gemini: {e}")
        return {
            "claim_id": claim["id"],
            "story_id": claim["story_id"],
            "label": "NONE",
            "confidence": 0.0,
            "analysis": f"Error: {str(e)}",
            "evidence_entries": []
        }
