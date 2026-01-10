
import os
import sys
import subprocess

def main():
    print("=================================================")
    print("   NARRATIVE-GUARD SUBMISSION RUNNER (TRACK A)   ")
    print("=================================================")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check if dependencies are installed (light check)
    try:
        import pathway
        import sentence_transformers
        import streamlit
    except ImportError as e:
        print(f"Error: Missing dependency {e}. Please run 'pip install -r requirements.txt'")
        sys.exit(1)

    # Add src to path just in case
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    
    # Check for Data
    if not os.path.exists("data/train.csv"):
        print("Warning: data/train.csv not found! The pipeline needs input data.")
    
    print("\nStarting End-to-End Pipeline (src/run_all.py)...")
    print("This will:")
    print("1. Ingest/Index Novels via Pathway")
    print("2. Extract Claims")
    print("3. Query & Reason (Neuro-Symbolic)")
    print("4. Generate 'results/results.csv'")
    print("-------------------------------------------------")
    
    # We call the python script as a subprocess to ensure clean environment
    try:
        subprocess.check_call([sys.executable, "src/run_all.py"])
        print("\n✅ SUCCESS: Pipeline Completed successfully.")
        print(f"Results saved to: {os.path.abspath('results/results.csv')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FAIL: Pipeline script crashed with code {e.returncode}.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
