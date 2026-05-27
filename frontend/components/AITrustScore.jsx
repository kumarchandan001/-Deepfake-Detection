import React from 'react';

export default function AITrustScore({ score = 96.5 }) {
  return (
    <div className="bg-[#111827] border border-gray-800 rounded-lg p-6 text-gray-100 flex flex-col items-center">
      <h3 className="text-xs uppercase text-gray-400 font-bold mb-4">Overall AI Trust Score</h3>
      
      <div className="relative flex items-center justify-center h-28 w-28 mb-4">
        {/* Large Dial */}
        <div className="absolute h-24 w-24 rounded-full border-8 border-gray-800" />
        <div className="absolute h-24 w-24 rounded-full border-8 border-blue-500 border-b-transparent animate-spin-slow" />
        <span className="text-2xl font-bold text-blue-400">{score}%</span>
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold text-emerald-400">HIGH FIDELITY MEDIA ENVIRONMENT</p>
        <p className="text-[10px] text-gray-500 mt-1">Calculated across verified imagery, waveforms, and video metadata hashes.</p>
      </div>
    </div>
  );
}
