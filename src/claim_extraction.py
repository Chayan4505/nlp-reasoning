
import re
import json

def extract_claims(backstory_text: str, story_id: str) -> list[dict]:
    """
    Extracts claims using local sentence splitting.
    Fast, Free, No Rate Limits.
    """
    # Simple semantic splitting by punctuation (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', backstory_text)
    
    claims = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if len(sent) > 10: # Ignore short noise
            # Generate simple adversarial queries locally
            adversarial_queries = [
                f"it is false that {sent}",
                f"contradiction: {sent}" 
            ]
            
            claims.append({
                "id": f"{story_id}_C{i}",
                "story_id": story_id,
                "text": sent,
                "adversarial_queries": adversarial_queries
            })
            
    return claims
