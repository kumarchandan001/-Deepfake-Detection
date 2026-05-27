import React from 'react';

export default function SOCDashboard() {
  return (
    <div className="p-6 bg-[#0B0F19] text-gray-100 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-blue-400">Security Operations Center (SOC)</h1>
          <p className="text-xs text-gray-400">Real-time enterprise media threat surveillance grid</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold text-emerald-400">LIVE FEED OPERATIONAL</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-[#111827] border border-gray-800 p-4 rounded-lg">
          <p className="text-xs text-gray-400 uppercase">Verification Volume (1h)</p>
          <p className="text-2xl font-bold text-gray-100">8,412</p>
        </div>
        <div className="bg-[#111827] border border-gray-800 p-4 rounded-lg">
          <p className="text-xs text-gray-400 uppercase">Deepfakes Identified</p>
          <p className="text-2xl font-bold text-red-500">327</p>
        </div>
        <div className="bg-[#111827] border border-gray-800 p-4 rounded-lg">
          <p className="text-xs text-gray-400 uppercase">Policy Violations Blocked</p>
          <p className="text-2xl font-bold text-yellow-500">14</p>
        </div>
        <div className="bg-[#111827] border border-gray-800 p-4 rounded-lg">
          <p className="text-xs text-gray-400 uppercase">Avg Response Latency</p>
          <p className="text-2xl font-bold text-blue-400">120 ms</p>
        </div>
      </div>

      <div className="bg-[#111827] border border-gray-800 rounded-lg p-6">
        <h3 className="text-sm font-bold uppercase text-gray-300 mb-4">Critical Threat Incidents Log</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-400">
            <thead className="text-gray-300 uppercase bg-[#1F2937] border-b border-gray-800">
              <tr>
                <th className="py-2 px-4">Timestamp</th>
                <th className="py-2 px-4">Event Description</th>
                <th className="py-2 px-4">Verdict</th>
                <th className="py-2 px-4">Risk Node</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              <tr className="hover:bg-gray-900">
                <td className="py-3 px-4">2026-05-27 23:10:12</td>
                <td className="py-3 px-4">Synthetic audio trace detected on account registration upload</td>
                <td className="py-3 px-4 text-red-500 font-bold">FAKE</td>
                <td className="py-3 px-4">CLONED_VOICE (ElevenLabsV2)</td>
              </tr>
              <tr className="hover:bg-gray-900">
                <td className="py-3 px-4">2026-05-27 23:08:45</td>
                <td className="py-3 px-4">Adversarial perturbation detected on profile image verification request</td>
                <td className="py-3 px-4 text-yellow-500 font-bold">PERTURBED</td>
                <td className="py-3 px-4">FGSM_ATTACK (Epsilon=0.05)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
