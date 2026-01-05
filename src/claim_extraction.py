
import os
import json
import google.generativeai as genai
from .data_types import Claim
from .config import GEMINI_API_KEY, LLM_MODEL

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_claims(backstory_text: str, story_id: str) -> list[dict]:
    """
    Extracts atomic claims from the backstory text using Gemini.
    """
    from .config import USE_DUMMY_LLM
    if USE_DUMMY_LLM:
        print("[Mock] Extracting claims using dummy LLM...")
        return [
            {"id": f"{story_id}_c0", "story_id": story_id, "text": "Dummy claim 1", "type": "event", "importance": "core"},
            {"id": f"{story_id}_c1", "story_id": story_id, "text": "Dummy claim 2", "type": "belief", "importance": "detail"}
        ]

    prompt = f"""
    You are an expert analyst. Break down the following backstory into atomic, verifiable claims.
    For each claim, generate 2-3 "Adversarial Search Queries" to find potential CONTRADICTIONS in the novel.
    
    Example: 
    Claim: "He was a pacifist."
    Adversarial Queries: ["he punched", "he killed", "he used a weapon", "he fought"]
    
    Backstory:
    {backstory_text}
    
    Output a JSON list of objects with keys: 
    "text" (the claim), 
    "type" (event/belief/etc), 
    "importance" (core/detail), 
    "adversarial_queries" (list of strings).
    
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
            
        claims_data = json.loads(content)
        if isinstance(claims_data, dict) and "claims" in claims_data:
            claims_data = claims_data["claims"]
        
        # Add metadata
        for i, claim in enumerate(claims_data):
            claim["id"] = f"{story_id}_c{i}"
            claim["story_id"] = story_id
            
        return claims_data
    except Exception as e:
        print(f"Error extracting claims with Gemini: {e}")
        return []
