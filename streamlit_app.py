
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
    st.header("📊 Batch Analysis Dashboard")
    
    if RESULTS_CSV.exists():
        res_df = pd.read_csv(RESULTS_CSV)
        
        # --- Metrics Section ---
        col1, col2, col3 = st.columns(3)
        total = len(res_df)
        if total > 0:
            consistent = len(res_df[res_df["Prediction"] == 1])
            contradictions = len(res_df[res_df["Prediction"] == 0])
            
            col1.metric("Total Stories", total)
            col2.metric("✅ Consistent", f"{consistent} ({consistent/total*100:.1f}%)")
            col3.metric("❌ Inconsistent", f"{contradictions} ({contradictions/total*100:.1f}%)")
        else:
            st.info("Empty Results File.")
        
        st.divider()
        
        # --- Filter & Table ---
        filter_status = st.radio("Filter Verdict:", ["All", "Consistent Only", "Inconsistent Only"], horizontal=True)
        
        filtered_df = res_df.copy()
        if filter_status == "Consistent Only":
            filtered_df = res_df[res_df["Prediction"] == 1]
        elif filter_status == "Inconsistent Only":
            filtered_df = res_df[res_df["Prediction"] == 0]
            
        st.dataframe(
            filtered_df,
            column_config={
                "Prediction": st.column_config.CheckboxColumn("Consistent?", disabled=True),
                "Rationale": "Summary Rationale"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # --- Deep Dive Inspection ---
        st.subheader("🔍 Deep Dive Inspection")
        if not filtered_df.empty:
            selected_id = st.selectbox("Select Story ID to audit:", filtered_df["Story ID"].unique())
            
            if selected_id:
                row = filtered_df[filtered_df["Story ID"] == selected_id].iloc[0]
                
                # Parse the Rationale String to recreate the Card
                rationale_raw = str(row["Rationale"])
                
                # Simple parser for our strict format: [Claim]: X | [Evidence]: Y | [Analysis]: Z
                claim_part = rationale_raw
                evidence_part = "See above"
                analysis_part = "See above"
                
                if "[Claim]:" in rationale_raw:
                    parts = rationale_raw.split("|")
                    for p in parts:
                        p = p.strip()
                        if p.startswith("[Claim]:"): claim_part = p.replace("[Claim]:", "").strip()
                        if p.startswith("[Evidence]:"): evidence_part = p.replace("[Evidence]:", "").strip().replace('"', '')
                        if p.startswith("[Analysis]:"): analysis_part = p.replace("[Analysis]:", "").strip()
                
                # Display Card
                st.markdown("### 🧩 Evidence Dossier Card")
                st.caption(f"Audit Log for Story ID: {selected_id}")
                
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    with c1:
                         if row['Prediction'] == 1:
                            st.markdown("## ✅\n**VALID**")
                         else:
                            st.markdown("## ❌\n**FALSE**")
                    
                    with c2:
                        st.markdown(f"**Questioned Claim**: {claim_part}")
                        st.info(f"**Logic Analysis**: {analysis_part}")
                    
                    with st.expander("📜 Primary Source Evidence (Verbatim)", expanded=True):
                        # Highlight evidence text based on verdict
                        if row['Prediction'] == 0:
                            st.markdown(f"> :red[**\"{evidence_part}\"**]")
                        else:
                            st.markdown(f"> :green[**\"{evidence_part}\"**]")
        else:
            st.info("No stories match the current filter.")

    else:
        st.warning("⚠️ No results.csv found. Please run the `src/run_all.py` pipeline first!")

elif mode == "Interactive Analysis":
    st.header("🕵️‍♀️ Interactive Investigation")
    
    if df.empty:
        st.error("No data/train.csv found!")
    else:
        # Story Selector
        story_options = df.apply(lambda x: f"{x['id']} - {x['book_name']}", axis=1)
        selected_option = st.selectbox("Select Story Case", story_options)
        
        if selected_option:
            story_id = str(selected_option.split(" - ")[0])
            row = df[df["id"] == int(story_id) if story_id.isdigit() else story_id].iloc[0]
            
            with st.expander("📖 Read Backstory Profile", expanded=False):
                st.markdown(f"*{row['content']}*")
            
            if st.button("🚀 Analyze Consistency", type="primary"):
                
                # --- Pipeline Execution ---
                with st.status("Running Hybrid Neuro-Symbolic Pipeline...", expanded=True) as status:
                    
                    try:
                        # 1. Extraction
                        status.write("🔍 Step 1: Decomposing Backstory into Claims (Regex)...")
                        claims = extract_claims(row["content"], story_id)
                        time.sleep(0.5) # UX feel
                        
                        if not claims:
                            status.update(label="Failed: No claims found.", state="error")
                            st.warning("No verifiable claims found in extraction.")
                        else:
                            # 2. Retrieval
                            status.write(f"📚 Step 2: Adversarial Retrieval (BM25 + Vector) for {len(claims)} claims...")
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
                            
                            # 3. Reasoning
                            status.write("🧠 Step 3: Neuro-Symbolic Verification (DeBERTa NLI)...")
                            decisions = reason_about_all_claims(claims, evidence_map)
                            
                            # 4. Aggregate
                            status.write("📝 Step 4: Compiling Evidence Dossier...")
                            result = aggregate_decisions(decisions, story_id)
                            final_rationale = build_dossier(story_id, decisions, result["prediction"])
                            
                            status.update(label="Analysis Complete!", state="complete", expanded=False)
                            
                            # --- Results Display ---
                            st.divider()
                            
                            # Tabs for Organized View
                            tab_verdict, tab_dossier, tab_raw = st.tabs(["🛡️ Final Verdict", "📂 Evidence Dossier (Track A)", "⚙️ Raw Data"])
                            
                            with tab_verdict:
                                st.subheader("Consistency Judgment")
                                if result['prediction'] == 1:
                                    st.success("### ✅ Consistent")
                                    st.markdown("The backstory aligns with the established narrative constraints.")
                                else:
                                    st.error("### ❌ Contradiction Detected")
                                    st.markdown("The backstory conflicts with specific events in the narrative.")
                                
                                st.markdown("### Submission Rationale")
                                st.info(final_rationale)
                                
                                # Download Button
                                dossier_json = json.dumps(decisions, indent=2)
                                st.download_button("📥 Download Dossier (JSON)", dossier_json, f"dossier_{story_id}.json")

                            with tab_dossier:
                                st.markdown("### 🧩 Claim Verification Audit")
                                st.caption("Strict compliance with Section 5: Excerpt -> Linkage -> Analysis")
                                
                                for decision in decisions:
                                    lbl = decision["label"]
                                    confidence = decision["confidence"]
                                    claim_txt = decision.get("claim_text", "Claim")
                                    
                                    # Card Styling
                                    with st.container(border=True):
                                        col1, col2 = st.columns([1, 4])
                                        with col1:
                                            if lbl == "SUPPORT":
                                                st.metric("Verdict", "✅ VALID", f"{confidence*100:.0f}% Conf")
                                            elif lbl == "CONTRADICT":
                                                st.metric("Verdict", "❌ FALSE", f"{confidence*100:.0f}% Conf", delta_color="inverse")
                                            else:
                                                st.metric("Verdict", "❓ UNSURE", "Low Data", delta_color="off")
                                        
                                        with col2:
                                            st.markdown(f"**Claim**: {claim_txt}")
                                            st.markdown(f"**Analysis**: *{decision['analysis']}*")
                                            
                                        # Evidence Dropdown
                                        with st.expander("📜 Primary Text Excerpts (Verbatim)"):
                                            if not decision["evidence_entries"]:
                                                st.caption("No direct retrieval matches found.")
                                            for ev in decision["evidence_entries"]:
                                                bg_color = "#e6ffe6" if lbl == "SUPPORT" else "#ffe6e6" if lbl == "CONTRADICT" else "#f0f2f6"
                                                st.markdown(f"""
                                                <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; border-left: 3px solid #ccc;">
                                                    <small>FILE: {ev.get("story_id", "Unknown")}</small><br>
                                                    <em>"...{ev['excerpt_text']}..."</em>
                                                </div>
                                                <br>
                                                """, unsafe_allow_html=True)

                            with tab_raw:
                                st.json(decisions)

                    except Exception as e:
                        st.error(f"Pipeline Error: {e}")
                        status.update(label="Pipeline Crashed", state="error")

