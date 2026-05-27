import React from 'react';

export default function ThreatMap() {
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-lg p-6 text-gray-100">
      <h3 className="text-sm font-bold uppercase text-gray-300 mb-4">Geographic Threat Map</h3>
      
      <div className="relative h-60 bg-gray-900 border border-gray-800 rounded-lg overflow-hidden flex items-center justify-center">
        {/* Mock representation of map contours using svg nodes */}
        <svg viewBox="0 0 1000 500" className="w-full h-full opacity-30 fill-gray-600">
          <rect x="100" y="100" width="120" height="80" rx="10" />
          <rect x="350" y="80" width="180" height="120" rx="10" />
          <rect x="250" y="250" width="150" height="100" rx="10" />
          <rect x="600" y="150" width="220" height="150" rx="10" />
        </svg>

        {/* Threat hot-spots overlays */}
        <div className="absolute top-1/4 left-1/4 animate-pulse flex flex-col items-center">
          <div className="h-4 w-4 rounded-full bg-red-500 border-2 border-white" />
          <span className="text-[10px] font-bold text-red-400 bg-black/60 px-1 rounded mt-1">USA (High Risk)</span>
        </div>

        <div className="absolute top-1/3 left-2/3 animate-pulse flex flex-col items-center">
          <div className="h-3 w-3 rounded-full bg-yellow-500 border-2 border-white" />
          <span className="text-[10px] font-bold text-yellow-400 bg-black/60 px-1 rounded mt-1">Germany (Moderate)</span>
        </div>

        <div className="absolute top-2/3 left-1/3 animate-pulse flex flex-col items-center">
          <div className="h-3 w-3 rounded-full bg-red-500 border-2 border-white" />
          <span className="text-[10px] font-bold text-red-400 bg-black/60 px-1 rounded mt-1">Russia (Active Threats)</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4 text-center">
        <div className="bg-gray-900 border border-gray-800 p-2 rounded">
          <p className="text-[10px] text-gray-500 uppercase">Primary Region</p>
          <p className="text-xs font-bold text-blue-400">North America</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-2 rounded">
          <p className="text-[10px] text-gray-500 uppercase">Active Attack Nodes</p>
          <p className="text-xs font-bold text-red-500">63 Sites</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-2 rounded">
          <p className="text-[10px] text-gray-500 uppercase">Target Channels</p>
          <p className="text-xs font-bold text-emerald-400">API Webhooks</p>
        </div>
      </div>
    </div>
  );
}
