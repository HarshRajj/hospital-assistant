# Hospital Voice Assistant - Frontend

Beautiful React TypeScript interface for the Hospital Voice Assistant.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will run on `http://localhost:5173`

### 3. Make sure Backend is Running

**Terminal 1: API Server**
```powershell
cd backend
uv run api/server.py
```

**Terminal 2: Voice Agent**
```powershell
cd backend
uv run voice-agent/query_engine.py dev
```

---

## 📦 Features

✅ Beautiful modern UI with gradient design  
✅ Real-time voice chat with AI assistant  
✅ Connection status indicators  
✅ Responsive design for mobile/desktop  
✅ Smooth animations and transitions  
✅ LiveKit WebRTC integration  

---

## 🎨 Tech Stack

- **React 18** - UI Framework
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **LiveKit Client** - WebRTC Voice Communication
- **CSS3** - Styling with animations

---

## 🔧 Configuration

The frontend connects to the backend API at `http://localhost:8000`

To change this, edit `src/App.tsx`:
```typescript
const API_URL = 'http://localhost:8000'  // Change if needed
```

---

## 🎯 How It Works

1. User enters their name
2. Clicks "Start Voice Chat"
3. Frontend calls `/connect` API endpoint
4. Receives LiveKit token
5. Connects to LiveKit room via WebRTC
6. Enables microphone
7. Speaks to AI assistant
8. Receives voice responses in real-time

---

## 📱 Responsive Design

The UI adapts to:
- 📱 Mobile (< 600px)
- 💻 Tablet (600px - 900px)
- 🖥️ Desktop (> 900px)

---

## 🛠️ Development

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 🎨 Customization

### Colors
Edit `src/App.css` gradient:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Hospital Name
Edit `src/App.tsx`:
```tsx
<p className="subtitle">Voice-enabled AI assistant for Your Hospital Name</p>
```

---

## 📄 File Structure

```
src/
├── App.tsx          # Main React component with LiveKit logic
├── App.css          # Component-specific styles
├── index.css        # Global styles
├── main.tsx         # React entry point
└── assets/          # Images, icons, etc.
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Kill the process on port 5173
npx kill-port 5173
```

### LiveKit connection fails
- Check backend API is running on port 8000
- Check voice agent is running
- Verify `.env` has correct LiveKit credentials
- Check browser console for errors

### No audio
- Grant microphone permissions in browser
- Check speaker/headphone volume
- Verify voice agent is connected to LiveKit

---

## 🚀 Deployment

### Build
```bash
npm run build
```

This creates a `dist/` folder with optimized files.

### Deploy to Vercel/Netlify
```bash
# Vercel
vercel deploy

# Netlify
netlify deploy --prod
```

### Environment Variables
Set in your hosting platform:
```
VITE_API_URL=https://your-backend-api.com
```

Then update `App.tsx`:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

---

## 📚 Learn More

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [LiveKit Client SDK](https://docs.livekit.io/client-sdk-js/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

Happy coding! 🎉
