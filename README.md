# 🏥 Hospital Voice Assistant

AI-powered voice assistant for Arogya Med-City Hospital with RAG (Retrieval-Augmented Generation) for accurate hospital information.

## ✨ Features

- 🎤 **Real-time voice conversation** using LiveKit
- 🧠 **RAG-powered responses** from hospital knowledge base
- 🌐 **Modern Next.js website** with hospital information
- ⚡ **Fast responses** (~1-2 seconds)
- 📱 **Responsive design** works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- LiveKit account (free tier works)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/HarshRajj/hospital-assistant.git
cd hospital-assistant
```

2. **Set up backend**
```bash
cd backend
cp .env.example .env  # Add your API keys
uv sync  # Install Python dependencies
uv run scripts/upload_embeddings.py --storage local  # Create knowledge base
```

3. **Set up frontend**
```bash
cd next_frontend
npm install
```

### Running the Application

**Terminal 1 - Backend API:**
```bash
cd backend
uv run api/server.py
```

**Terminal 2 - Voice Agent:**
```bash
cd backend
uv run voice-agent/query_engine.py dev
```

**Terminal 3 - Frontend:**
```bash
cd next_frontend
npm run dev
```

**Visit:** http://localhost:3001

## 🎯 Usage

1. Open http://localhost:3001 in your browser
2. Click **"Start Voice Chat"**
3. Allow microphone access
4. Ask questions like:
   - "What are the cafeteria hours?"
   - "Tell me about the Cardiology department"
   - "Who are the cardiologists available?"
   - "What are the visiting hours?"

## 📁 Project Structure

```
hospital-assistant/
├── backend/
│   ├── api/                    # FastAPI server
│   ├── voice-agent/            # LiveKit voice agent
│   ├── data/                   # Hospital knowledge base
│   ├── rag/                    # RAG modules
│   ├── scripts/                # Utility scripts
│   └── storage/                # Vector embeddings
├── next_frontend/              # Next.js website
│   └── app/
│       ├── components/         # React components
│       └── page.tsx            # Main page
└── README.md
```

## 🛠️ Tech Stack

- **Frontend:** Next.js 16, React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, LiveKit Agents
- **Voice:** AssemblyAI (STT), OpenAI GPT-4o-mini (LLM), Cartesia (TTS)
- **RAG:** LlamaIndex, FAISS, OpenAI Embeddings
- **Real-time:** LiveKit (WebRTC)

## 📝 Configuration

Edit `backend/.env`:
```env
# LiveKit
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI
OPENAI_API_KEY=sk-...

# Optional
RAG_STORAGE_TYPE=local
```

## 📄 License

MIT License - feel free to use for your projects!

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io) for real-time voice infrastructure
- [LlamaIndex](https://www.llamaindex.ai) for RAG framework
- [OpenAI](https://openai.com) for embeddings and LLM

---

Made with ❤️ for better healthcare accessibility
