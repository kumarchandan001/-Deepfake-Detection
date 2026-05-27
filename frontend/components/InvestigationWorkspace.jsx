import React, { useState } from 'react';

export default function InvestigationWorkspace() {
  const [activeCase, setActiveCase] = useState({
    id: "case_09e3a8db",
    title: "Executive Audio Phishing Attempt",
    status: "UNDER_REVIEW",
    analyst: "Investigator Alpha",
    evidence: [
      { name: "voice_recording_clip.wav", sha: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", status: "VERIFIED_FAKE" }
    ],
    timeline: [
      { time: "23:10:00", event: "File Acquisition from incident response team" },
      { time: "23:12:15", event: "Acoustic spectrogram extraction completed" },
      { time: "23:13:00", event: "CNN+LSTM model model execution completed" }
    ]
  });

  return (
    <div className="p-6 bg-[#0B0F19] text-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold text-blue-400 mb-6">Forensic Investigation Workspace</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#111827] border border-gray-800 rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-gray-200">{activeCase.title}</h2>
            <span className="bg-yellow-500/20 text-yellow-500 border border-yellow-500 text-xs px-2 py-0.5 rounded font-bold">
              {activeCase.status}
            </span>
          </div>
          
          <div className="mb-6">
            <h3 className="text-xs uppercase text-gray-400 font-bold mb-2">Registered Case Evidence</h3>
            {activeCase.evidence.map((ev, idx) => (
              <div key={idx} className="bg-gray-900 border border-gray-800 p-3 rounded flex justify-between items-center">
                <div>
                  <p className="text-sm font-semibold">{ev.name}</p>
                  <p className="text-xxs text-gray-500 font-mono">{ev.sha}</p>
                </div>
                <span className="text-xs font-bold text-red-500 bg-red-500/20 border border-red-500 px-2 py-0.5 rounded">
                  {ev.status}
                </span>
              </div>
            ))}
          </div>

          <div>
            <h3 className="text-xs uppercase text-gray-400 font-bold mb-3">Chain of Custody Timeline</h3>
            <div className="border-l border-gray-800 pl-4 space-y-4">
              {activeCase.timeline.map((item, idx) => (
                <div key={idx} className="relative">
                  <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-blue-500" />
                  <p className="text-xs text-gray-300 font-semibold">{item.event}</p>
                  <p className="text-xxs text-gray-500">{item.time}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-[#111827] border border-gray-800 rounded-lg p-6">
          <h3 className="text-sm font-bold text-gray-200 mb-4">Analyst Actions Panel</h3>
          <div className="space-y-3">
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2 px-4 rounded transition">
              Upload New Evidence File
            </button>
            <button className="w-full bg-[#1F2937] hover:bg-gray-800 border border-gray-700 text-gray-300 font-bold text-xs py-2 px-4 rounded transition">
              Generate PDF Forensic Report
            </button>
            <button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2 px-4 rounded transition">
              Resolve & Close Investigation
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
