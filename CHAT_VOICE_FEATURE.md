# 💬 Chat + Voice Assistant Feature

## Overview

Your hospital assistant now supports **TWO modes**:

1. **💬 Chat Assistant** - Text-based Q&A using RAG
2. **🎤 Voice Assistant** - Real-time voice conversation using RAG

Both use the **same RAG knowledge base** for consistent answers!

## Features

### Chat Assistant ✅
- ✅ Instant text responses
- ✅ Full conversation history
- ✅ No microphone needed
- ✅ Works on all devices
- ✅ Copy/paste friendly

### Voice Assistant ✅
- ✅ Hands-free operation
- ✅ Natural conversation
- ✅ Real-time responses
- ✅ LiveKit powered
- ✅ Speech-to-text + Text-to-speech

## How to Use

### Start Backend API (with Chat support):
```bash
cd backend
uv run api/server.py
```

**New endpoints:**
- `POST /chat` - Text chat with RAG
- `POST /connect` - Voice assistant token

### Start Voice Agent:
```bash
cd backend
uv run voice-agent/query_engine.py dev
```

### Start Frontend:
```bash
cd next_frontend
npm run dev
```

Visit: **http://localhost:3001**

## Frontend Layout

```
┌─────────────────────────────────────┐
│     Arogya Med-City Hospital        │
├─────────────────────────────────────┤
│                                     │
│  [💬 Chat]  [🎤 Voice]  <-- Tabs   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │                               │ │
│  │   Chat/Voice Interface        │ │
│  │                               │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

## Backend Architecture

```python
# api/server.py

@app.post("/chat")  # NEW! Text chat endpoint
async def chat(request: ChatRequest):
    # Uses RAG to answer questions
    query_engine = rag_index.as_query_engine()
    response = await query_engine.aquery(request.message)
    return {"answer": str(response)}

@app.post("/connect")  # Voice assistant token
async def connect():
    # Generates LiveKit token for voice
    return {"token": jwt_token, "url": LIVEKIT_URL}
```

## API Examples

### Chat API:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the cafeteria hours?"}'
```

**Response:**
```json
{
  "question": "What are the cafeteria hours?",
  "answer": "The cafeteria hours are: Breakfast 6:30 AM - 9:30 AM, Lunch 12:00 PM - 3:00 PM, Dinner 6:00 PM - 9:00 PM.",
  "source": "RAG Knowledge Base"
}
```

## Deployment Notes

### Render (Backend):
Add environment variables:
```env
GOOGLE_API_KEY=your_gemini_key
RAG_EMBEDDING_PROVIDER=gemini
```

The backend now serves BOTH:
- `/chat` endpoint (REST API)
- LiveKit voice agent (WebSocket)

### Vercel (Frontend):
Environment variable:
```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

Frontend automatically uses the backend for both chat and voice!

## Benefits

### Why Both Chat + Voice?

| Feature | Chat | Voice |
|---------|------|-------|
| **Speed** | Instant | 1-2 seconds |
| **Accessibility** | Keyboard/Mouse | Hands-free |
| **Noise** | Works anywhere | Quiet environment needed |
| **History** | Easy to review | Ephemeral |
| **Multitasking** | Can copy/paste | Conversational |

**Best of both worlds!** 🎉

## Sample Questions (Both Modes)

- "What are the cafeteria hours?"
- "Tell me about the Cardiology department"
- "Who are the cardiologists?"
- "What are the visiting hours?"
- "How can I contact Pediatrics?"

## Cost Comparison

| Component | Chat Mode | Voice Mode |
|-----------|-----------|------------|
| **STT** | Not needed | Deepgram (~$0.004/min) |
| **Embeddings** | Gemini (FREE) | Gemini (FREE) |
| **LLM** | GPT-4o-mini (~$0.15/1M) | GPT-4o-mini (~$0.15/1M) |
| **TTS** | Not needed | Cartesia (~$0.05/1M chars) |
| **Infrastructure** | Render/Vercel (FREE) | LiveKit + Render (FREE tier) |

**Chat is cheaper!** But voice is more convenient! 💪

## Testing

### Test Chat:
1. Go to http://localhost:3001
2. Click "💬 Chat Assistant" tab
3. Type: "What are the cafeteria hours?"
4. Press Enter
5. Get instant response!

### Test Voice:
1. Click "🎤 Voice Assistant" tab
2. Click "Start Voice Chat"
3. Allow microphone
4. Say: "What are the cafeteria hours?"
5. Hear the response!

## Troubleshooting

### Chat not working?
- ✅ Check backend running: `http://localhost:8000/health`
- ✅ Verify RAG index exists: `backend/storage/local_index/`
- ✅ Check CORS allows your frontend URL

### Voice not working?
- ✅ Voice agent running: `uv run voice-agent/query_engine.py dev`
- ✅ LiveKit credentials in `.env`
- ✅ Microphone permission granted

---

**Enjoy your dual-mode hospital assistant!** 🏥💬🎤
