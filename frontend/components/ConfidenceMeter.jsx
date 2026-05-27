import React from "react";

export default function ConfidenceMeter({ percentage = 0, isFake = false, subtitle = "Scanning live stream..." }) {
  // Clamp percentage between 0 and 100
  const cleanPercent = Math.max(0, Math.min(100, Math.round(percentage)));
  
  // Calculate SVG circular parameters
  const radius = 60;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (cleanPercent / 100) * circumference;

  // Determine active colors based on deepfake prediction
  const colorClass = isFake ? "stroke-rose-500" : "stroke-emerald-500";
  const bgRingClass = "stroke-slate-800";
  const glowClass = isFake ? "shadow-rose-950/20" : "shadow-emerald-950/20";
  const textClass = isFake ? "text-rose-400" : "text-emerald-400";

  return (
    <div className={`w-full flex flex-col items-center bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-2xl transition-all duration-300 ${glowClass}`}>
      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-6">Real-Time Risk Gauge</span>
      
      {/* Circular Progress Gauge */}
      <div className="relative w-40 h-40 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background Track Ring */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className={`${bgRingClass} fill-transparent`}
            strokeWidth={strokeWidth}
          />
          {/* Animated Value Ring */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className={`${colorClass} fill-transparent transition-all duration-300 ease-out`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </svg>
        
        {/* Core Value Label */}
        <div className="absolute flex flex-col items-center text-center">
          <span className="text-3xl font-black text-white leading-none">
            {cleanPercent}%
          </span>
          <span className={`text-[10px] font-extrabold uppercase mt-1 tracking-wider ${textClass}`}>
            {isFake ? "MANIPULATED" : "AUTHENTIC"}
          </span>
        </div>
      </div>

      {/* Description Metrics */}
      <div className="mt-6 text-center">
        <p className="text-sm font-semibold text-slate-200">{subtitle}</p>
        <div className="flex gap-2 justify-center items-center mt-3">
          <span className={`w-2 h-2 rounded-full ${isFake ? "bg-rose-500" : "bg-emerald-500"}`}></span>
          <span className="text-xs text-slate-500">
            {isFake 
              ? "Synthesis signatures detected in active frame batch" 
              : "Attribution matches organic recording standards"}
          </span>
        </div>
      </div>
    </div>
  );
}
