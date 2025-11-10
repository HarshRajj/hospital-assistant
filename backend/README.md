# Hospital Assistant - Backend

This directory contains all backend components for the Hospital Assistant voice agent with RAG pipeline.

## 📁 Directory Structure

```
backend/
├── .env                    ← 🔑 Single configuration file (YOU EDIT THIS!)
├── .env.example            ← Template for .env
├── setup-env.ps1           ← Automated setup script
│
├── data/
│   └── Knowledgebase.txt   ← Hospital information (Markdown)
│
├── rag/                    ← RAG Pipeline Module
│   ├── __init__.py
│   ├── config.py           ← RAG configuration
│   ├── embeddings.py       ← Document loading & embeddings
│   ├── vector_store.py     ← Vector storage (Pinecone/Local)
│   ├── retriever.py        ← Query interface
│   ├── requirements.txt    ← Dependencies
│   └── README.md           ← Full RAG documentation
│
├── scripts/                ← Utility Scripts
│   ├── upload_embeddings.py   ← Create vector indices
│   └── test_rag.py            ← Test RAG pipeline
│
├── storage/                ← Local Vector Store
│   └── local_index/        ← (Auto-created by upload script)
│
└── voice-agent/            ← LiveKit Voice Agent
    ├── agent.py            ← Main agent code
    └── .env.example        ← (Reference only - USE backend/.env instead)
```

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
cd rag
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
cd ..
.\setup-env.ps1    # Automated
# OR
cp .env.example .env    # Manual
```

Edit `backend/.env` with your API keys.

### 3. Upload Knowledge Base
```powershell
cd scripts
python upload_embeddings.py --storage local
```

### 4. Test RAG Pipeline
```powershell
python test_rag.py
```

### 5. Run Voice Agent
```powershell
cd ..\voice-agent
uv run agent.py console
```

## ⚙️ Configuration

### Single Source of Truth: `backend/.env`

All components (RAG, Voice Agent, Scripts) load from this **one file**.

```env
# Core
OPENAI_API_KEY=sk-xxx

# LiveKit (for voice agent)
LIVEKIT_URL=wss://xxx
LIVEKIT_API_KEY=xxx
LIVEKIT_API_SECRET=xxx

# RAG
RAG_STORAGE_TYPE=local    # or "pinecone"
RAG_SIMILARITY_TOP_K=2

# Pinecone (optional)
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=us-east-1
```

See `backend/.env.example` for full template.

## 📚 Documentation

| File | Purpose |
|------|---------|
| `ENV_MIGRATION.md` | Environment configuration guide |
| `ENV_FIX_SUMMARY.md` | Why we use single .env |
| `RAG_IMPLEMENTATION.md` | Technical details |
| `rag/README.md` | RAG module documentation |
| `../INSTALLATION.md` | Full installation guide |
| `../QUICKSTART.md` | Quick setup guide |

## 🔑 Environment Variables Reference

### Required for All
- `OPENAI_API_KEY` - OpenAI API key for embeddings

### Required for Voice Agent
- `LIVEKIT_URL` - LiveKit server URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret

### RAG Configuration (Optional - has defaults)
- `RAG_STORAGE_TYPE` - "local" or "pinecone" (default: local)
- `RAG_SIMILARITY_TOP_K` - Number of chunks to retrieve (default: 2)
- `RAG_EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)
- `RAG_DATA_PATH` - Path to knowledge base (default: data/Knowledgebase.txt)
- `RAG_LOCAL_STORAGE_DIR` - Local storage path (default: storage/local_index)

### Required for Pinecone (only if RAG_STORAGE_TYPE=pinecone)
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ENVIRONMENT` - Pinecone region (e.g., us-east-1)
- `PINECONE_INDEX_NAME` - Index name (default: hospital-assistant)

## 🎯 Common Tasks

### Update Knowledge Base
```powershell
# 1. Edit data/Knowledgebase.txt
# 2. Re-upload
cd scripts
python upload_embeddings.py --storage local
```

### Switch Storage Type
```powershell
# Edit backend/.env
RAG_STORAGE_TYPE=pinecone    # or "local"

# Restart agent
cd voice-agent
uv run agent.py console
```

### Test Changes
```powershell
cd scripts
python test_rag.py
```

## 🐛 Troubleshooting

### Import Errors
```powershell
cd rag
pip install -r requirements.txt
```

### API Key Not Found
- Check `backend/.env` exists
- Verify API keys are set correctly
- No spaces around `=` sign

### No Index Found
```powershell
cd scripts
python upload_embeddings.py --storage local
```

### Slow Responses
- Reduce `RAG_SIMILARITY_TOP_K` to 1 in `.env`
- Use local storage instead of Pinecone

## 📖 Learn More

- **RAG Pipeline Details**: `rag/README.md`
- **Environment Setup**: `ENV_MIGRATION.md`
- **Full Installation**: `../INSTALLATION.md`
- **Quick Start**: `../QUICKSTART.md`

## 🎉 You're All Set!

Once configured, the system provides:
- ⚡ Fast retrieval (<500ms)
- 🎯 Accurate hospital information
- 🗣️ Natural voice interaction
- 📊 Dual storage options (local/cloud)
- 🔧 Easy configuration management

---

**Single .env, multiple benefits!** ✨
