import React, { useEffect, useRef, useState } from "react";

export default function WebcamDetector({ socketUrl = "ws://localhost:8000/api/v1/forensics/realtime/stream", onPrediction }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  
  const [isActive, setIsActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState(0);
  const [prediction, setPrediction] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Time tracker for FPS and Latency metrics
  const lastFrameTimeRef = useRef(Date.now());
  const sentTimesRef = useRef([]);

  // Access the webcam stream
  const startCamera = async () => {
    try {
      setErrorMsg(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, frameRate: { ideal: 30 } },
        audio: false
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsActive(true);
      }
      connectWebSocket();
    } catch (err) {
      console.error("Camera access failed:", err);
      setErrorMsg("Failed to access camera. Please verify permissions.");
    }
  };

  // Turn off webcam and disconnect
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
    setIsActive(false);
    setIsConnected(false);
    setPrediction(null);
  };

  // Set up WebSocket connection
  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(socketUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log("Forensics WebSocket connection established.");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setPrediction(data);
        
        // Handle latency calculations using FIFO queue
        const sentTime = sentTimesRef.current.shift();
        if (sentTime) {
          const roundtrip = Date.now() - sentTime;
          setLatency(roundtrip);
        }

        // Calculate receiving FPS
        const now = Date.now();
        const delta = now - lastFrameTimeRef.current;
        lastFrameTimeRef.current = now;
        setFps(Math.round(1000 / delta));

        if (onPrediction) {
          onPrediction(data);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setErrorMsg("WebSocket communication error occurred.");
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log("WebSocket disconnected.");
      };
    } catch (err) {
      console.error("WebSocket setup failed:", err);
      setErrorMsg("Failed to establish server connection.");
    }
  };

  // Stream captured frame segments
  useEffect(() => {
    let intervalId;
    if (isActive && isConnected) {
      intervalId = setInterval(() => {
        if (!videoRef.current || !canvasRef.current || !wsRef.current) return;
        if (wsRef.current.readyState !== WebSocket.OPEN) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        // Set dimensions
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;

        // Draw current video frame to hidden canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to binary JPEG Blob and stream
        canvas.toBlob((blob) => {
          if (blob && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            // Track request sent timestamp
            sentTimesRef.current.push(Date.now());
            // Send binary frame bytes directly
            wsRef.current.send(blob);
          }
        }, "image/jpeg", 0.7);
      }, 100); // 10 FPS streaming frequency for reliable network transmission
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isActive, isConnected]);

  // Clean up component on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="w-full flex flex-col bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-2xl transition-all duration-300 hover:shadow-cyan-950/20">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">Live Webcam Feed</h2>
          <p className="text-xs text-slate-400 mt-1">Real-time facial manipulation and deepfake analysis</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
            isConnected ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
          }`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-emerald-400 animate-pulse" : "bg-rose-400"}`}></span>
            {isConnected ? "CONNECTED" : "DISCONNECTED"}
          </span>
          
          <button
            onClick={isActive ? stopCamera : startCamera}
            className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all duration-200 shadow-md ${
              isActive 
                ? "bg-rose-600 hover:bg-rose-500 text-white hover:shadow-rose-950/40" 
                : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white hover:shadow-cyan-950/40"
            }`}
          >
            {isActive ? "Stop Stream" : "Start Live Feed"}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="mb-4 bg-rose-950/40 border border-rose-800 text-rose-300 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
          <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {errorMsg}
        </div>
      )}

      {/* Main Video Screen */}
      <div className="relative w-full aspect-video bg-black/60 rounded-xl border border-slate-800/80 overflow-hidden flex items-center justify-center">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover"
          muted
          playsInline
        />

        {/* Hidden processing canvas */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Bounding Box Drawing Overlay */}
        {isActive && isConnected && prediction?.faces && prediction.faces.map((face, index) => {
          // Bounding Box coordinates as percentages from stream_processor responses
          const { x, y, w, h, fake_probability } = face;
          const isFake = fake_probability > 0.5;
          return (
            <div
              key={index}
              style={{
                position: "absolute",
                left: `${x * 100}%`,
                top: `${y * 100}%`,
                width: `${w * 100}%`,
                height: `${h * 100}%`,
                borderColor: isFake ? "#f43f5e" : "#10b981",
                boxShadow: isFake ? "0 0 12px rgba(244, 63, 94, 0.4)" : "0 0 12px rgba(16, 185, 129, 0.4)"
              }}
              className="border-2 rounded-lg transition-all duration-75 flex flex-col justify-end p-1.5"
            >
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded text-white self-start ${
                isFake ? "bg-rose-600/90" : "bg-emerald-600/90"
              }`}>
                {isFake ? "MANIPULATED" : "REAL"} {Math.round(fake_probability * 100)}%
              </span>
            </div>
          );
        })}

        {!isActive && (
          <div className="z-10 flex flex-col items-center gap-3 text-center px-4">
            <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 shadow-xl">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-sm font-semibold text-slate-300">Camera Feed Inactive</p>
            <p className="text-xs text-slate-500 max-w-xs">Click "Start Live Feed" to boot the webcam and stream real-time frames to the deepfake detector.</p>
          </div>
        )}
      </div>

      {/* Latency & Hardware Stats */}
      {isActive && isConnected && (
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3.5 flex flex-col">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Stream FPS</span>
            <span className="text-lg font-extrabold text-white mt-0.5">{fps} <span className="text-xs text-slate-400 font-normal">fps</span></span>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3.5 flex flex-col">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Inference Latency</span>
            <span className="text-lg font-extrabold text-white mt-0.5">{latency} <span className="text-xs text-slate-400 font-normal">ms</span></span>
          </div>
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-3.5 flex flex-col">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">System Verdict</span>
            <span className={`text-sm font-black mt-1 ${
              prediction?.success 
                ? (prediction.fake_probability > 0.5 ? "text-rose-400" : "text-emerald-400")
                : "text-slate-400"
            }`}>
              {prediction?.success 
                ? (prediction.fake_probability > 0.5 ? "🚨 SUSPECTED FAKE" : "✔ AUTHENTIC") 
                : "AWAITING FRAME"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
