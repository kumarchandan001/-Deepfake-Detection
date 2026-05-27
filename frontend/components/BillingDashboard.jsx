import React from 'react';

export default function BillingDashboard() {
  const usageStats = {
    planName: "Professional Forensics",
    price: 199.00,
    monthlyQuota: 5000,
    checksRun: 1842,
    billingCycleEnd: "June 27, 2026"
  };

  const usagePercentage = (usageStats.checksRun / usageStats.monthlyQuota) * 100;

  return (
    <div className="bg-[#111827] border border-gray-800 rounded-lg p-6 text-gray-100">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-bold uppercase text-gray-300">Subscription & Billing</h3>
        <span className="text-xs text-blue-400 font-bold">{usageStats.planName}</span>
      </div>

      <div className="bg-gray-900 border border-gray-800 p-4 rounded-lg mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-gray-400">Monthly Usage Volume</span>
          <span className="text-xs font-bold text-gray-200">
            {usageStats.checksRun} / {usageStats.monthlyQuota} checks
          </span>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full" 
            style={{ width: `${usagePercentage}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-center">
        <div className="bg-gray-900 border border-gray-800 p-3 rounded">
          <p className="text-[10px] text-gray-500 uppercase">Monthly Price</p>
          <p className="text-lg font-bold text-gray-200">${usageStats.price.toFixed(2)}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 p-3 rounded">
          <p className="text-[10px] text-gray-500 uppercase">Billing Cycle Ends</p>
          <p className="text-xs font-bold text-gray-400 mt-1">{usageStats.billingCycleEnd}</p>
        </div>
      </div>

      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs py-2 px-4 rounded transition">
        Manage Subscription in Stripe
      </button>
    </div>
  );
}
