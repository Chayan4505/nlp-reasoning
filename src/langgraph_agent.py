
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

# Import existing modules
from .retrieval import retrieve_evidence
from .reasoning_llm import reason_about_claim
from .config import RETRIEVAL_K

class AgentState(TypedDict):
    claim: dict
    story_id: str
    evidence: list
    decision: dict
    confidence: float

def retrieve_node(state: AgentState):
    """
    Retrieves evidence (Semantic + Adversarial + Hybrid Reranked).
    """
    evidence = retrieve_evidence(state["claim"], state["story_id"], k=RETRIEVAL_K)
    return {"evidence": evidence}

def reason_node(state: AgentState):
    """
    Reasons about consistency using Gemini.
    """
    decision = reason_about_claim(state["claim"], state["evidence"])
    # Clean up decision to match dict if needed
    return {
        "decision": decision, 
        "confidence": decision.get("confidence", 0.0)
    }

def should_rerank(state: AgentState):
    """
    Conditional Logic: If confidence is low, could trigger deeper search (not implemented here loop-wise to avoid costs),
    or just END.
    """
    if state["confidence"] < 0.5:
        # In a full agent, we might change query and loop back to 'retrieve'
        # return "retrieve" 
        return "aggregate"
    return "aggregate"

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reason", reason_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reason")
workflow.add_conditional_edges(
    "reason",
    should_rerank,
    {
        "retrieve": "retrieve",
        "aggregate": END
    }
)

app = workflow.compile()

def run_agentic_check(claim: dict, story_id: str):
    """
    Entry point to run the LangGraph agent for a single claim.
    """
    initial_state = {
        "claim": claim, 
        "story_id": story_id, 
        "evidence": [], 
        "decision": {}, 
        "confidence": 0.0
    }
    result = app.invoke(initial_state)
    return result["decision"]
