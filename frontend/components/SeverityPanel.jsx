import React from "react";

export default function SeverityPanel({ score = 0.86, details }) {
  const defaultDetails = [
    { label: "Visual Surface Anomaly (Laplacian)", val: 0.94, desc: "Surface variance matches static display textures." },
    { label: "Acoustic Synthesized Pitch Correlation", val: 0.88, desc: "Voice cloning matching target pitch signatures." },
    { label: "Adversarial Fourier Spike (2D FFT)", val: 0.72, desc: "High frequency grid pattern modifications detected." },
    { label: "Social propagation exposure coefficient", val: 0.91, desc: "Fast-spreading network amplification detected." }
  ];

  const activeDetails = details || defaultDetails;
  const percentage = (score * 100).toFixed(0);

  const getGaugeColor = (val) => {
    if (val >= 0.8) return { text: "text-red-400", bg: "bg-red-500", border: "border-red-500/35", fill: "#ef4444" };
    if (val >= 0.5) return { text: "text-amber-400", bg: "bg-amber-500", border: "border-amber-500/35", fill: "#f59e0b" };
    return { text: "text-emerald-400", bg: "bg-emerald-500", border: "border-emerald-500/35", fill: "#10b981" };
  };

  const theme = getGaugeColor(score);

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl flex flex-col justify-between h-full relative overflow-hidden">
      {/* Dynamic Cyber light effect in background */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-red-600/10 to-transparent rounded-full blur-xl pointer-events-none" />

      <div className="border-b border-slate-800/60 pb-3 mb-5 shrink-0">
        <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Composite Cyber Threat Severity</h3>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Unified risk assessment & forensic breakdown panels</p>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6 mb-5">
        {/* Animated Visual Gauge */}
        <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
          <svg className="absolute inset-0 w-full h-full transform -rotate-90">
            <circle 
              cx="64" 
              cy="64" 
              r="52" 
              stroke="#0f172a" 
              strokeWidth="8" 
              fill="transparent" 
            />
            <circle 
              cx="64" 
              cy="64" 
              r="52" 
              stroke={theme.fill} 
              strokeWidth="8" 
              fill="transparent" 
              strokeDasharray={2 * Math.PI * 52}
              strokeDashoffset={2 * Math.PI * 52 * (1 - score)}
              className="transition-all duration-1000 ease-out"
              strokeLinecap="round"
            />
          </svg>
          <div className="flex flex-col items-center">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Threat</span>
            <span className={`text-3xl font-black font-mono tracking-tighter ${theme.text}`}>
              {percentage}%
            </span>
            <span className="text-[8px] text-slate-400 font-bold uppercase font-mono tracking-widest mt-0.5">CRITICAL</span>
          </div>
        </div>

        {/* Severity descriptive text */}
        <div className="flex-1">
          <h4 className="text-xs font-black uppercase tracking-wider text-white">Forensic Risk Advisory</h4>
          <p className="text-xs text-slate-400 leading-relaxed font-bold mt-1.5">
            The analyzed media matches established synthetic signatures and propagation networks. System recommends immediate verification hold on target account feed.
          </p>
          <div className="mt-3 flex gap-2">
            <span className="text-[9px] bg-red-950/80 text-red-400 border border-red-500/20 px-2 py-0.5 rounded font-mono font-bold uppercase">
              HIGH RISK TARGET
            </span>
            <span className="text-[9px] bg-slate-950 text-cyan-400 border border-slate-850 px-2 py-0.5 rounded font-mono font-bold uppercase">
              MITIGATION ACTIVE
            </span>
          </div>
        </div>
      </div>

      {/* Breakdown metrics list */}
      <div className="space-y-3.5 border-t border-slate-950 pt-4 flex-1">
        {activeDetails.map((item, idx) => {
          const itemTheme = getGaugeColor(item.val);
          return (
            <div key={idx} className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center text-[10px] font-mono font-bold">
                <span className="text-slate-400 uppercase tracking-wide truncate max-w-[75%]">{item.label}</span>
                <span className={itemTheme.text}>{(item.val * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-900">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${itemTheme.bg}`}
                  style={{ width: `${item.val * 100}%` }}
                />
              </div>
              <span className="text-[8px] text-slate-650 font-bold font-mono tracking-wide uppercase mt-0.5">
                {item.desc}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
