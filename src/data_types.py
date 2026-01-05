
from typing import TypedDict, Literal, List, Optional

class Claim(TypedDict):
    id: str
    story_id: str
    text: str
    type: str # event, belief, etc
    importance: str # core, detail

class Evidence(TypedDict):
    text: str
    score: float
    metadata: dict

class DossierEntry(TypedDict):
    story_id: str
    claim_id: str
    claim_text: str
    excerpt_text: str # Verbatim text
    relation: Literal["SUPPORT", "CONTRADICT", "NONE"]
    analysis: str # Explanation of constraint/refutation

class ClaimDecision(TypedDict):
    # Internal intermediate state
    claim_id: str
    story_id: str
    label: Literal["SUPPORT", "CONTRADICT", "NONE"]
    confidence: float
    analysis: str
    evidence_entries: List[DossierEntry] # Explicit dossier entries

class StoryResult(TypedDict):
    story_id: str
    prediction: int # 0 or 1
    rationale: str
    score_support: float
    score_contradict: float
