# 🚀 Quick Deployment Checklist

## ✅ Pre-Deployment (COMPLETED)
- [x] Fixed missing `os` import in streamlit_app.py
- [x] Created `.streamlit/config.toml` for theme configuration
- [x] Updated `requirements.txt` with version constraints
- [x] Created `.gitignore` to protect sensitive files
- [x] Created secrets template (`.streamlit/secrets.toml.example`)
- [x] Created `DEPLOYMENT.md` guide
- [x] Committed and pushed all changes to GitHub
- [x] Verified data folder size (5MB - OK!)

## 📋 Deployment Steps (DO NOW)

### 1. Sign In to Streamlit Cloud
- Browser is already open at: https://share.streamlit.io/
- Click **"Continue to sign-in"** or **"Sign in with GitHub"**
- Authorize Streamlit to access your GitHub repositories

### 2. Create New App
- Click **"New app"** button
- Fill in the form:
  - **Repository**: `Chayan4505/nlp-reasoning`
  - **Branch**: `main`
  - **Main file path**: `streamlit_app.py`
  - **App URL**: Choose a custom name (e.g., `narrative-guard`)

### 3. Configure Secrets (CRITICAL!)
- Click **"Advanced settings"**
- Find the **"Secrets"** section
- Copy and paste this (with your real API key):

```toml
OPENAI_API_KEY = "not-needed-for-gemini"
GEMINI_API_KEY = "AIzaSyCFvHAaX9TFj2QPrZjWwuD0ZJwMNXyceTM"
PATHWAY_LICENSE_KEY = "pathway-license-key-optional"
USE_DUMMY_LLM = "False"
```

### 4. Deploy!
- Click **"Deploy!"** button
- Wait 5-10 minutes for first build
- Your app will be live at: `https://[your-app-name].streamlit.app`

## ⚠️ Important Notes

### Memory Warning
Your app uses heavy ML models (DeBERTa, sentence-transformers):
- Free tier: 1GB RAM limit
- If app crashes, consider:
  - Using smaller model variants
  - Implementing `@st.cache_resource` for models
  - Upgrading to paid tier ($20/month for 4GB RAM)

### API Key Security
- ✅ Your `.env` file is in `.gitignore` (safe)
- ✅ Use Streamlit Secrets for production API keys
- ❌ Never commit real API keys to GitHub

## 🎯 After Deployment

Once deployed, you can:
- Share the URL with anyone
- Auto-redeploy on every `git push`
- Monitor logs in Streamlit Cloud dashboard
- Update secrets without redeploying

## 🔄 Future Updates

To update your app:
```bash
git add .
git commit -m "Update app"
git push origin main
```

The app will automatically rebuild (2-3 minutes).

## 📊 Monitoring

Access your app dashboard at:
- https://share.streamlit.io/

You can:
- View real-time logs
- Check resource usage
- See visitor analytics
- Manage secrets
- Restart/delete app

## 🆘 Troubleshooting

### Build Fails
- Check logs in Streamlit Cloud dashboard
- Verify all dependencies in `requirements.txt`
- Ensure Python version compatibility

### App Crashes (Out of Memory)
- Implement model caching
- Use smaller models
- Upgrade to paid tier

### Data Not Found
- Ensure `data/` folder is in Git
- Check file paths are relative
- Verify files are not in `.gitignore`

---

**Your app is ready to deploy! Follow the steps above.** 🚀

**Estimated deployment time**: 5-10 minutes
**Your app URL will be**: `https://[your-chosen-name].streamlit.app`
