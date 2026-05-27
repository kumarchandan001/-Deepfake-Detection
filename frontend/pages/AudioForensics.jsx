import React from "react";
import AudioUpload from "../components/AudioUpload";

export default function AudioForensics() {
  return (
    <div className="w-full min-h-screen bg-slate-950 py-12 px-6">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white shadow-lg shadow-cyan-500/20">
            AF
          </div>
          <div>
            <h1 className="text-xl font-black uppercase tracking-widest text-white leading-none">Voice Forensics Laboratory</h1>
            <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Synthetic voice clone scanning station</p>
          </div>
        </div>
        <AudioUpload />
      </div>
    </div>
  );
}
