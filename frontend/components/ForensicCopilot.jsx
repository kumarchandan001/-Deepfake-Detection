import React, { useState, useEffect, useRef } from "react";

export default function ForensicCopilot() {
  const [messages, setMessages] = useState([
    {
      role: "system",
      content: "Antigravity Forensic Copilot initialized. Neural pipeline online. Ready to audit deepfakes, inspect adversarial Fourier profiles, and decode threat graph clusters.",
      timestamp: "23:05:01"
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Simulate forensic reasoning response
    setTimeout(() => {
      let botResponse = "";
      const text = input.toLowerCase();

      if (text.includes("fourier") || text.includes("fft") || text.includes("adversarial")) {
        botResponse = "ADVERSARIAL DIAGNOSTICS: 2D Fast Fourier Transform (FFT) analysis maps high frequency grids. Our models scan for radial power spectrum drops. In synthesized faces, there is typically a characteristic power spike in coordinates (350, 480) representing GAN convolutional grid artifacts.";
      } else if (text.includes("graph") || text.includes("campaign") || text.includes("loop")) {
        botResponse = "INTELLIGENCE REPORT: Campaign topological scan identifies a cluster of 5 high-similarity image hash nodes targeting account VIP_021. Perceptual Hamming matching matches local vector databases with 97.4% accuracy, isolating Russian IP range hosting nodes.";
      } else if (text.includes("liveness") || text.includes("spoof") || text.includes("laplacian")) {
        botResponse = "SPOOF MITIGATION: The active liveness scanner runs a 3x3 Laplacian edge extraction kernel. If the pixel intensity variance falls below 0.0035, it flags the image as a printed mask or display re-broadcast. Live webcam stream variance is healthy at 0.0142.";
      } else if (text.includes("voice") || text.includes("audio") || text.includes("pitch")) {
        botResponse = "AUDIO ANALYSIS: Pitch matching checks the first 4 formant frequencies against recorded reference data. The Wav2Vec2 layer indicates vocal segment synthesis with pitch anomaly duration coefficient of 0.88.";
      } else {
        botResponse = "COGNITIVE ORCHESTRATION: The autonomous investigation workflow recommends submitting suspicious assets to /api/v1/investigations/analyze for complete convolutional and Laplacian texture validation. Severity of active campaigns remains elevated at 0.86.";
      }

      const botMessage = {
        role: "copilot",
        content: botResponse,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl flex flex-col h-[500px] overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-800/60 pb-3 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></div>
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Neural Forensic Copilot Terminal</h3>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Autonomous intelligence advisor & campaign diagnostic utility</p>
          </div>
        </div>
        <span className="text-[9px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 border border-slate-850 rounded">
          COGNITION v1.9-O
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 font-mono scrollbar-thin">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex flex-col gap-1.5 p-3.5 rounded-xl border max-w-[85%] ${
              msg.role === "user"
                ? "bg-cyan-950/40 border-cyan-900/50 text-cyan-200 self-end ml-auto"
                : msg.role === "copilot"
                ? "bg-slate-950/90 border-slate-850 text-slate-200 self-start"
                : "bg-slate-950/50 border-slate-900 text-slate-400 text-xs self-start"
            }`}
          >
            <div className="flex justify-between items-center text-[9px] text-slate-500 font-bold uppercase tracking-wide border-b border-slate-900/40 pb-1 mb-1">
              <span>{msg.role}</span>
              <span>{msg.timestamp}</span>
            </div>
            <p className="text-xs leading-relaxed tracking-wide whitespace-pre-wrap">
              {msg.content}
            </p>
          </div>
        ))}
        {isTyping && (
          <div className="bg-slate-950/90 border border-slate-900 text-slate-400 text-xs p-3 rounded-xl max-w-[85%] self-start flex items-center gap-1.5 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "0ms" }}></span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "150ms" }}></span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "300ms" }}></span>
            <span className="text-[10px] text-slate-500 font-bold tracking-widest uppercase">Orchestrating forensic models...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input box */}
      <form onSubmit={handleSend} className="flex gap-2 shrink-0 border-t border-slate-850/80 pt-3">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Copilot (e.g., Explain 2D FFT adversarial patterns / Show campaign tracking loops)..."
          className="flex-1 bg-slate-950 text-xs font-mono text-cyan-400 placeholder:text-slate-650 px-4 py-3 rounded-xl border border-slate-900 focus:outline-none focus:border-cyan-500/50 transition-all duration-200"
        />
        <button 
          type="submit"
          disabled={!input.trim() || isTyping}
          className="px-5 py-3 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 font-bold text-xs uppercase tracking-wider text-white shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50 disabled:pointer-events-none transition-all duration-200"
        >
          Send
        </button>
      </form>
    </div>
  );
}
