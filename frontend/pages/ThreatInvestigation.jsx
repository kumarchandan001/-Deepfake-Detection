import React, { useState } from "react";
import SeverityPanel from "../components/SeverityPanel";

export default function ThreatInvestigation() {
  const [file, setFile] = useState(null);
  const [urlInput, setUrlInput] = useState("");
  const [activeStep, setActiveStep] = useState(null); // 'upload', 'visual', 'adversarial', 'attribution', 'complete'
  const [isProcessing, setIsProcessing] = useState(false);
  const [report, setReport] = useState(null);

  const steps = [
    { id: "upload", label: "Ingestion & Media Parsing", desc: "Checking file formats and verifying spatial parameters." },
    { id: "visual", label: "Laplacian Surface Check", desc: "Extracting texture gradients to audit face liveness depth." },
    { id: "adversarial", label: "Fourier Adversarial Scan", desc: "Calculating 2D Fast Fourier power spectrum artifacts." },
    { id: "attribution", label: "Campaign Attribution Graph", desc: "Matching Hamming hash codes against historical loops databases." }
  ];

  const handleStartInvestigation = (e) => {
    e.preventDefault();
    if (!file && !urlInput.trim()) return;

    setIsProcessing(true);
    setReport(null);
    
    // Animate through active pipelines sequentially
    let currentIdx = 0;
    setActiveStep(steps[currentIdx].id);

    const interval = setInterval(() => {
      currentIdx += 1;
      if (currentIdx < steps.length) {
        setActiveStep(steps[currentIdx].id);
      } else {
        clearInterval(interval);
        setActiveStep("complete");
        setIsProcessing(false);
        setReport({
          case_id: `INV-2026-${Math.floor(1000 + Math.random() * 9000)}`,
          score: 0.912,
          details: [
            { label: "Visual Surface Anomaly (Laplacian)", val: 0.94, desc: "Surface variance matches static display textures." },
            { label: "Acoustic Synthesized Pitch Correlation", val: 0.88, desc: "Voice cloning matching target pitch signatures." },
            { label: "Adversarial Fourier Spike (2D FFT)", val: 0.72, desc: "High frequency grid pattern modifications detected." },
            { label: "Social propagation exposure coefficient", val: 0.91, desc: "Fast-spreading network amplification detected." }
          ]
        });
      }
    }, 1800);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans py-8 px-6">
      <div className="max-w-6xl mx-auto flex flex-col gap-8">
        
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-slate-900 pb-5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-500 to-indigo-600 flex items-center justify-center font-black text-white shadow-lg shadow-red-500/10">
            TI
          </div>
          <div>
            <h1 className="text-xl font-black uppercase tracking-widest text-white leading-none">Autonomous Incident Lab</h1>
            <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Multi-layer deep learning and forensic validation sweeps</p>
          </div>
        </div>

        {/* Input selectors */}
        {!isProcessing && !report && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
            
            {/* File dropzone */}
            <div 
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="border-2 border-dashed border-slate-800 hover:border-cyan-500/40 bg-slate-900/30 p-8 rounded-2xl flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 min-h-[300px]"
            >
              <div className="w-12 h-12 rounded-xl bg-slate-950 border border-slate-850 flex items-center justify-center font-mono text-cyan-400 font-bold text-xs uppercase mb-4">
                Raw
              </div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Drag and drop verification media</h3>
              <p className="text-xs text-slate-500 font-bold mt-1.5 max-w-xs">
                Supports deepfake video (.mp4, .webm), target high-profile images (.jpg, .png), or voice streams (.wav, .mp3).
              </p>
              <input 
                type="file" 
                id="file-selector"
                onChange={(e) => setFile(e.target.files[0])}
                className="hidden" 
              />
              <label 
                htmlFor="file-selector"
                className="mt-5 px-5 py-2.5 rounded-xl border border-slate-800 bg-slate-950 text-xs font-bold font-mono text-cyan-400 hover:border-cyan-500/40 transition-all duration-200"
              >
                [Browse Local Workspace]
              </label>

              {file && (
                <div className="mt-4 bg-slate-950 px-3 py-1.5 border border-slate-850 rounded text-[10px] font-mono text-slate-400 font-bold">
                  Target File: {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                </div>
              )}
            </div>

            {/* URL input */}
            <div className="bg-slate-900/40 border border-slate-850 p-8 rounded-2xl flex flex-col gap-5 min-h-[300px] justify-between">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Fetch feed scraper URL</h3>
                <p className="text-xs text-slate-500 font-bold mt-1.5">
                  Type a social media account post or direct link to pull content asynchronously into our forensic workers queue.
                </p>
              </div>

              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://twitter.com/target_post/status/9482..."
                className="w-full bg-slate-950 text-xs font-mono text-cyan-400 placeholder:text-slate-650 px-4 py-3.5 rounded-xl border border-slate-900 focus:outline-none focus:border-cyan-500/50 transition-all duration-200"
              />

              <button
                onClick={handleStartInvestigation}
                disabled={!file && !urlInput.trim()}
                className="w-full py-3.5 rounded-xl bg-gradient-to-tr from-red-500 to-indigo-600 font-bold text-xs uppercase tracking-wider text-white shadow-lg shadow-red-500/20 active:scale-95 disabled:opacity-50 disabled:pointer-events-none transition-all duration-200"
              >
                Initialize Incident Scan
              </button>
            </div>

          </div>
        )}

        {/* Dynamic scan progress pipeline */}
        {isProcessing && (
          <div className="bg-slate-900/60 border border-slate-850 p-8 rounded-2xl shadow-2xl flex flex-col gap-6 items-center py-12">
            <span className="w-8 h-8 border-3 border-cyan-400 border-t-transparent rounded-full animate-spin"></span>
            <div className="text-center">
              <h2 className="text-sm font-black text-white uppercase tracking-widest">Autonomous Pipeline Active</h2>
              <p className="text-xs text-slate-500 font-bold mt-1 uppercase tracking-wider">Celery distributed scheduler routing raw target tensors</p>
            </div>

            {/* Pipeline progress checkpoints */}
            <div className="w-full max-w-2xl grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              {steps.map((step) => {
                const isActive = activeStep === step.id;
                const isChecked = steps.findIndex(s => s.id === activeStep) > steps.findIndex(s => s.id === step.id);
                
                return (
                  <div 
                    key={step.id} 
                    className={`border p-4 rounded-xl flex flex-col gap-2 transition-all duration-300 ${
                      isActive 
                        ? "border-cyan-500 bg-slate-950" 
                        : isChecked 
                        ? "border-slate-800 bg-slate-900/40 opacity-70"
                        : "border-slate-900 bg-slate-950/20 opacity-30"
                    }`}
                  >
                    <span className={`text-[9px] font-mono font-black uppercase ${isActive ? "text-cyan-400 animate-pulse" : isChecked ? "text-slate-400" : "text-slate-650"}`}>
                      {isActive ? "RUNNING" : isChecked ? "COMPLETED" : "PENDING"}
                    </span>
                    <h4 className="text-xs font-bold text-white uppercase font-mono">{step.label}</h4>
                    <p className="text-[9px] text-slate-500 font-bold leading-relaxed">{step.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Complete Report Dossier view */}
        {report && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start animate-fadeIn">
            
            {/* Severity and Advise metrics column */}
            <div className="lg:col-span-1 flex flex-col gap-6">
              <SeverityPanel score={report.score} details={report.details} />
              
              <button
                onClick={() => { setReport(null); setFile(null); setUrlInput(""); }}
                className="w-full py-3 rounded-xl border border-slate-800 hover:border-slate-700 bg-slate-900/40 text-xs font-bold font-mono text-slate-400 hover:text-white uppercase transition-all duration-200"
              >
                [Run New Investigation]
              </button>
            </div>

            {/* Structured Findings text dossier */}
            <div className="lg:col-span-2 bg-slate-900/60 border border-slate-850 p-6 rounded-2xl shadow-xl flex flex-col gap-5">
              <div className="border-b border-slate-800 pb-3 flex justify-between items-center">
                <div>
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Case Verification Dossier Summary</h3>
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Structured findings compiled by forensic agents</p>
                </div>
                <span className="text-xs font-mono font-bold text-cyan-400">{report.case_id}</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-slate-950 p-4 border border-slate-900 rounded-xl">
                  <h4 className="text-xs font-bold text-white font-mono uppercase">Attribution Status</h4>
                  <p className="text-xs text-slate-400 font-bold mt-1.5 leading-relaxed">
                    Hamming Hash matches image duplicates on 3 accounts tracked under Russian Sybil Client-73 network loop.
                  </p>
                </div>
                <div className="bg-slate-950 p-4 border border-slate-900 rounded-xl">
                  <h4 className="text-xs font-bold text-white font-mono uppercase">Liveness Verification</h4>
                  <p className="text-xs text-slate-400 font-bold mt-1.5 leading-relaxed">
                    Laplacian variance below 0.003 threshold. Face pattern is flat screen recording or print.
                  </p>
                </div>
              </div>

              <div className="bg-slate-950 p-4 border border-slate-900 rounded-xl">
                <h4 className="text-xs font-bold text-white font-mono uppercase">Adversarial Evasion Auditing</h4>
                <p className="text-xs text-slate-400 font-bold mt-1.5 leading-relaxed">
                  2D Fast Fourier Transform Magnitude spectrum plots show power spikes in high spatial frequencies indicating adversarial modifications designed to spoof baseline detectors. Liveness protections successfully filtered the anomalies.
                </p>
              </div>

              <div className="border-t border-slate-950 pt-4 flex justify-between items-center text-[9px] font-mono font-bold uppercase">
                <span className="text-slate-500">Forensics Report generated successfully.</span>
                <span className="text-cyan-400 cursor-pointer hover:underline">Export Full Forensic Brief (PDF)</span>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
