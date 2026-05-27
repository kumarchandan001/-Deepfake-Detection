import React, { useState, useRef } from "react";

export default function AudioUpload({ uploadUrl = "http://localhost:8000/api/v1/forensics/audio/predict", onAnalysisComplete }) {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
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
    
    // Check file type
    const validTypes = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav", "audio/ogg", "audio/m4a"];
    const fileExt = selectedFile.name.split(".").pop().toLowerCase();
    const isValidExt = ["wav", "mp3", "ogg", "m4a", "aac"].includes(fileExt);

    if (!validTypes.includes(selectedFile.type) && !isValidExt) {
      setErrorMsg("Invalid file format. Please upload a valid audio file (WAV, MP3, M4A, OGG).");
      return;
    }

    // Check size limit (15MB)
    if (selectedFile.size > 15 * 1024 * 1024) {
      setErrorMsg("File size exceeds the 15MB limit. Please upload a smaller audio clip.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
  };

  const uploadFile = async () => {
    if (!file) return;

    setIsUploading(true);
    setProgress(15);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Simulate incremental upload progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => (prev < 85 ? prev + 10 : prev));
      }, 200);

      const response = await fetch(uploadUrl, {
        method: "POST",
        body: formData
      });

      clearInterval(progressInterval);
      setProgress(100);

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || "Failed to analyze the acoustic profile.");
      }

      setResult(data);
      if (onAnalysisComplete) {
        onAnalysisComplete(data);
      }
    } catch (err) {
      console.error("Audio upload error:", err);
      setErrorMsg(err.message || "An error occurred during audio forensics processing.");
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
    setErrorMsg(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="w-full flex flex-col bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-2xl transition-all duration-300">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white tracking-wide">Acoustic Forensic Lab</h2>
        <p className="text-xs text-slate-400 mt-1">Upload voice recordings to scan for synthesizer artifacts, speech vocoders, and cloned AI vocals.</p>
      </div>

      {errorMsg && (
        <div className="mb-4 bg-rose-950/40 border border-rose-800 text-rose-300 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
          <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {errorMsg}
        </div>
      )}

      {/* Drag & Drop Area */}
      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`w-full py-10 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all duration-350 ${
            isDragOver 
              ? "border-cyan-400 bg-cyan-950/20 text-cyan-300 scale-[0.99]" 
              : "border-slate-800 hover:border-slate-700 bg-slate-950/30 text-slate-400 hover:text-slate-300"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".wav,.mp3,.ogg,.m4a,.aac"
          />
          <div className="w-14 h-14 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-500 shadow-xl mb-4 group-hover:scale-110 transition-all">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <p className="text-sm font-semibold text-slate-300">Drag & drop your voice recording here</p>
          <p className="text-xs text-slate-500 mt-1">Supports WAV, MP3, M4A up to 15MB</p>
          <button className="mt-4 px-4 py-2 bg-slate-850 border border-slate-750 text-slate-300 text-xs font-semibold rounded-lg hover:bg-slate-800 transition-all">
            Browse Storage
          </button>
        </div>
      ) : (
        <div className="w-full bg-slate-950/40 border border-slate-800/80 rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <svg className="w-5 h-5 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <div className="overflow-hidden">
                <p className="text-sm font-bold text-white truncate max-w-[240px] md:max-w-[400px]">{file.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
            </div>
            
            {!isUploading && !result && (
              <button
                onClick={clearFile}
                className="text-slate-400 hover:text-rose-400 transition-colors p-1.5 hover:bg-rose-500/10 rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>

          {/* Progress Bar */}
          {isUploading && (
            <div className="w-full flex flex-col gap-2 mt-2 mb-3">
              <div className="flex justify-between items-center text-xs">
                <span className="text-cyan-400 font-semibold animate-pulse">Running voice clone scan...</span>
                <span className="text-slate-400 font-bold">{progress}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  style={{ width: `${progress}%` }}
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 shadow-md shadow-cyan-500/50 rounded-full transition-all duration-300"
                />
              </div>
            </div>
          )}

          {/* Primary Action Button */}
          {!isUploading && !result && (
            <button
              onClick={uploadFile}
              className="w-full mt-2 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold rounded-xl text-sm transition-all duration-200 shadow-md hover:shadow-cyan-950/40 flex items-center justify-center gap-1.5"
            >
              Analyze Audio Profile
            </button>
          )}
        </div>
      )}

      {/* Forensic Report Display */}
      {result && (
        <div className="mt-6 border-t border-slate-800 pt-6 animate-fadeIn">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Forensic Diagnostic Report</h3>
            <button
              onClick={clearFile}
              className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1 font-semibold"
            >
              Scan Another File
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className={`p-4 rounded-xl border flex flex-col ${
              result.prediction === "FAKE_VOICE" || result.prediction === "FAKE"
                ? "bg-rose-500/10 border-rose-500/20" 
                : "bg-emerald-500/10 border-emerald-500/20"
            }`}>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Acoustic Integrity</span>
              <span className={`text-lg font-black mt-1 flex items-center gap-1.5 ${
                result.prediction === "FAKE_VOICE" || result.prediction === "FAKE" ? "text-rose-400" : "text-emerald-400"
              }`}>
                {result.prediction === "FAKE_VOICE" || result.prediction === "FAKE" ? (
                  <>🚨 MANIPULATED CLONE</>
                ) : (
                  <>✔ SECURE / GENUINE</>
                )}
              </span>
            </div>

            <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-950/30 flex flex-col">
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Analysis Confidence</span>
              <span className="text-lg font-black text-white mt-1">
                {result.confidence ? result.confidence.toFixed(2) : "0.00"}%
              </span>
            </div>
          </div>

          <div className="bg-slate-950/50 border border-slate-800/60 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Processing Latency</span>
              <span className="text-white font-mono font-semibold">{result.processing_time ? result.processing_time.toFixed(3) : "0.000"} s</span>
            </div>
            {result.spectrogram_path && (
              <div className="mt-3">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-2">Acoustic Spec Anomaly Map</span>
                <div className="w-full bg-slate-900 border border-slate-800 rounded-lg p-1.5 overflow-hidden flex justify-center items-center">
                  <img
                    src={`http://localhost:8000/static/${result.spectrogram_path.split("/").pop().split("\\").pop()}`}
                    alt="Acoustic Spectrogram Diagnosis"
                    className="max-h-48 object-contain rounded-md w-full"
                    onError={(e) => {
                      // Fallback visual representation if the file is static and server is serving otherwise
                      e.target.style.display = 'none';
                    }}
                  />
                  {/* Decorative static display if image server is unavailable */}
                  <div className="text-[10px] text-slate-500 font-mono py-8 flex flex-col items-center gap-1.5">
                    <svg className="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>Spectrogram mapping complete and stored at:</span>
                    <span className="text-cyan-400 text-center font-bold px-4 max-w-full break-all">{result.spectrogram_path}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
