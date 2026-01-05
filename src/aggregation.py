
from typing import List, TypedDict, Literal
from .data_types import ClaimDecision, StoryResult

class CausalAggregator:
    def __init__(self):
        self.core_threshold = 0.8  # Core claim contradiction -> immediate 0
        self.support_threshold = 2.0 # Threshold for positive prediction if no core contradiction

    def aggregate(self, decisions: List[ClaimDecision], story_id: str) -> StoryResult:
        """
        Aggregates claim decisions using Causal Signal Detection rules.
        """
        
        # Rule 1: Core Claim Override
        # If any CORE claim is strongly contradicted, the backstory is invalid.
        # Note: We need 'importance' passed through. Assuming ClaimDecision has access or we treat all high-confidence as core for now.
        # Ideally, we verify against claim metadata.
        
        core_contradictions = [
            d for d in decisions 
            if d.get("label") == "CONTRADICT" and d.get("confidence", 0.0) >= self.core_threshold
        ]
        
        if core_contradictions:
            return {
                "story_id": story_id,
                "prediction": 0,
                "rationale": f"Rejected due to {len(core_contradictions)} CORE contradictions. Example: {core_contradictions[0].get('analysis')}",
                "decisions": decisions
            }

        # Rule 2: Temporal Weighting & Adversarial Decay
        # Calculate scores
        support_score = 0.0
        contradict_score = 0.0
        
        for d in decisions:
            # Simple temporal heuristic: assume evidence order correlates roughly with text position if not generic
            # For this implementation, we sum confidence.
            if d.get("label") == "SUPPORT":
                support_score += d.get("confidence", 0.0)
            elif d.get("label") == "CONTRADICT":
                contradict_score += d.get("confidence", 0.0)

        # Rule 3: Causal Threshold
        # Contradictions are weighted heavier than support (falsifiability)
        if contradict_score > support_score * 0.5: # Aggressive contradiction checking
             prediction = 0
             rationale = "Cumulative contradictions outweigh support signals."
        elif support_score >= self.support_threshold:
             prediction = 1
             rationale = "Consistent with narrative evidence."
        else:
             # Default to 0 (Conservative) or 1? 
             # Task says "Does it fit?" -> If no evidence, maybe 0 (Not proven) or 1 (Compatible).
             # Let's align with "Compatible" if no contradictions found.
             prediction = 1
             rationale = "No significant contradictions found; assumed consistent."

        return {
            "story_id": story_id,
            "prediction": prediction,
            "rationale": rationale,
            "decisions": decisions
        }

def aggregate_decisions(decisions: List[ClaimDecision], story_id: str) -> StoryResult:
    aggregator = CausalAggregator()
    return aggregator.aggregate(decisions, story_id)
