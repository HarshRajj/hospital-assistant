"use client";

import { useEffect, useRef, useState } from "react";
import { Room, RoomEvent, Track } from "livekit-client";

const BACKEND_URL = "http://localhost:8000";

export default function VoiceAssistant() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const roomRef = useRef<Room | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const connectToAgent = async () => {
    setIsConnecting(true);
    setError(null);

    try {
      // Get token from backend
      const response = await fetch(`${BACKEND_URL}/connect`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
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
    <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="inline-block bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full p-4 mb-4">
          <div className="text-4xl">🎤</div>
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Voice Assistant</h3>
        <p className="text-gray-600">
          Ask me anything about the hospital - departments, doctors, timings, and more!
        </p>
      </div>

      {/* Status Section */}
      <div className="bg-gray-50 rounded-xl p-6 mb-6 text-center">
        {isConnected ? (
          <div className="space-y-2">
            <div className="flex items-center justify-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-700 font-semibold">Connected - Listening...</span>
            </div>
            <p className="text-sm text-gray-600">
              🎤 Speak naturally to ask your questions
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2">
            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            <span className="text-gray-600">Not Connected</span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700 text-sm">
            <strong>Error:</strong> {error}
          </p>
        </div>
      )}

      {/* Connect Button */}
      <div className="mb-6">
        {!isConnected ? (
          <button
            onClick={connectToAgent}
            disabled={isConnecting}
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold py-4 px-6 rounded-xl hover:from-blue-600 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          >
            {isConnecting ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <span className="text-2xl">🎤</span>
                <span>Start Voice Chat</span>
              </>
            )}
          </button>
        ) : (
          <button
            onClick={disconnect}
            className="w-full bg-red-500 text-white font-semibold py-4 px-6 rounded-xl hover:bg-red-600 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-3"
          >
            <span className="text-2xl">🔴</span>
            <span>End Chat</span>
          </button>
        )}
      </div>

      {/* Sample Questions */}
      <div className="bg-blue-50 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span>💡</span>
          <span>Try asking:</span>
        </h4>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>"What are the cafeteria hours?"</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>"Tell me about the Cardiology department"</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>"Who are the cardiologists available?"</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>"What are the visiting hours?"</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>"How can I contact Pediatrics?"</span>
          </li>
        </ul>
      </div>

      {/* Footer Note */}
      <p className="text-center text-xs text-gray-500 mt-6">
        Powered by LiveKit • OpenAI • RAG Technology
      </p>
    </div>
  );
}
