import React, { useState } from 'react';

export default function LiveModerationCenter() {
  const [feed, setFeed] = useState([
    { id: 1, filename: "stream_frame_1042.jpg", status: "REAL", confidence: 98.4, timestamp: "23:40:01" },
    { id: 2, filename: "stream_frame_1043.jpg", status: "REAL", confidence: 97.9, timestamp: "23:40:02" },
    { id: 3, filename: "stream_frame_1044.jpg", status: "FAKE", confidence: 94.1, timestamp: "23:40:03" }
  ]);

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-lg p-6 text-gray-100">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-bold uppercase text-gray-300">Live WebRTC Moderation Stream</h3>
        <span className="bg-red-500/20 text-red-500 border border-red-500 text-xs px-2 py-0.5 rounded font-bold animate-pulse">
          MONITORING ACTIVE
        </span>
      </div>

      <div className="space-y-3 max-h-60 overflow-y-auto mb-4">
        {feed.map((frame) => (
          <div 
            key={frame.id} 
            className={`p-3 rounded border flex justify-between items-center ${
              frame.status === "REAL" 
                ? "bg-emerald-500/10 border-emerald-500/30" 
                : "bg-red-500/10 border-red-500/30"
            }`}
          >
            <div>
              <p className="text-xs font-semibold text-gray-200">{frame.filename}</p>
              <p className="text-[10px] text-gray-500">Captured at: {frame.timestamp}</p>
            </div>
            <div className="text-right">
              <span className={`text-xs font-bold ${frame.status === "REAL" ? "text-emerald-400" : "text-red-400"}`}>
                {frame.status}
              </span>
              <p className="text-[10px] text-gray-400">Confidence: {frame.confidence}%</p>
            </div>
          </div>
        ))}
      </div>

      <button className="w-full bg-[#1F2937] hover:bg-gray-800 border border-gray-700 text-gray-300 font-bold text-xs py-2 px-4 rounded transition">
        Pause WebRTC Feed
      </button>
    </div>
  );
}
