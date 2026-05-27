import React, { useState } from "react";

export default function InvestigationTimeline({ investigations = [] }) {
  const [expandedId, setExpandedId] = useState(null);

  const defaultInvestigations = [
    {
      id: "INV-2026-9041",
      case_name: "CEO Press Mockery Campaign",
      timestamp: "2026-05-27T22:15:30Z",
      status: "COMPLETED",
      severity: 0.94,
      steps: [
        { name: "Raw Ingestion & Type Auditing", status: "completed", msg: "Identified dual channels: MPEG stream & stereo audio track." },
        { name: "Laplacian Face Liveness Pass", status: "completed", msg: "Texture score variance 0.0028 indicating low surface depth." },
        { name: "2D FFT Adversarial Perturbation Check", status: "completed", msg: "No high-frequency power spikes detected. Clean fake." },
        { name: "Acoustic Vocal Correlation scan", status: "completed", msg: "Voice clone matching probability 92.4%." },
        { name: "Topological Attributive Campaign Mapping", status: "completed", msg: "Isolated Sybil client A1 node link propagation." }
      ],
      media_count: 2,
      platform: "Twitter/X",
    },
    {
      id: "INV-2026-8812",
      case_name: "Stock Market Manipulative Deepfake",
      timestamp: "2026-05-27T18:40:11Z",
      status: "COMPLETED",
      severity: 0.82,
      steps: [
        { name: "Raw Ingestion & Type Auditing", status: "completed", msg: "Target: MP4 snippet (45s)." },
        { name: "Laplacian Face Liveness Pass", status: "completed", msg: "Liveness verification failed. Face is static mask." },
        { name: "2D FFT Adversarial Perturbation Check", status: "completed", msg: "Spike detected in upper spectrums. Evasion pattern confirmed." }
      ],
      media_count: 1,
      platform: "Reddit /r/finance",
    },
    {
      id: "INV-2026-7539",
      case_name: "VIP Video Call Extortion",
      timestamp: "2026-05-27T11:05:00Z",
      status: "COMPLETED",
      severity: 0.58,
      steps: [
        { name: "Raw Ingestion & Type Auditing", status: "completed", msg: "Target: Webm screen recording." },
        { name: "Laplacian Face Liveness Pass", status: "completed", msg: "Normal depth variations registered. Possible cheapfake." }
      ],
      media_count: 1,
      platform: "Direct Upload (E-Crime Incident)",
    }
  ];

  const activeInvestigations = investigations.length > 0 ? investigations : defaultInvestigations;

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl flex flex-col h-full">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/60 pb-3">
        <div>
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Forensic Investigation Timelines</h3>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Chronological execution stream & diagnostic sweeps</p>
        </div>
        <span className="text-[10px] bg-slate-950 px-2 py-0.5 border border-slate-800 rounded font-mono text-cyan-400 font-bold">
          {activeInvestigations.length} ACTIVE CASES
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 max-h-[500px] pr-2">
        {activeInvestigations.map((inv) => {
          const isExpanded = expandedId === inv.id;
          const isCritical = inv.severity >= 0.8;

          return (
            <div 
              key={inv.id}
              className={`border rounded-xl transition-all duration-300 ${
                isExpanded ? "border-slate-755 bg-slate-950/60" : "border-slate-850/80 hover:border-slate-800 bg-slate-900/30"
              }`}
            >
              {/* Header Summary */}
              <div 
                onClick={() => setExpandedId(isExpanded ? null : inv.id)}
                className="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 cursor-pointer select-none"
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono text-xs font-black uppercase shrink-0 ${
                    isCritical ? "bg-red-950/80 text-red-400 border border-red-500/35" : "bg-slate-950 text-cyan-400 border border-cyan-500/20"
                  }`}>
                    {inv.id.substring(4, 8)}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-snug">{inv.case_name}</h4>
                    <div className="flex flex-wrap gap-x-2 gap-y-0.5 mt-0.5 text-[9px] font-mono font-bold uppercase text-slate-500">
                      <span>{inv.id}</span>
                      <span>•</span>
                      <span>{new Date(inv.timestamp).toLocaleString()}</span>
                      <span>•</span>
                      <span className="text-cyan-400">{inv.platform}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
                  <div className="flex flex-col items-end">
                    <span className="text-[8px] text-slate-500 font-bold uppercase">Risk Score</span>
                    <span className={`text-xs font-mono font-black ${isCritical ? "text-red-400" : "text-amber-400"}`}>
                      {(inv.severity * 100).toFixed(1)}%
                    </span>
                  </div>
                  <span className="text-xs text-slate-500 font-mono transition-transform duration-300">
                    {isExpanded ? "[-]" : "[+]"}
                  </span>
                </div>
              </div>

              {/* Steps Timeline Expansion */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-slate-950 pt-4 bg-slate-950/30 rounded-b-xl animate-fadeIn">
                  <div className="relative pl-6 border-l border-slate-800 space-y-5">
                    {inv.steps.map((step, idx) => (
                      <div key={idx} className="relative">
                        {/* Bullet tracker */}
                        <div className="absolute -left-[31px] top-1 w-2.5 h-2.5 rounded-full border bg-slate-950 border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-400/20">
                          <div className="w-1 h-1 rounded-full bg-cyan-400" />
                        </div>
                        
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-slate-300 font-mono">{step.name}</span>
                          <span className="text-[10px] text-slate-500 mt-0.5 leading-relaxed font-bold">{step.msg}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-850 flex justify-between items-center text-[9px] font-mono font-bold uppercase">
                    <span className="text-slate-500">Node Cluster attributions</span>
                    <span className="text-cyan-400 cursor-pointer hover:underline">Download Forensic Dossier (JSON)</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
