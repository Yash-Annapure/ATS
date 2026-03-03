# Deployment Guide

This guide explains how to deploy the **HushHush Recruiter** app, keeping the Backend and Frontend on separate services.

## 1. Backend Deployment (Render.com)

Render is great for Python backends (FastAPI).

1. **Create a Web Service** on Render connected to your GitHub repo.
2. **Build Command**: `uv install` (or standard pip install)
3. **Start Command**: `uvicorn code.backend.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.10` (or matching your local)
5. **Deploy**: Render will give you a URL like `https://hushhush-backend.onrender.com`.

## 2. Frontend Deployment (Streamlit Cloud or Render)

You can deploy the Streamlit app on Streamlit Cloud (easiest) or Render.

### Option A: Streamlit Cloud
1. Connect your GitHub repo.
2. Select `code/UI/UX/app.py` as the entry point.
3. **Advanced Settings**:
   - Add Environment Variable: `BACKEND_URL` = `https://hushhush-backend.onrender.com` (The URL from step 1).

### Option B: Render Web Service
1. Create a new Web Service.
2. **Start Command**: `streamlit run code/UI/UX/app.py --server.port $PORT --server.address 0.0.0.0`
3. **Env Vars**: `BACKEND_URL` = `https://hushhush-backend.onrender.com`

## 3. GitHub Actions (Optional)

If you want to use GitHub Actions to deploy, you would set up a workflow (`.github/workflows/deploy.yml`) that triggers on push. However, for Render/Streamlit Cloud, the "Auto-Deploy on Push" feature is built-in and easier than managing a custom action file.
