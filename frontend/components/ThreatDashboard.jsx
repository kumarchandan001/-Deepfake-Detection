import React, { useState } from "react";
import ThreatGraph from "./ThreatGraph";
import InvestigationTimeline from "./InvestigationTimeline";
import LiveThreatFeed from "./LiveThreatFeed";
import ForensicCopilot from "./ForensicCopilot";
import SeverityPanel from "./SeverityPanel";

export default function ThreatDashboard() {
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);

  const handleNodeSelect = (node) => {
    setSelectedNode(node);
  };

  const handleAlertSelect = (alert) => {
    setSelectedAlert(alert);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-500 selection:text-black">
      {/* Cyber Grid Mask Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900/40 via-slate-950 to-slate-950 -z-10 pointer-events-none" />

      {/* Cyber Header */}
      <header className="border-b border-slate-900 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-red-500 via-purple-600 to-cyan-500 flex items-center justify-center font-black text-white shadow-lg tracking-wider">
              SOC
            </div>
            <div>
              <h1 className="text-sm font-black uppercase tracking-widest text-white leading-none">Security Operations Center</h1>
              <p className="text-[9px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Autonomous deepfake forensic intelligence grid</p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 bg-slate-900/40 px-4 py-2 border border-slate-850 rounded-xl">
            <div className="flex flex-col items-end">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Grid Integrity</span>
              <span className="text-xs font-bold text-emerald-400 mt-0.5 flex items-center gap-1.5 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                ALL NODES GREEN
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Metric Counters Banner */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-2xl flex flex-col justify-between">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Total Scans Audited</span>
            <span className="text-2xl font-black font-mono tracking-tight text-white mt-1">45,198</span>
            <span className="text-[8px] text-emerald-400 font-bold font-mono uppercase mt-1">↑ 14.8% MONTHLY</span>
          </div>
          <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-2xl flex flex-col justify-between">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Adversarial Mitigations</span>
            <span className="text-2xl font-black font-mono tracking-tight text-red-400 mt-1">1,942</span>
            <span className="text-[8px] text-red-500 font-bold font-mono uppercase mt-1">LIVENESS ACTIVE</span>
          </div>
          <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-2xl flex flex-col justify-between">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Campaign Graph Loops</span>
            <span className="text-2xl font-black font-mono tracking-tight text-purple-400 mt-1">37</span>
            <span className="text-[8px] text-purple-400 font-bold font-mono uppercase mt-1">NETWORKX MAPS</span>
          </div>
          <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-2xl flex flex-col justify-between">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Distributed Node Load</span>
            <span className="text-2xl font-black font-mono tracking-tight text-cyan-400 mt-1">28.4%</span>
            <span className="text-[8px] text-cyan-400 font-bold font-mono uppercase mt-1">4 CLUSTERS ONLINE</span>
          </div>
        </div>

        {/* Dashboard Grid Modules */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* Column 1: Composite Severity and Incident Feed */}
          <div className="flex flex-col gap-6 lg:col-span-1">
            <SeverityPanel score={0.86} />
            <LiveThreatFeed onAlertSelect={handleAlertSelect} />
          </div>

          {/* Column 2 & 3: Threat Graph Topology and Neural Chat Copilot */}
          <div className="flex flex-col gap-6 lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2 h-[450px]">
                <ThreatGraph onNodeSelect={handleNodeSelect} />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-1 h-[500px]">
                <InvestigationTimeline />
              </div>
              <div className="md:col-span-1 h-[500px]">
                <ForensicCopilot />
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
