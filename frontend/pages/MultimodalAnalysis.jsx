import React, { useState, useRef } from "react";
import ConfidenceMeter from "../components/ConfidenceMeter";

export default function MultimodalAnalysis() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    setErrorMsg(null);
    const droppedFile = e.dataTransfer.files[0];
    validateAndSetFile(droppedFile);
  };

  const handleFileSelect = (e) => {
    setErrorMsg(null);
    const selectedFile = e.target.files[0];
    validateAndSetFile(selectedFile);
  };

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;
    const fileExt = selectedFile.name.split(".").pop().toLowerCase();
    const isValidExt = ["mp4", "avi", "mov", "mkv"].includes(fileExt);

    if (!isValidExt) {
      setErrorMsg("Unsupported format. Please upload a video container (MP4, MOV, AVI, MKV).");
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setErrorMsg("File size exceeds 50MB. Please use compressed media assets.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
  };

  const analyzeMedia = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setProgress(10);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Incremental simulation of demux and model loading
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev < 40) return prev + 15;
          if (prev < 80) return prev + 5;
          return prev;
        });
      }, 500);

      const response = await fetch("http://localhost:8000/api/v1/forensics/multimodal/predict", {
        method: "POST",
        body: formData
      });

      clearInterval(interval);
      setProgress(100);

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || "Multimodal fusion extraction failed.");
      }

      setResult(data);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Failed during multimodal forensic stream processing.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetScanner = () => {
    setFile(null);
    setResult(null);
    setErrorMsg(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="w-full min-h-screen bg-slate-950 py-12 px-6">
      <div className="max-w-6xl mx-auto flex flex-col gap-8">
        
        {/* Page Title */}
        <div className="flex justify-between items-center border-b border-slate-900 pb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-cyan-500 flex items-center justify-center font-black text-white shadow-lg shadow-purple-500/20">
              MM
            </div>
            <div>
              <h1 className="text-xl font-black uppercase tracking-widest text-white leading-none">Multimodal Fusion Station</h1>
              <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Correlating audio + video deepfake signatures</p>
            </div>
          </div>
          <button 
            onClick={resetScanner}
            className="text-xs text-slate-400 hover:text-white border border-slate-800 hover:bg-slate-900 px-4 py-2 rounded-xl transition-all font-semibold"
          >
            Clear Station
          </button>
        </div>

        {errorMsg && (
          <div className="bg-rose-950/40 border border-rose-800 text-rose-300 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
            <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {errorMsg}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Main Upload / Media Station */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {!file ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`py-16 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 bg-slate-900/20 ${
                  isDragOver ? "border-purple-500 bg-purple-950/10 text-purple-300" : "border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-300"
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  className="hidden"
                  accept=".mp4,.avi,.mov,.mkv"
                />
                <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-850 flex items-center justify-center text-purple-400 shadow-xl mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a2 2 0 002-2V6a2 2 0 00-2-2H4a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="text-sm font-bold text-slate-200">Drag and drop your video file here</p>
                <p className="text-xs text-slate-500 mt-1">Supports MP4, MOV, MKV up to 50MB</p>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col gap-4">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
                      <svg className="w-6 h-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="overflow-hidden">
                      <p className="text-sm font-bold text-white truncate max-w-md">{file.name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                  </div>
                  {!isAnalyzing && !result && (
                    <button 
                      onClick={resetScanner}
                      className="text-slate-500 hover:text-rose-400 p-2 hover:bg-rose-500/10 rounded-lg transition-all"
                    >
                      Remove
                    </button>
                  )}
                </div>

                {isAnalyzing && (
                  <div className="w-full flex flex-col gap-2.5 my-2">
                    <div className="flex justify-between items-center text-xs font-bold">
                      <span className="text-purple-400 animate-pulse">De-muxing audio channels & running neural scans...</span>
                      <span className="text-slate-400">{progress}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-950 rounded-full border border-slate-850 overflow-hidden">
                      <div 
                        style={{ width: `${progress}%` }}
                        className="h-full bg-gradient-to-r from-purple-500 to-cyan-500 shadow-md shadow-purple-500/50 rounded-full transition-all duration-300"
                      />
                    </div>
                  </div>
                )}

                {!isAnalyzing && !result && (
                  <button
                    onClick={analyzeMedia}
                    className="w-full py-3 bg-gradient-to-r from-purple-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white font-bold rounded-xl text-sm transition-all duration-200 shadow-lg hover:shadow-purple-950/40"
                  >
                    Run Multimodal Forensic Analysis
                  </button>
                )}
              </div>
            )}

            {/* Results breakdown */}
            {result && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col gap-6 animate-fadeIn">
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest border-b border-slate-800/80 pb-3">Detailed Modality Diagnostic</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Video details */}
                  <div className="bg-slate-950/30 border border-slate-800/80 rounded-xl p-4 flex flex-col gap-2.5">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-400">Video Channel</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        result.video_prediction === "FAKE" ? "bg-rose-500/20 text-rose-400 border border-rose-500/20" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/20"
                      }`}>
                        {result.video_prediction || "UNKNOWN"}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-500">Spatial Confidence</span>
                      <span className="text-white font-bold font-mono">{result.video_confidence ? result.video_confidence.toFixed(2) : "0.00"}%</span>
                    </div>
                  </div>

                  {/* Audio details */}
                  <div className="bg-slate-950/30 border border-slate-800/80 rounded-xl p-4 flex flex-col gap-2.5">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-400">Acoustic Channel</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        result.audio_prediction === "FAKE" || result.audio_prediction === "FAKE_VOICE" ? "bg-rose-500/20 text-rose-400 border border-rose-500/20" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/20"
                      }`}>
                        {result.audio_prediction || "UNKNOWN"}
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-500">Synthesizer Confidence</span>
                      <span className="text-white font-bold font-mono">{result.audio_confidence ? result.audio_confidence.toFixed(2) : "0.00"}%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-950/50 border border-slate-850 rounded-xl p-4 flex flex-col gap-2.5 text-xs text-slate-400">
                  <div className="flex justify-between border-b border-slate-900 pb-2">
                    <span>Fusion Strategy</span>
                    <span className="text-white font-bold font-mono">Weighted Decision Fusion</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Forensic Engine Latency</span>
                    <span className="text-white font-bold font-mono">{result.processing_time ? result.processing_time.toFixed(3) : "0.0"} seconds</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Fusion Indicator column */}
          <div className="flex flex-col gap-6">
            <ConfidenceMeter
              percentage={result?.success ? (result.confidence || 0) : 0}
              isFake={result?.success ? (result.prediction === "FAKE" || result.prediction === "FAKE_VOICE") : false}
              subtitle={result?.success ? "Integrated Multimodal Decision Fused" : "Awaiting media analysis..."}
            />

            {result && (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Fusion Report Log</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {result.prediction === "FAKE" || result.prediction === "FAKE_VOICE" 
                    ? "🚨 CRITICAL: The decision fusion model combined spatial neural anomalies and synthesised frequency parameters to output an overall MANIPULATED verdict."
                    : "✔ SECURE: The joint visual attributions and acoustic spectrum profiles confirm this media is authentic and un-synthesised."
                  }
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
