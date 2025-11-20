# 🆓 FREE Gemini Embeddings Setup Guide

## Why Gemini?

✅ **Completely FREE**
✅ **15,000 requests per day**
✅ **High-quality embeddings**
✅ **Works on Render/Vercel deployments**
✅ **No credit card required**

## Setup Steps

### 1. Get FREE Google Gemini API Key

1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### 2. Update backend/.env

```env
# Add this line to your backend/.env file:
GOOGLE_API_KEY=your_gemini_api_key_here

# Make sure these are set:
RAG_EMBEDDING_PROVIDER=gemini
RAG_GEMINI_EMBEDDING_MODEL=models/embedding-001
```

### 3. Install Dependencies

```bash
cd backend
uv sync
```

### 4. Create Embeddings

```bash
cd backend
uv run scripts/upload_embeddings_gemini.py
```

**Output:**
```
🆓 Using FREE Google Gemini Embeddings
📦 Model: models/embedding-001
✅ FREE Tier: 15,000 requests/day
...
✅ SUCCESS! Gemini embeddings created and saved!
🆓 Cost: $0.00 (using free tier!)
```

### 5. Run Voice Agent

```bash
cd backend
uv run voice-agent/query_engine.py dev
```

**You should see:**
```
🆓 Using FREE Gemini embeddings: models/embedding-001
✅ Hospital knowledge base loaded from local storage!
```

## ✅ Ready for Deployment!

Your embeddings are now created using FREE Gemini API and stored locally in FAISS.

### For Render Deployment:

Add these environment variables in Render dashboard:
```env
GOOGLE_API_KEY=your_gemini_api_key
RAG_EMBEDDING_PROVIDER=gemini
RAG_GEMINI_EMBEDDING_MODEL=models/embedding-001
```

The build command will automatically create embeddings on deploy:
```bash
uv sync && uv run scripts/upload_embeddings_gemini.py
```

## 📊 Free Tier Limits

- **15,000 requests per day**
- **1,500 requests per minute**
- **No credit card required**

For a hospital assistant, this is MORE than enough!

## 💰 Cost Comparison

| Provider | FREE Tier | Cost After Free |
|----------|-----------|----------------|
| **Gemini** | 15K/day | Always free |
| OpenAI | None | $0.13/1M tokens |
| Cohere | 1K calls/month | $1/1K calls |

**Winner: Gemini! 🎉**

## 🚀 Next Steps

1. Test locally with `uv run voice-agent/query_engine.py dev`
2. Deploy to Render (will use Gemini embeddings)
3. Deploy frontend to Vercel
4. Enjoy your FREE voice assistant!
