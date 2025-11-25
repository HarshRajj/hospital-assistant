"use client";

import { useEffect, useRef, useState } from "react";
import { Room, RoomEvent, Track } from "livekit-client";
import { useAuth } from "@clerk/nextjs";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function VoiceAssistant() {
  const { getToken } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const roomRef = useRef<Room | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Check backend health on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/health`, {
          method: "GET",
          signal: AbortSignal.timeout(3000),
        });
        setBackendHealthy(response.ok);
      } catch {
        setBackendHealthy(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  const connectToAgent = async () => {
    setIsConnecting(true);
    setError(null);

    try {
      // Get Clerk auth token
      const clerkToken = await getToken();
      if (!clerkToken) {
        throw new Error("Not authenticated. Please sign in.");
      }

      // Get token from backend with auth
      const response = await fetch(`${BACKEND_URL}/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${clerkToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get token: ${response.statusText}`);
      }

      const data = await response.json();
      const { token, url } = data;

      console.log("✅ Got token from backend");

      // Create LiveKit room
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      roomRef.current = room;

      // Set up audio element for playback
      if (!audioRef.current) {
        audioRef.current = new Audio();
        audioRef.current.autoplay = true;
      }

      // Handle incoming audio from agent
      room.on(RoomEvent.TrackSubscribed, (track, _publication, participant) => {
        console.log("🎵 Track subscribed:", track.kind, "from", participant.identity);

        if (track.kind === Track.Kind.Audio && audioRef.current) {
          const mediaStream = new MediaStream([track.mediaStreamTrack]);
          audioRef.current.srcObject = mediaStream;
          audioRef.current.play().catch((e) => console.error("Audio play error:", e));
        }
      });

      // Connection events
      room.on(RoomEvent.Connected, () => {
        console.log("✅ Connected to LiveKit room");
        setIsConnected(true);
        setIsConnecting(false);
      });

      room.on(RoomEvent.Disconnected, () => {
        console.log("❌ Disconnected from room");
        setIsConnected(false);
        setIsConnecting(false);
      });

      // Connect to LiveKit
      await room.connect(url, token);
      console.log("🔗 Connecting to LiveKit...");

      // Enable microphone
      await room.localParticipant.setMicrophoneEnabled(true);
      console.log("🎤 Microphone enabled");
    } catch (err) {
      console.error("Connection error:", err);
      setError(err instanceof Error ? err.message : "Failed to connect");
      setIsConnecting(false);
    }
  };

  const disconnect = () => {
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.srcObject = null;
    }
    setIsConnected(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
    };
  }, []);

  return (
    <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 p-8 h-full flex flex-col">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-50 rounded-full mb-6 relative">
          <div className="absolute inset-0 bg-blue-100 rounded-full animate-ping opacity-20"></div>
          <div className="text-4xl">🎤</div>
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Voice Assistant</h3>
        <p className="text-gray-500 text-sm leading-relaxed max-w-sm mx-auto">
          Ask me anything about the hospital - departments, doctors, timings, and more!
        </p>
      </div>

      {/* Status Section */}
      <div className={`rounded-xl p-6 mb-8 text-center transition-colors ${isConnected ? 'bg-green-50 border border-green-100' : 'bg-gray-50 border border-gray-100'}`}>
        {isConnected && backendHealthy ? (
          <div className="space-y-3">
            <div className="flex items-center justify-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
              <span className="text-green-700 font-semibold">Listening...</span>
            </div>
            <div className="flex justify-center gap-1 h-4 items-end">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="w-1 bg-green-500 rounded-full animate-[bounce_1s_infinite]" style={{ animationDelay: `${i * 0.1}s`, height: '100%' }}></div>
              ))}
            </div>
          </div>
        ) : backendHealthy === false ? (
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-red-400 rounded-full"></div>
            <span className="text-red-500 font-medium">Backend not running</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span className="text-gray-500 font-medium">Ready to connect</span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-100 rounded-xl p-4 mb-6 flex items-start gap-3">
          <span className="text-red-500 mt-0.5">⚠️</span>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Connect Button */}
      <div className="mb-8">
        {!isConnected ? (
          <button
            onClick={connectToAgent}
            disabled={isConnecting || backendHealthy === false}
            className="w-full group relative overflow-hidden bg-gray-900 text-white font-semibold py-4 px-6 rounded-xl hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <div className="relative z-10 flex items-center justify-center gap-3">
              {isConnecting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Connecting...</span>
                </>
              ) : backendHealthy === false ? (
                <>
                  <span>⚠️</span>
                  <span>Backend Offline</span>
                </>
              ) : (
                <>
                  <span className="group-hover:scale-110 transition-transform">🎙️</span>
                  <span>Start Voice Chat</span>
                </>
              )}
            </div>
          </button>
        ) : (
          <button
            onClick={disconnect}
            className="w-full bg-white border-2 border-red-100 text-red-600 font-semibold py-4 px-6 rounded-xl hover:bg-red-50 transition-all flex items-center justify-center gap-3"
          >
            <span>⏹️</span>
            <span>End Conversation</span>
          </button>
        )}
      </div>

      {/* Sample Questions */}
      <div className="mt-auto">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 text-center">Suggested Questions</p>
        <div className="space-y-2">
          {[
            "What are the cafeteria hours?",
            "Tell me about Cardiology",
          ].map((q, i) => (
            <button
              key={i}
              className="w-full text-left text-sm text-gray-600 p-3 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-100 flex items-center gap-3 group"
            >
              <span className="text-gray-300 group-hover:text-blue-500 transition-colors">💬</span>
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
