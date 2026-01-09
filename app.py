
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="KDSH 2026 Track A", page_icon="🧠", layout="wide")

st.title("🧠 KDSH 2026 Track A - Evidence Explorer")
st.markdown("### Systems Reasoning with NLP and Generative AI")

# Load results
results_path = "results/results.csv"
if os.path.exists(results_path):
    df = pd.read_csv(results_path)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Prediction Results")
        st.dataframe(df)

    with col2:
        st.subheader("Evidence Dossier Viewer")
        story_id = st.selectbox("Select Story ID to Inspect", df["Story ID"].unique())
        
        if story_id:
            dossier_path = f"data/processed/dossiers/story_{story_id}_dossier.json"
            if os.path.exists(dossier_path):
                with open(dossier_path, "r", encoding="utf-8") as f:
                    dossier_data = json.load(f)
                
                st.write(f"**Prediction:** {dossier_data.get('prediction', 'N/A')}")
                
                # Display individual entries nicely
                entries = dossier_data.get("dossier", [])
                if not entries:
                    st.info("No detailed evidence entries found.")
                
                # Color mapping for relation labels
                color_map = {
                    "SUPPORT": "green",
                    "CONTRADICT": "red",
                    "NONE": "gray"
                }

                for i, entry in enumerate(entries):
                    relation = entry.get('relation', 'NONE')
                    color = color_map.get(relation, "gray")
                    
                    with st.expander(f"Claim: {entry.get('claim_text', 'Unknown')[:60]}..."):
                        # Use columns for a header-like effect
                        c1, c2 = st.columns([1, 4])
                        with c1:
                            st.markdown(f":{color}[**{relation}**]")
                        with c2:
                            st.caption(f"Confidence: {entry.get('confidence', 'N/A')}")

                        st.markdown(f"**Analysis:** {entry.get('analysis')}")
                        st.markdown("**Evidence Excerpt:**")
                        st.info(entry.get('excerpt_text'))
                        
                # Raw JSON fallback
                with st.expander("View Raw JSON"):
                    st.json(dossier_data)
            else:
                st.warning(f"Dossier file not found: `{dossier_path}`")
else:
    st.error("No results file found. Please run `python -m src.run_inference` first.")
