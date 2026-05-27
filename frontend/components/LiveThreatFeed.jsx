import React, { useState, useEffect } from "react";

export default function LiveThreatFeed({ onAlertSelect }) {
  const [alerts, setAlerts] = useState([
    {
      id: "TR-1002",
      type: "CLONED_AUDIO",
      source: "TikTok @bot_network_hub",
      severity: "CRITICAL",
      msg: "Audio deepfake spoofing CEO signature detected.",
      timestamp: "23:02:45"
    },
    {
      id: "TR-1001",
      type: "FACE_SPOOF",
      source: "Webcam Entrypoint Node-3",
      severity: "WARNING",
      msg: "Laplacian face check detected spoofing mask pattern.",
      timestamp: "23:01:10"
    },
    {
      id: "TR-1000",
      type: "ADVERSARIAL_EVASION",
      source: "API Client #19482",
      severity: "CRITICAL",
      msg: "2D FFT scan identified high frequency adversarial noise injection.",
      timestamp: "22:58:30"
    }
  ]);

  // Simulate incoming real-time alerts periodically
  useEffect(() => {
    const types = ["CLONED_AUDIO", "FACE_SPOOF", "ADVERSARIAL_EVASION", "PERCEPTUAL_MATCH"];
    const severities = ["CRITICAL", "WARNING", "INFO"];
    const channels = ["Telegram Feed", "Instagram API Hook", "Live Stream RTMP", "Reddit /r/politics"];
    const messages = [
      "Voice model clones signature audio pattern with 94% pitch correlation.",
      "Perceptual Hamming hash indicates exact replicate of media campaign #91A.",
      "Fast Fourier power spectrum detects evasion spike in spatial frequencies.",
      "Face texture variance threshold check failed. Surface depth anomaly.",
    ];

    const interval = setInterval(() => {
      const randomType = types[Math.floor(Math.random() * types.length)];
      const randomSeverity = severities[Math.floor(Math.random() * severities.length)];
      const randomChannel = channels[Math.floor(Math.random() * channels.length)];
      const randomMsg = messages[Math.floor(Math.random() * messages.length)];
      
      const newAlert = {
        id: `TR-${Math.floor(1000 + Math.random() * 9000)}`,
        type: randomType,
        source: randomChannel,
        severity: randomSeverity,
        msg: randomMsg,
        timestamp: new Date().toLocaleTimeString(),
      };

      setAlerts(prev => [newAlert, ...prev.slice(0, 14)]);
      
      if (onAlertSelect) {
        // Option to trigger visual highlight on parent container
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [onAlertSelect]);

  const getSeverityStyle = (severity) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-950/80 border-red-500/50 text-red-400";
      case "WARNING":
        return "bg-amber-950/80 border-amber-500/50 text-amber-400";
      default:
        return "bg-slate-900/60 border-slate-800 text-slate-400";
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/60 pb-3 shrink-0">
        <div>
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Live Cybersecurity Forensics Threat Feed</h3>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Real-time socket network logs & active intrusion events</p>
        </div>
        <div className="flex items-center gap-1.5 bg-slate-950 px-2 py-0.5 border border-slate-850 rounded">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></span>
          <span className="text-[8px] font-mono text-slate-400 font-bold tracking-widest uppercase">STREAMING LIVE</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2.5 max-h-[400px] pr-2 scrollbar-thin">
        {alerts.map((alert) => (
          <div 
            key={alert.id}
            onClick={() => onAlertSelect && onAlertSelect(alert)}
            className={`border rounded-xl p-3.5 transition-all duration-300 cursor-pointer hover:scale-[1.01] hover:bg-slate-950/60 active:scale-100 flex flex-col gap-1.5 animate-slideIn ${getSeverityStyle(alert.severity)}`}
          >
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-mono font-black uppercase tracking-widest bg-slate-950 px-2 py-0.5 border border-slate-800 rounded">
                  {alert.type}
                </span>
                <span className="text-[9px] font-mono text-slate-500 font-bold">{alert.timestamp}</span>
              </div>
              <span className="text-[8px] font-mono font-black tracking-wider uppercase text-slate-400">
                {alert.id}
              </span>
            </div>
            
            <p className="text-xs font-bold text-white tracking-wide">{alert.msg}</p>
            
            <div className="flex justify-between items-center text-[9px] font-mono font-bold uppercase text-slate-500 border-t border-slate-950 pt-2 mt-1">
              <span>Channel: <span className="text-cyan-400">{alert.source}</span></span>
              <span className="hover:text-cyan-400">Mitigate →</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
