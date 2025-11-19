# Hospital Website - Next.js Frontend

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd next_frontend
npm install livekit-client
```

### 2. Run the Development Server
```bash
npm run dev
```

The website will be available at: **http://localhost:3000**

## 📦 What's Included

- ✅ Clean, light-themed hospital website
- ✅ Department showcase
- ✅ Quick information cards (visiting hours, cafeteria, facilities)
- ✅ AI Voice Assistant integration (ready for LiveKit)
- ✅ Responsive design with Tailwind CSS
- ✅ Modern Next.js 16 with TypeScript

## 🔧 Next Steps

1. **Install LiveKit Client** (run in next_frontend folder):
   ```bash
   npm install livekit-client
   ```

2. **Update VoiceAssistant Component** to use LiveKit
   - File: `app/components/VoiceAssistant.tsx`
   - Add LiveKit Room connection
   - Add audio handling

3. **Start Backend Services**:
   - Terminal 1: `cd backend && uv run api/server.py` (FastAPI on port 8000)
   - Terminal 2: `cd backend && uv run voice-agent/query_engine.py dev` (LiveKit agent)
   - Terminal 3: `cd next_frontend && npm run dev` (Next.js on port 3000)

## 📁 File Structure

```
next_frontend/
├── app/
│   ├── components/
│   │   └── VoiceAssistant.tsx    # Voice assistant component
│   ├── globals.css                # Global styles
│   ├── layout.tsx                 # Root layout
│   └── page.tsx                   # Main page
├── package.json
├── next.config.ts
└── tsconfig.json
```

## 🎨 Features

### Main Page
- Hospital header with logo and contact info
- Hero section with welcome message
- Interactive voice assistant card
- Department grid (Cardiology, Pediatrics, etc.)
- Quick info cards (hours, facilities)
- Clean footer

### Voice Assistant
- Connection status indicator
- Sample questions guide
- Connect/Disconnect buttons
- Error handling
- Modern gradient design

## 🔗 Backend Integration

The voice assistant connects to:
- **Backend API**: `http://localhost:8000` (FastAPI)
- **LiveKit**: Cloud-hosted real-time communication

Make sure your backend API is running before connecting the voice assistant!
