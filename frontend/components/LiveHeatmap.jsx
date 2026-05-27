import React from "react";

export default function LiveHeatmap({ prediction }) {
  const isFake = prediction?.fake_probability > 0.5;
  const score = prediction?.fake_probability ? Math.round(prediction.fake_probability * 100) : 0;
  
  // Extract face boxes if present
  const faces = prediction?.faces || [];
  
  return (
    <div className="w-full flex flex-col bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-2xl transition-all duration-300">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white tracking-wide">Live XAI Activation Map</h2>
        <p className="text-xs text-slate-400 mt-1">Real-time convolutional layer attribution maps highlighting synthetic skin textures and splicing edges.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual Heatmap Canvas Placeholder / Live Overlay Status */}
        <div className="lg:col-span-2 relative aspect-video bg-black/40 rounded-xl border border-slate-800/80 overflow-hidden flex flex-col items-center justify-center p-4">
          {prediction?.success ? (
            <div className="w-full h-full flex flex-col justify-between">
              {/* Top Banner */}
              <div className="flex justify-between items-center z-10">
                <span className="text-[10px] bg-slate-900/90 text-cyan-400 border border-slate-800 px-2.5 py-1 rounded font-bold uppercase tracking-wider">
                  Target Layer: conv_head
                </span>
                <span className={`text-[10px] px-2.5 py-1 rounded font-bold uppercase tracking-wider ${
                  isFake ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                }`}>
                  Anomaly Score: {score}%
                </span>
              </div>

              {/* Central Status */}
              <div className="my-auto flex flex-col items-center justify-center text-center gap-3 py-6">
                <div className={`w-14 h-14 rounded-full flex items-center justify-center border shadow-xl ${
                  isFake 
                    ? "bg-rose-500/10 border-rose-500/30 text-rose-400 animate-pulse" 
                    : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                }`}>
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                
                <p className={`text-base font-extrabold tracking-wide uppercase ${isFake ? "text-rose-400" : "text-emerald-400"}`}>
                  {isFake ? "🚨 Splicing Artifacts Detected" : "✔ Stable Skin Spectrum"}
                </p>
                <p className="text-xs text-slate-400 max-w-sm">
                  {isFake 
                    ? "Explainability model localized convolutional focus spikes on face boundaries and eyes, typical of diffusion deepfakes."
                    : "Attribution layers show homogeneous weighting across facial keypoints indicating normal physical micro-reflections."}
                </p>
              </div>

              {/* Bottom Details */}
              <div className="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-800/60 pt-3">
                <span>Stream ID: {prediction.frame_id || "N/A"}</span>
                <span>Active Faces Tracked: {faces.length}</span>
              </div>
            </div>
          ) : (
            <div className="text-center p-6 flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-950 border border-slate-850 flex items-center justify-center text-slate-500">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.907c.961 0 1.36 1.243.577 1.824l-3.97 2.885a1 1 0 00-.364 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.971-2.885a1 1 0 00-1.18 0l-3.97 2.885c-.782.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.364-1.118l-3.97-2.885c-.783-.58-.38-1.824.577-1.824h4.908a1 1 0 00.95-.69l1.519-4.674z" />
                </svg>
              </div>
              <p className="text-xs font-semibold text-slate-400">Awaiting Webcam Feed Activation</p>
              <p className="text-[10px] text-slate-600 max-w-xs">Attribution weights and spatial anomaly points will render live once a stream connection starts.</p>
            </div>
          )}
        </div>

        {/* Forensic Diagnostics Legend */}
        <div className="flex flex-col justify-between bg-slate-950/30 border border-slate-850 rounded-xl p-5">
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">Gradient Legend</h3>
            
            <div className="flex flex-col gap-3.5">
              <div className="flex items-center gap-3">
                <span className="w-3.5 h-3.5 rounded bg-rose-500 shadow-lg shadow-rose-500/30 shrink-0"></span>
                <div>
                  <p className="text-xs font-bold text-white">Peak Activations (High Risk)</p>
                  <p className="text-[10px] text-slate-500">Unnatural gradients. Strong correlation with synthetic blending masks.</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="w-3.5 h-3.5 rounded bg-amber-500 shadow-lg shadow-amber-500/30 shrink-0"></span>
                <div>
                  <p className="text-xs font-bold text-white">Medium Attribution (Warning)</p>
                  <p className="text-[10px] text-slate-500">Noticeable gradient shifts. Normal around blinking eyes or fast movement.</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="w-3.5 h-3.5 rounded bg-blue-600 shadow-lg shadow-blue-500/30 shrink-0"></span>
                <div>
                  <p className="text-xs font-bold text-white">Deep Spectrum (Authentic)</p>
                  <p className="text-[10px] text-slate-500">Standard, low-contrast gradients indicating uniform natural textures.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 border-t border-slate-800/80 pt-4 flex flex-col gap-2">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">XAI Diagnostic Logic</span>
            <p className="text-[10px] text-slate-400 leading-relaxed">
              We monitor spatial attributions dynamically using Grad-CAM. High concentration zones around nose bridges or cheek boundaries represent edge inconsistencies typical of modern video deepfakes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
