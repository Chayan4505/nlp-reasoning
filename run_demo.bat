echo ==================================================
echo      KDSH 2026 Track A - Automated Pipeline
echo ==================================================
echo.
echo [1/2] Running RAG Inference (Generating Results)...
.\.venv\Scripts\python.exe -m src.run_inference --test
echo.
echo [2/2] Launching Evidence Dashboard...
echo       (Press Ctrl+C to stop)
.\.venv\Scripts\python.exe -m streamlit run app.py
