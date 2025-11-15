import { useState, useEffect } from 'react'
import './App.css'
import { Room, RoomEvent } from 'livekit-client'

const API_URL = 'http://localhost:8000'

interface ConnectionResponse {
  token: string
  url: string
  room_name: string
}

function App() {
  const [userName, setUserName] = useState('Patient')
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [status, setStatus] = useState('')
  const [statusType, setStatusType] = useState<'info' | 'success' | 'error'>('info')
  const [room, setRoom] = useState<Room | null>(null)

  useEffect(() => {
    // Check server health on load
    checkServerHealth()
  }, [])

  const checkServerHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`)
      const data = await response.json()
      if (data.status === 'healthy') {
        console.log('✅ Server is healthy')
      }
    } catch (error) {
      showStatus('⚠️ Cannot connect to server. Make sure the API is running on port 8000.', 'error')
    }
  }

  const showStatus = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    setStatus(message)
    setStatusType(type)
  }

  const connect = async () => {
    if (!userName.trim()) {
      showStatus('Please enter your name', 'error')
      return
    }

    setIsConnecting(true)
    showStatus('Connecting to hospital assistant...', 'info')

    try {
      // Request connection token from backend
      const response = await fetch(`${API_URL}/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_name: userName.trim()
        })
      })

      if (!response.ok) {
        throw new Error('Failed to connect to server')
      }

      const data: ConnectionResponse = await response.json()

      // Connect to LiveKit room
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
      })

      // Handle audio track
      newRoom.on(RoomEvent.TrackSubscribed, (track: any) => {
        if (track.kind === 'audio') {
          const audioElement = track.attach()
          document.body.appendChild(audioElement)
          showStatus('🎧 Connected! Speak to the assistant...', 'success')
        }
      })

      newRoom.on(RoomEvent.Disconnected, () => {
        showStatus('Disconnected from assistant', 'info')
        setIsConnected(false)
        setRoom(null)
        // Remove audio elements
        document.querySelectorAll('audio').forEach(el => el.remove())
      })

      // Connect to room
      await newRoom.connect(data.url, data.token)

      // Enable microphone
      await newRoom.localParticipant.setMicrophoneEnabled(true)

      setRoom(newRoom)
      setIsConnected(true)
      setIsConnecting(false)
      showStatus('🎤 Connected! Start speaking...', 'success')

    } catch (error) {
      console.error('Connection error:', error)
      showStatus(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
      setIsConnecting(false)
    }
  }

  const disconnect = async () => {
    if (room) {
      await room.disconnect()
      setRoom(null)
      setIsConnected(false)
      // Remove audio elements
      document.querySelectorAll('audio').forEach(el => el.remove())
    }
  }

  return (
    <div className="app-container">
      <div className="card">
        <div className="header">
          <h1>🏥 Hospital Assistant</h1>
          <p className="subtitle">Voice-enabled AI assistant for Arogya Med-City Hospital</p>
        </div>

        <div className="content">
          <div className="input-group">
            <label htmlFor="userName">Your Name</label>
            <input
              type="text"
              id="userName"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              disabled={isConnected}
            />
          </div>

          <div className="button-group">
            {!isConnected ? (
              <button
                className="btn-primary"
                onClick={connect}
                disabled={isConnecting}
              >
                {isConnecting ? (
                  <>
                    <span className="loading"></span> Connecting...
                  </>
                ) : (
                  <>🎤 Start Voice Chat</>
                )}
              </button>
            ) : (
              <button
                className="btn-secondary"
                onClick={disconnect}
              >
                ⏹️ End Session
              </button>
            )}
          </div>

          {status && (
            <div className={`status ${statusType}`}>
              {status}
            </div>
          )}
        </div>

        <div className="footer">
          <p>Powered by LiveKit & AI</p>
        </div>
      </div>
    </div>
  )
}

export default App
