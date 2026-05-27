import React from 'react';

export default function GovernancePanel() {
  const complianceScore = 85;

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-lg p-6 text-gray-100">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-sm font-bold uppercase text-gray-300">AI Governance & Compliance</h3>
        <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500 px-2 py-0.5 rounded font-bold">
          COMPLIANT
        </span>
      </div>

      <div className="flex items-center space-x-6 mb-6">
        <div className="relative flex items-center justify-center h-24 w-24">
          {/* Circular progress bar */}
          <div className="absolute h-20 w-20 rounded-full border-4 border-gray-800" />
          <div className="absolute h-20 w-20 rounded-full border-4 border-emerald-500 border-t-transparent animate-spin-slow" />
          <span className="text-lg font-bold text-gray-100">{complianceScore}%</span>
        </div>
        <div className="flex-1">
          <p className="text-xs text-gray-400 uppercase">Compliance Target Benchmark</p>
          <h4 className="text-md font-bold text-gray-200">EU AI Act Compliance</h4>
          <p className="text-xs text-gray-500 mt-1">High-Risk Biometric Forensic System Requirements adhered.</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="bg-gray-900 border border-gray-800 p-3 rounded flex justify-between items-center">
          <span className="text-xs text-gray-300">GDPR Recital 71 (Right to Explanation)</span>
          <span className="text-xs font-bold text-emerald-400">PASSED</span>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-3 rounded flex justify-between items-center">
          <span className="text-xs text-gray-300">EU AI Act Article 12 (Traceability Logging)</span>
          <span className="text-xs font-bold text-emerald-400">PASSED</span>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-3 rounded flex justify-between items-center">
          <span className="text-xs text-gray-300">Model Output Drift Index</span>
          <span className="text-xs font-bold text-yellow-500">0.03 (STABLE)</span>
        </div>
      </div>
    </div>
  );
}
