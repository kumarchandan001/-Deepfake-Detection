import React, { useState, useEffect } from 'react';
import LiveDetection from '../pages/LiveDetection';
import MultimodalAnalysis from '../pages/MultimodalAnalysis';
import IntelligenceCenter from '../pages/IntelligenceCenter';

// Custom lightweight inline icons for high visual fidelity
const Icons = {
  Live: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ),
  Multimodal: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 100-6 3 3 0 000 6z" />
    </svg>
  ),
  Intelligence: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  ),
  Billing: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
  ),
  Status: () => (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  )
};

export default function App() {
  const [activePage, setActivePage] = useState('live');
  const [tenantId, setTenantId] = useState('test_ent_client');
  const [currentPlan, setCurrentPlan] = useState('pro');
  const [usageStats, setUsageStats] = useState({
    dailyChecks: 12,
    dailyLimit: 200,
    monthlyChecks: 184,
    monthlyLimit: 5000,
  });
  const [invoices, setInvoices] = useState([
    { id: 'inv_mock_98213', date: 'May 28, 2026', amount: '$199.00', status: 'PAID' }
  ]);
  const [isUpdating, setIsUpdating] = useState(false);

  // Sync subscription status with the actual API gateway in the background
  useEffect(() => {
    async function syncSubscription() {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/saas/subscription/status?tenant_id=${tenantId}`);
        if (response.ok) {
          const data = await response.json();
          setCurrentPlan(data.plan_key);
        }
      } catch (err) {
        console.warn("Backend server not responding, operating in simulator fallback mode.");
      }
    }
    syncSubscription();
  }, [tenantId]);

  // Handle Dynamic Plan Upgrades
  const handleUpgradePlan = async (planKey) => {
    setIsUpdating(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/saas/tenant/onboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          name: 'Global Operations Group',
          email: 'admin@globalops.com',
          plan_key: planKey
        })
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(planKey);
        
        // Dynamic stats limits updates based on config
        const limitMap = {
          free: { daily: 10, monthly: 300 },
          pro: { daily: 200, monthly: 5000 },
          enterprise: { daily: 1000000, monthly: 10000000 }
        };
        
        setUsageStats(prev => ({
          ...prev,
          dailyLimit: limitMap[planKey].daily,
          monthlyLimit: limitMap[planKey].monthly
        }));
        
        // Add new simulated invoice
        const priceMap = { free: '$0.00', pro: '$199.00', enterprise: '$1,500.00' };
        setInvoices(prev => [
          { 
            id: `inv_mock_${Math.floor(Math.random()*90000)+10000}`, 
            date: 'May 28, 2026', 
            amount: priceMap[planKey], 
            status: 'PAID' 
          },
          ...prev
        ]);
      }
    } catch (err) {
      alert("Failed to communicate with local API gateway to perform plan upgrade.");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#020617] text-slate-100 font-sans overflow-hidden">
      
      {/* ─── Premium Navigation Sidebar ─── */}
      <aside className="w-64 bg-[#090d1f] border-r border-slate-900 flex flex-col shrink-0">
        
        {/* Brand/Header */}
        <div className="h-16 border-b border-slate-900 flex items-center px-6 gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-black text-white shadow-lg shadow-cyan-500/20">
            AG
          </div>
          <div>
            <h1 className="text-xs font-black uppercase tracking-widest text-white leading-none">Antigravity Forensics</h1>
            <p className="text-[9px] text-slate-500 font-bold uppercase mt-0.5 tracking-wider">Cybersecurity & Trust</p>
          </div>
        </div>

        {/* Dynamic Tenant Profile Selector */}
        <div className="p-4 border-b border-slate-900 bg-slate-950/40 shrink-0">
          <label className="text-[9px] text-slate-500 font-bold uppercase tracking-wider block mb-1">Active Tenant Workspace</label>
          <div className="flex items-center gap-2">
            <input 
              type="text" 
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              className="w-full bg-slate-950 text-cyan-400 font-mono text-xs px-2.5 py-1.5 rounded border border-slate-900 focus:outline-none focus:border-cyan-500/40"
            />
          </div>
        </div>

        {/* Sidebar Nav Buttons */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          <button
            onClick={() => setActivePage('live')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 ${
              activePage === 'live' 
                ? 'bg-gradient-to-r from-cyan-500/10 to-indigo-600/10 border border-cyan-500/20 text-cyan-400' 
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Icons.Live />
            Live Video Lab
          </button>

          <button
            onClick={() => setActivePage('multimodal')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 ${
              activePage === 'multimodal' 
                ? 'bg-gradient-to-r from-cyan-500/10 to-indigo-600/10 border border-cyan-500/20 text-cyan-400' 
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Icons.Multimodal />
            Multimodal Scan
          </button>

          <button
            onClick={() => setActivePage('intelligence')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 ${
              activePage === 'intelligence' 
                ? 'bg-gradient-to-r from-cyan-500/10 to-indigo-600/10 border border-cyan-500/20 text-cyan-400' 
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Icons.Intelligence />
            Threat Intel
          </button>

          <button
            onClick={() => setActivePage('billing')}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 ${
              activePage === 'billing' 
                ? 'bg-gradient-to-r from-cyan-500/10 to-indigo-600/10 border border-cyan-500/20 text-cyan-400' 
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30'
            }`}
          >
            <Icons.Billing />
            SaaS Billing & Plan
          </button>
        </nav>

        {/* active Plan footer indicator */}
        <div className="p-4 border-t border-slate-900 bg-[#060814] text-center shrink-0">
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-950/40 border border-cyan-900/40">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-[10px] font-black uppercase tracking-widest text-cyan-400 font-mono">
              Tier: {currentPlan}
            </span>
          </div>
        </div>

      </aside>

      {/* ─── Main Content Canvas ─── */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/10 via-[#020617] to-[#020617] pointer-events-none -z-10" />
        
        {/* Dynamic Page Router */}
        <div className="flex-1 overflow-y-auto">
          
          {activePage === 'live' && <LiveDetection />}
          {activePage === 'multimodal' && <MultimodalAnalysis />}
          {activePage === 'intelligence' && <IntelligenceCenter />}

          {/* ─── Integrated SaaS Subscription Dashboard ─── */}
          {activePage === 'billing' && (
            <div className="py-12 px-6 max-w-5xl mx-auto flex flex-col gap-8 animate-fadeIn">
              
              {/* Header */}
              <div className="flex justify-between items-center border-b border-slate-900 pb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center font-black text-white shadow-lg shadow-cyan-500/10">
                    <Icons.Billing />
                  </div>
                  <div>
                    <h1 className="text-xl font-black uppercase tracking-widest text-white leading-none">Subscription & Billing Engine</h1>
                    <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Dynamic Stripe mappings and usage enforcement logs</p>
                  </div>
                </div>
              </div>

              {/* Grid: Plan pricing & stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Free Plan */}
                <div className={`bg-slate-900/60 border rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 ${
                  currentPlan === 'free' ? 'border-cyan-500 shadow-lg shadow-cyan-500/10' : 'border-slate-850 hover:border-slate-800'
                }`}>
                  <h3 className="text-sm font-black uppercase text-white tracking-widest">Developer Free</h3>
                  <div className="flex items-baseline gap-1 mt-2">
                    <span className="text-2xl font-black">$0</span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">/ Month</span>
                  </div>
                  <ul className="text-xs text-slate-400 space-y-2.5 mt-2 flex-1">
                    <li className="flex items-center gap-2 font-bold">✔ Image Deepfake Checks</li>
                    <li className="flex items-center gap-2 font-bold">✔ Basic Forensics Audit</li>
                    <li className="text-slate-650 flex items-center gap-2 font-bold">❌ Video Detection</li>
                    <li className="text-slate-650 flex items-center gap-2 font-bold">❌ Audio/Voice Scanning</li>
                  </ul>
                  <button
                    disabled={currentPlan === 'free' || isUpdating}
                    onClick={() => handleUpgradePlan('free')}
                    className="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 border border-slate-800 hover:bg-slate-950 bg-slate-900/50 disabled:opacity-40"
                  >
                    {currentPlan === 'free' ? 'Active Plan' : 'Downgrade'}
                  </button>
                </div>

                {/* Pro Plan */}
                <div className={`bg-slate-900/60 border rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 ${
                  currentPlan === 'pro' ? 'border-cyan-500 shadow-lg shadow-cyan-500/10' : 'border-slate-850 hover:border-slate-800'
                }`}>
                  <div className="absolute top-0 right-0 bg-cyan-500 text-[#020617] text-[8px] font-black uppercase tracking-widest px-3 py-1 rounded-bl-lg">
                    RECOMMENDED
                  </div>
                  <h3 className="text-sm font-black uppercase text-white tracking-widest">Professional</h3>
                  <div className="flex items-baseline gap-1 mt-2">
                    <span className="text-2xl font-black">$199</span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">/ Month</span>
                  </div>
                  <ul className="text-xs text-slate-400 space-y-2.5 mt-2 flex-1">
                    <li className="flex items-center gap-2 font-bold">✔ Image, Video, & Audio scanning</li>
                    <li className="flex items-center gap-2 font-bold">✔ 5,000 monthly checks limit</li>
                    <li className="flex items-center gap-2 font-bold">✔ Fractional GPU compute allocation</li>
                    <li className="flex items-center gap-2 font-bold">✔ Live slack webhooks & alerts</li>
                  </ul>
                  <button
                    disabled={currentPlan === 'pro' || isUpdating}
                    onClick={() => handleUpgradePlan('pro')}
                    className="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 bg-gradient-to-tr from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white shadow-md disabled:opacity-40"
                  >
                    {currentPlan === 'pro' ? 'Active Plan' : 'Select Pro'}
                  </button>
                </div>

                {/* Enterprise Plan */}
                <div className={`bg-slate-900/60 border rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden transition-all duration-300 ${
                  currentPlan === 'enterprise' ? 'border-cyan-500 shadow-lg shadow-cyan-500/10' : 'border-slate-850 hover:border-slate-800'
                }`}>
                  <h3 className="text-sm font-black uppercase text-white tracking-widest">Enterprise Sovereignty</h3>
                  <div className="flex items-baseline gap-1 mt-2">
                    <span className="text-2xl font-black">$1,500</span>
                    <span className="text-[10px] text-slate-500 font-bold uppercase">/ Month</span>
                  </div>
                  <ul className="text-xs text-slate-400 space-y-2.5 mt-2 flex-1">
                    <li className="flex items-center gap-2 font-bold">✔ Dedicated Ray/GPU inference node</li>
                    <li className="flex items-center gap-2 font-bold">✔ Isolated sqlite logical databases</li>
                    <li className="flex items-center gap-2 font-bold">✔ High-availability SSO & SSO Auth</li>
                    <li className="flex items-center gap-2 font-bold">✔ Custom compliance & SOC dashboard</li>
                  </ul>
                  <button
                    disabled={currentPlan === 'enterprise' || isUpdating}
                    onClick={() => handleUpgradePlan('enterprise')}
                    className="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all duration-200 border border-slate-800 hover:bg-slate-950 bg-slate-900/50 disabled:opacity-40"
                  >
                    {currentPlan === 'enterprise' ? 'Active Plan' : 'Select Enterprise'}
                  </button>
                </div>

              </div>

              {/* Usage tracking monitor */}
              <div className="bg-slate-900/60 border border-slate-850 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
                <div className="border-b border-slate-800 pb-3 mb-2 flex justify-between items-center">
                  <span className="text-xs font-black text-slate-300 uppercase tracking-widest">Metered Quota Consumption</span>
                  <span className="text-[9px] font-mono text-slate-500">REDIS ATOMIC COUNTER SYNCED</span>
                </div>
                
                <div>
                  <div className="flex justify-between items-center text-xs mb-2">
                    <span className="text-slate-450 font-bold">Monthly Usage Footprint</span>
                    <span className="text-slate-200 font-mono font-bold">
                      {usageStats.monthlyChecks} / {currentPlan === 'enterprise' ? 'Unlimited' : usageStats.monthlyLimit} checks
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-950 border border-slate-850 rounded-full overflow-hidden">
                    <div 
                      style={{ width: `${currentPlan === 'enterprise' ? 1.5 : (usageStats.monthlyChecks / usageStats.monthlyLimit) * 100}%` }}
                      className="h-full bg-cyan-500 shadow-md shadow-cyan-500/40 rounded-full transition-all duration-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                  <div className="bg-slate-950/40 border border-slate-900 p-3.5 rounded-xl flex flex-col gap-0.5">
                    <span className="text-[9px] text-slate-500 font-bold uppercase">Daily checks run</span>
                    <span className="text-sm font-bold text-white font-mono">{usageStats.dailyChecks}</span>
                  </div>
                  <div className="bg-slate-950/40 border border-slate-900 p-3.5 rounded-xl flex flex-col gap-0.5">
                    <span className="text-[9px] text-slate-500 font-bold uppercase">Database isolation profile</span>
                    <span className="text-xs font-bold text-cyan-400 font-mono mt-0.5">
                      {currentPlan === 'enterprise' ? 'ISOLATED_PHYSICAL' : 'LOGICAL_ROW_SEPARATION'}
                    </span>
                  </div>
                  <div className="bg-slate-950/40 border border-slate-900 p-3.5 rounded-xl flex flex-col gap-0.5">
                    <span className="text-[9px] text-slate-500 font-bold uppercase">Billing strategy</span>
                    <span className="text-xs font-bold text-white mt-0.5 uppercase">{currentPlan === 'enterprise' ? 'Metered Overage (2¢/chk)' : 'Flat Tier'}</span>
                  </div>
                  <div className="bg-slate-950/40 border border-slate-900 p-3.5 rounded-xl flex flex-col gap-0.5">
                    <span className="text-[9px] text-slate-500 font-bold uppercase">Compute Queue</span>
                    <span className="text-xs font-bold text-white mt-0.5 font-mono">
                      {currentPlan === 'free' && 'cpu_low_priority'}
                      {currentPlan === 'pro' && 'gpu_shared'}
                      {currentPlan === 'enterprise' && 'dedicated_ray_worker'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Invoices list */}
              <div className="bg-slate-900/60 border border-slate-850 p-6 rounded-2xl shadow-xl flex flex-col gap-4">
                <div className="border-b border-slate-800 pb-3 mb-2 flex justify-between items-center">
                  <span className="text-xs font-black text-slate-300 uppercase tracking-widest">Invoice Transaction History</span>
                  <span className="text-[9px] font-mono text-slate-500">MOCK STRIPE PAYMENTS INTEGRATED</span>
                </div>
                <div className="space-y-2">
                  {invoices.map((inv, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-slate-950/40 border border-slate-900 p-4 rounded-xl text-xs">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-bold text-white">{inv.id}</span>
                        <span className="text-[10px] text-slate-550 font-bold">{inv.date}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-mono font-bold text-slate-350">{inv.amount}</span>
                        <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px] font-bold tracking-widest">
                          {inv.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

        </div>
      </main>

    </div>
  );
}
