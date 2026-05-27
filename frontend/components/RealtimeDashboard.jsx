import React, { useState } from "react";
import WebcamDetector from "./WebcamDetector";
import AudioUpload from "./AudioUpload";
import LiveHeatmap from "./LiveHeatmap";
import ConfidenceMeter from "./ConfidenceMeter";

export default function RealtimeDashboard() {
  const [activeTab, setActiveTab] = useState("live"); // 'live' or 'audio'
  const [livePrediction, setLivePrediction] = useState(null);
  
  const handleLivePrediction = (data) => {
    setLivePrediction(data);
  };

  const isLiveFake = livePrediction?.success ? (livePrediction.fake_probability > 0.5) : false;
  const liveConfidence = livePrediction?.success 
    ? (isLiveFake ? livePrediction.fake_probability * 100 : (1 - livePrediction.fake_probability) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-500 selection:text-black">
      {/* Dynamic Background Gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-950/20 via-slate-950 to-slate-950 -z-10 pointer-events-none" />

      {/* Premium Header */}
      <header className="border-b border-slate-900 bg-slate-950/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white shadow-lg shadow-cyan-500/20 tracking-wider">
              AG
            </div>
            <div>
              <h1 className="text-sm font-black uppercase tracking-widest text-white leading-none">Antigravity Forensics</h1>
              <p className="text-[9px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Deepfake & Voice Clone platform</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1.5 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800/80">
            <button
              onClick={() => setActiveTab("live")}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 ${
                activeTab === "live"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Live Video Lab
            </button>
            <button
              onClick={() => setActiveTab("audio")}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 ${
                activeTab === "audio"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Voice Clone Lab
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        
        {/* Banner Section */}
        <div className="mb-8 bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-850 rounded-2xl p-6 relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-xl">
          <div>
            <h2 className="text-xl font-black tracking-wide text-white">Forensic Detection Console</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-xl">
              An enterprise-grade platform monitoring convolutional gradients, spatial splice points, and synthesized frequencies to verify media authenticity.
            </p>
          </div>
          <div className="flex items-center gap-4 shrink-0 bg-slate-900/40 px-5 py-3 border border-slate-850 rounded-xl">
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-500 font-bold uppercase">System Status</span>
              <span className="text-xs font-bold text-emerald-400 mt-0.5 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Inference Ready
              </span>
            </div>
            <div className="w-px h-8 bg-slate-800" />
            <div className="flex flex-col">
              <span className="text-[9px] text-slate-500 font-bold uppercase">CUDA Acceleration</span>
              <span className="text-xs font-bold text-cyan-400 mt-0.5">ENABLED (v11.8)</span>
            </div>
          </div>
        </div>

        {/* Tab Workspaces */}
        {activeTab === "live" ? (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
            {/* Webcam Streaming Core */}
            <div className="xl:col-span-2 flex flex-col gap-6">
              <WebcamDetector onPrediction={handleLivePrediction} />
              <LiveHeatmap prediction={livePrediction} />
            </div>

            {/* Side gauges and stats */}
            <div className="flex flex-col gap-6">
              <ConfidenceMeter 
                percentage={livePrediction?.success ? liveConfidence : 0} 
                isFake={isLiveFake} 
                subtitle={livePrediction?.success ? "Real-time webcam frames monitored" : "Awaiting live camera connection..."}
              />
              
              {/* Platform Info Module */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 shadow-2xl">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">Forensic Engines</h3>
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                    <span className="text-xs text-slate-400">Spatial Classifier</span>
                    <span className="text-xs font-bold text-white font-mono">EfficientNet-B4</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                    <span className="text-xs text-slate-400">Sequence Analyzer</span>
                    <span className="text-xs font-bold text-white font-mono">Temporal Transformer</span>
                  </div>
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                    <span className="text-xs text-slate-400">Audio Classifier</span>
                    <span className="text-xs font-bold text-white font-mono">CNN + Wav2Vec2</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">Fusion Processor</span>
                    <span className="text-xs font-bold text-white font-mono">Decision Fusion</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            <AudioUpload />
          </div>
        )}
      </main>
    </div>
  );
}
