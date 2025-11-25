# 🏥 Hospital AI Assistant

AI-powered hospital assistant with voice chat, text chat, and appointment booking for Arogya Med-City Hospital.

## ✨ Features

- 🎤 **Voice Assistant** - Real-time voice conversation with AI
- 💬 **Chat Assistant** - Fast text-based Q&A
- 📅 **Appointment Booking** - Schedule appointments via UI, chat, or voice
- 🔐 **User Authentication** - Secure sign-up/sign-in with Clerk
- 🧠 **RAG-Powered** - Accurate answers from hospital knowledge base
- ⚡ **Ultra-Fast** - FREE Cerebras LLM (~1-2s responses)
- 📱 **Responsive** - Works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Clerk Account](https://clerk.com) (free)
- [LiveKit Account](https://livekit.io) (free tier)
- API Keys: Cerebras, Google Gemini, Deepgram, Cartesia

### 1. Clone Repository
```bash
git clone https://github.com/HarshRajj/hospital-assistant.git
cd hospital-assistant
```

### 2. Backend Setup
```bash
cd backend
# Copy .env and add your API keys
uv sync
```

### 3. Frontend Setup
```bash
cd next_frontend
npm install
# Update .env.local with Clerk keys
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
uv run python -m uvicorn api.server:app --reload --port 8000
```

**Terminal 2 - Voice Agent (optional):**
```bash
cd backend
uv run voice-agent/agent.py dev
```

**Terminal 3 - Frontend:**
```bash
cd next_frontend
npm run dev
```

**Visit:** http://localhost:3000

## 🎯 Usage

### Voice Assistant
1. Sign up/Sign in
2. Click "Start Voice Chat"
3. Ask questions: "What are cafeteria hours?" or "Book appointment in Cardiology"

### Chat Assistant
1. Type your question
2. Get instant answers
3. Works without login!

### Appointment Booking
1. Sign in
2. Select department, doctor, date, time
3. Confirm booking
4. View/cancel in "My Appointments"

## 📁 Project Structure

```
hospital-assistant/
├── backend/
│   ├── api/server.py           # FastAPI endpoints
│   ├── services/               # Business logic
│   │   ├── chat_service.py     # Chat + RAG + booking
│   │   ├── appointment_service.py  # Appointment management
│   │   ├── rag_service.py      # Knowledge base search
│   │   └── auth_service.py     # Authentication
│   ├── voice-agent/agent.py    # LiveKit voice agent
│   ├── data/Knowledgebase.txt  # Hospital info
│   └── storage/local_index/    # FAISS embeddings
├── next_frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── VoiceAssistant.tsx
│   │   │   ├── ChatAssistant.tsx
│   │   │   └── CalendarBooking.tsx
│   │   ├── layout.tsx          # ClerkProvider
│   │   └── page.tsx            # Main page
│   └── middleware.ts           # Clerk auth
└── README.md
```

## 🛠️ Tech Stack

**Frontend:**
- Next.js 16 (App Router)
- TypeScript + Tailwind CSS
- Clerk (Authentication)
- LiveKit Client (Voice)

**Backend:**
- FastAPI (Python)
- Cerebras LLM (FREE, ultra-fast)
- Google Gemini (FREE embeddings)
- FAISS (Local vector store)
- LiveKit (Voice infrastructure)
- Deepgram (Speech-to-Text)
- Cartesia (Text-to-Speech)

**Data:**
- In-memory appointments (no database)
- Local FAISS index (no cloud costs)

## 🔑 Environment Variables

**Backend (`backend/.env`):**
```env
# LLM & Embeddings (FREE)
CEREBRAS_API_KEY=your_key
GOOGLE_API_KEY=your_key

# Voice (Paid)
LIVEKIT_URL=wss://...
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
DEEPGRAM_API_KEY=your_key
CARTESIA_API_KEY=your_key

# Auth
CLERK_SECRET_KEY=sk_test_...
```

**Frontend (`next_frontend/.env.local`):**
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_LIVEKIT_URL=wss://...
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## 💡 Key Highlights

- ✅ **Zero Database Cost** - In-memory storage
- ✅ **FREE LLM** - Cerebras gpt-oss-120b
- ✅ **FREE Embeddings** - Google Gemini (15K/day)
- ✅ **Local Vector Store** - FAISS (no Pinecone)
- ✅ **Production Ready** - Clerk auth + deployment configs
- ✅ **3 Booking Methods** - UI, Chat, Voice

## 📄 License

MIT License

## 🙏 Credits

Built with [LiveKit](https://livekit.io), [Clerk](https://clerk.com), [Cerebras](https://cerebras.ai), [LlamaIndex](https://llamaindex.ai)

---

**Made with ❤️ for accessible healthcare**
