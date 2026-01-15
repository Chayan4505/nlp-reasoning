# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at https://streamlit.io/cloud)
- Your code pushed to GitHub

## Step-by-Step Deployment Instructions

### 1. Push Your Code to GitHub

First, make sure all your changes are committed and pushed:

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Sign Up for Streamlit Community Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign up" or "Continue with GitHub"
3. Authorize Streamlit to access your GitHub repositories

### 3. Deploy Your App

1. Click "New app" button
2. Fill in the deployment form:
   - **Repository**: `Chayan4505/nlp-reasoning`
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom URL (e.g., `narrative-guard`)

3. Click "Advanced settings" (optional but recommended):
   - **Python version**: 3.11 (or your preferred version)

### 4. Configure Secrets (IMPORTANT!)

Before deploying, you need to add your API keys:

1. In the deployment settings, find "Secrets" section
2. Copy the content from `.streamlit/secrets.toml.example`
3. Paste it into the Secrets text area
4. **Replace** `your-gemini-api-key-here` with your actual Gemini API key
5. Click "Save"

Example secrets format:
```toml
OPENAI_API_KEY = "not-needed-for-gemini"
GEMINI_API_KEY = "AIzaSyCFvHAaX9TFj2QPrZjWwuD0ZJwMNXyceTM"
PATHWAY_LICENSE_KEY = "pathway-license-key-optional"
USE_DUMMY_LLM = false
```

### 5. Deploy!

Click "Deploy!" button and wait for the build to complete (usually 5-10 minutes for first deployment).

## 📝 Important Notes

### File Size Limitations
- Streamlit Cloud has a **1GB repository size limit**
- Your `data/` folder with novels might be large
- Consider these options:
  1. **Use Git LFS** for large files
  2. **Load data from external storage** (Google Drive, S3, etc.)
  3. **Use a smaller dataset** for the demo

### Memory Limitations
- Free tier has **1GB RAM limit**
- Your ML models (DeBERTa, sentence-transformers) might be heavy
- Consider:
  1. Using smaller model variants
  2. Implementing model caching with `@st.cache_resource`
  3. Upgrading to paid tier if needed

### Environment Variables
- Never commit `.env` file with real API keys
- Always use Streamlit Secrets for sensitive data
- The app will read from `st.secrets` instead of `.env` in production

## 🔧 Troubleshooting

### Build Fails Due to Dependencies
If PyTorch installation fails:
1. Add `--find-links https://download.pytorch.org/whl/cpu/torch_stable.html` to requirements
2. Or use CPU-only version: `torch==2.0.0+cpu`

### App Crashes Due to Memory
1. Reduce model size
2. Implement lazy loading
3. Use `@st.cache_resource` for models
4. Consider upgrading to paid tier

### Data Files Not Found
1. Ensure `data/` folder is committed to Git
2. Check file paths are relative, not absolute
3. Use `Path(__file__).parent` for relative paths

## 🎯 Post-Deployment

Once deployed, your app will be available at:
```
https://[your-app-name].streamlit.app
```

You can:
- Share this URL with anyone
- Auto-redeploy on every git push
- Monitor logs in the Streamlit Cloud dashboard
- Update secrets without redeploying

## 🔄 Updating Your App

Any push to your GitHub repository will automatically trigger a redeployment!

```bash
git add .
git commit -m "Update app"
git push origin main
```

The app will rebuild and redeploy automatically (usually takes 2-3 minutes).

## 📊 Monitoring

- View logs in real-time from Streamlit Cloud dashboard
- Check resource usage (CPU, memory)
- See visitor analytics

## 💡 Tips for Better Performance

1. **Cache expensive operations**:
```python
@st.cache_data
def load_data():
    return pd.read_csv("data/train.csv")

@st.cache_resource
def load_model():
    return pipeline("text-classification", model="...")
```

2. **Lazy load models**: Only load when needed
3. **Optimize data loading**: Use parquet instead of CSV for large files
4. **Implement pagination**: Don't load all data at once

## 🆘 Need Help?

- Streamlit Community Forum: https://discuss.streamlit.io/
- Documentation: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Issues: Report bugs in your repository

---

**Good luck with your deployment! 🚀**
