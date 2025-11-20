# 🚀 Deployment Guide

## Overview

- **Backend (API + Voice Agent)**: Deploy to Render
- **Frontend (Next.js)**: Deploy to Vercel
- **Communication**: Frontend calls Backend API via HTTPS

---

## 📦 Backend Deployment (Render)

### Option 1: Using render.yaml (Blueprint)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configs"
   git push origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Deploy with Blueprint**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

4. **Set Environment Variables** (in Render dashboard)
   
   For **hospital-assistant-api**:
   ```
   LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=sk-...
   ```
   
   For **hospital-voice-agent**:
   ```
   LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=sk-...
   DEEPGRAM_API_KEY=your_deepgram_key (optional)
   ```

5. **Wait for Deployment**
   - API service will be at: `https://hospital-assistant-api.onrender.com`
   - Voice agent runs as background worker

### Option 2: Manual Deployment

1. **Deploy API Service**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect GitHub repo
   - Settings:
     - **Name**: hospital-assistant-api
     - **Region**: Oregon (or closest to you)
     - **Branch**: main
     - **Root Directory**: backend
     - **Build Command**: `pip install uv && uv sync`
     - **Start Command**: `uv run uvicorn api.server:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: Free

2. **Deploy Voice Agent Worker**
   - Click "New" → "Background Worker"
   - Connect GitHub repo
   - Settings:
     - **Name**: hospital-voice-agent
     - **Root Directory**: backend
     - **Build Command**: `pip install uv && uv sync && uv run scripts/upload_embeddings.py --storage local`
     - **Start Command**: `uv run voice-agent/query_engine.py start`
     - **Instance Type**: Free

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Vercel Project

1. **Install Vercel CLI** (optional)
   ```bash
   npm i -g vercel
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

### Step 2: Deploy to Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com
   - Sign in with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your `hospital-assistant` repository
   - Vercel auto-detects Next.js

3. **Configure Build Settings**
   - **Framework Preset**: Next.js
   - **Root Directory**: `next_frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Set Environment Variables**
   ```
   NEXT_PUBLIC_BACKEND_URL=https://hospital-assistant-api.onrender.com
   ```
   
   ⚠️ **Important**: Use your actual Render API URL from step above

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be at: `https://hospital-assistant-xxx.vercel.app`

---

## 🔗 Connecting Frontend to Backend

### Update CORS in Backend

Once you have your Vercel URL, update `backend/api/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-vercel-app.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy on Render (automatic if connected to GitHub).

---

## ✅ Deployment Checklist

### Before Deploying:

- [ ] Push all code to GitHub
- [ ] Have LiveKit account and credentials ready
- [ ] Have OpenAI API key ready
- [ ] (Optional) Have Deepgram API key for faster STT

### Backend (Render):

- [ ] API service deployed and running
- [ ] Voice agent worker deployed and running
- [ ] All environment variables set
- [ ] Knowledge base created (happens during build)
- [ ] Note the API URL: `https://hospital-assistant-api.onrender.com`

### Frontend (Vercel):

- [ ] Project imported and deployed
- [ ] Environment variable `NEXT_PUBLIC_BACKEND_URL` set to Render API URL
- [ ] CORS updated in backend to include Vercel URL
- [ ] Test the deployment

---

## 🧪 Testing Deployed App

1. **Visit your Vercel URL**
   ```
   https://your-app.vercel.app
   ```

2. **Click "Start Voice Chat"**

3. **Check if it connects**
   - Should request microphone permission
   - Should connect to LiveKit
   - Should respond to voice questions

4. **Test with questions**:
   - "What are the cafeteria hours?"
   - "Tell me about Cardiology department"

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Check:**
- Is `NEXT_PUBLIC_BACKEND_URL` set correctly in Vercel?
- Is backend API running on Render?
- Visit `https://hospital-assistant-api.onrender.com/health`
- Should return `{"status":"healthy"}`

### CORS errors

**Fix:**
- Add Vercel URL to CORS in `backend/api/server.py`
- Redeploy backend on Render
- Clear browser cache

### Voice agent not responding

**Check Render logs:**
- Go to Render dashboard
- Click on `hospital-voice-agent` worker
- Check logs for errors
- Verify all environment variables are set

### "Failed to get token"

**Check:**
- Backend API is running
- LiveKit credentials are correct
- Visit backend `/connect` endpoint directly

---

## 💰 Cost Breakdown

### Free Tier Limits:

**Render (Free)**:
- Web Service: 750 hours/month
- Background Worker: 750 hours/month
- Apps sleep after 15 minutes of inactivity
- ⚠️ Cold starts take ~30 seconds

**Vercel (Free)**:
- Unlimited deployments
- 100GB bandwidth/month
- Serverless functions included
- No sleep time

**Total Monthly Cost**: $0 (using free tiers)

### Upgrade Options:

If you need 24/7 uptime without sleep:
- **Render Starter**: $7/month per service
- **Vercel Pro**: $20/month

---

## 🔄 Continuous Deployment

Both Render and Vercel support auto-deployment:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Automatic Deployment**
   - Render rebuilds backend automatically
   - Vercel rebuilds frontend automatically
   - Takes 2-5 minutes

---

## 📝 Environment Variables Summary

### Render (Backend API + Worker)

```env
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=... (optional)
RAG_STORAGE_TYPE=local
```

### Vercel (Frontend)

```env
NEXT_PUBLIC_BACKEND_URL=https://hospital-assistant-api.onrender.com
```

---

## 🎉 Success!

Your hospital voice assistant is now live!

- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://hospital-assistant-api.onrender.com
- **Voice Agent**: Running on Render as background worker

Share your app with the world! 🚀
