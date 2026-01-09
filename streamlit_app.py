
import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path

# Import pipeline components
from src.claim_extraction import extract_claims
from src.retrieval import retrieve_evidence
from src.reasoning_llm import reason_about_all_claims
from src.aggregation import aggregate_decisions
from src.rationale_builder import build_dossier
from src.run_all import TRAIN_CSV, RESULTS_CSV

st.set_page_config(page_title="Narrative Consistency Guard", layout="wide")

st.title("📚 Narrative Consistency Guard")
st.markdown("""
**System**: Hybrid Neuro-Symbolic (DeBERTa NLI + Regex Extraction + Pathway).  
**Goal**: Verify if a character's backstory is consistent with the novel (Track A).
""")

# --- Sidebar ---
st.sidebar.header("Navigation")
mode = st.sidebar.radio("Mode", ["Interactive Analysis", "View Results"])

@st.cache_data
def load_data():
    if TRAIN_CSV.exists():
        return pd.read_csv(TRAIN_CSV)
    # Fallback to local file if path object fails
    if os.path.exists("data/train.csv"):
         return pd.read_csv("data/train.csv")
    return pd.DataFrame()

df = load_data()

if mode == "View Results":
    st.header("📊 Batch Processing Results")
    if RESULTS_CSV.exists():
        res_df = pd.read_csv(RESULTS_CSV)
        st.metric("Processed Stories", len(res_df))
        st.dataframe(res_df)
        
        # Detail View
        selected_id = st.selectbox("Select Result to Inspect", res_df["Story ID"].unique())
        if selected_id:
            row = res_df[res_df["Story ID"] == selected_id].iloc[0]
            st.subheader(f"Verdict: {'✅ Consistent' if row['Prediction']==1 else '❌ Inconsistent'}")
            st.text_area("Rationale", row["Rationale"], height=300)
    else:
        st.info("No results.csv found. Run the batch pipeline or use Interactive Analysis.")

elif mode == "Interactive Analysis":
    st.header("🕵️‍♀️ Analyze a Story")
    
    if df.empty:
        st.error("No data/train.csv found!")
    else:
        # Story Selector
        story_options = df.apply(lambda x: f"{x['id']} - {x['book_name']}", axis=1)
        selected_option = st.selectbox("Select Story", story_options)
        
        if selected_option:
            story_id = str(selected_option.split(" - ")[0])
            row = df[df["id"] == int(story_id) if story_id.isdigit() else story_id].iloc[0]
            
            with st.expander("📖 View Backstory", expanded=True):
                st.write(row["content"])
            
            if st.button("Analyze Consistency"):
                progress = st.progress(0)
                status_text = st.empty()
                
                try:
                    # 1. Extraction
                    status_text.text("Step 1/4: Extracting Claims (Regex/Local)...")
                    with st.spinner("Extracting claims..."):
                        claims = extract_claims(row["content"], story_id)
                    progress.progress(25)
                    
                    st.write(f"**Found {len(claims)} Claims**")
                    with st.expander("View Claims"):
                        st.json([c["text"] for c in claims])
                    
                    if not claims:
                        st.warning("No claims found.")
                    else:
                        # 2. Retrieval
                        status_text.text("Step 2/4: Retrieving Evidence (BM25 + Vector)...")
                        evidence_map = {}
                        for claim in claims:
                            ev_data = retrieve_evidence(claim, story_id)
                            evidence_list = []
                            for item in ev_data:
                                evidence_list.append({
                                    "text": item.get("text", ""),
                                    "score": item.get("score", 0.0),
                                    "metadata": item.get("metadata", {})
                                })
                            evidence_map[claim["id"]] = evidence_list
                        progress.progress(50)
                        
                        # 3. Reasoning
                        status_text.text("Step 3/4: Reasoning (Local DeBERTa NLI)...")
                        with st.spinner("Reasoning about consistency..."):
                            decisions = reason_about_all_claims(claims, evidence_map)
                        progress.progress(75)
                        
                        # Display Decisions
                        # Display Decisions
                        st.subheader("Claim Verification")
                        for decision in decisions:
                            lbl = decision["label"]
                            confidence = decision["confidence"]
                            claim_txt = decision.get("claim_text", "Claim")
                            
                            # Visual Card matching Dossier Style
                            if lbl == "SUPPORT":
                                container = st.container(border=True)
                                container.markdown(f"✅ **Consistent**: {claim_txt}")
                            elif lbl == "CONTRADICT":
                                container = st.container(border=True)
                                container.markdown(f"❌ **Contradiction**: {claim_txt}")
                            else:
                                container = st.container(border=True)
                                container.markdown(f"❓ **Ambiguous**: {claim_txt}")
                                
                            with st.expander(f"🔍 View Evidence Dossier (Confidence: {confidence:.2f})"):
                                st.markdown(f"**Analysis**: {decision['analysis']}")
                                st.markdown("---")
                                st.caption("Primary Text Excerpts:")
                                for ev in decision["evidence_entries"]:
                                    st.markdown(f"> *\"{ev['excerpt_text']}...\"*")


                        # 4. Aggregate
                        status_text.text("Step 4/4: Aggregating Verdict...")
                        result = aggregate_decisions(decisions, story_id)
                        final_rationale = build_dossier(story_id, decisions, result["prediction"])
                        progress.progress(100)
                        
                        st.success("Analysis Complete!")
                        st.markdown(f"## Final Prediction: {'✅ Consistent' if result['prediction']==1 else '❌ Inconsistent'}")
                        st.text_area("Final Rationale (Dossier)", final_rationale, height=400)
                        
                except Exception as e:
                    st.error(f"Error: {e}")
