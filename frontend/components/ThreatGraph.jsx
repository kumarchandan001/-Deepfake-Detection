import React, { useState } from "react";

export default function ThreatGraph({ nodes = [], edges = [], onNodeSelect }) {
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);

  // Mock graph data in case prop is empty
  const defaultNodes = [
    { id: "A1", label: "Sybil Botnet Client-73", type: "actor", severity: 0.92, ip: "185.220.101.4" },
    { id: "M1", label: "VIP_Deepfake_Speech.wav", type: "audio", severity: 0.88, format: "audio/wav" },
    { id: "M2", label: "CEO_PressConference_Spoof.mp4", type: "video", severity: 0.95, format: "video/mp4" },
    { id: "T1", label: "@VIP_Corporate_Official", type: "target", severity: 0.65, platform: "Twitter/X" },
    { id: "A2", label: "Rogue-Hosting VPS-9", type: "infrastructure", severity: 0.81, ip: "45.138.74.12" },
    { id: "M3", label: "Fake_Signature_Contract.jpg", type: "image", severity: 0.74, format: "image/jpeg" },
  ];

  const defaultEdges = [
    { source: "A1", target: "M1", relation: "GENERATE" },
    { source: "A1", target: "M2", relation: "GENERATE" },
    { source: "M1", target: "T1", relation: "TARGET" },
    { source: "M2", target: "T1", relation: "TARGET" },
    { source: "A2", target: "A1", relation: "HOST" },
    { source: "A2", target: "M3", relation: "HOST" },
    { source: "M3", target: "T1", relation: "TARGET" },
  ];

  const activeNodes = nodes.length > 0 ? nodes : defaultNodes;
  const activeEdges = edges.length > 0 ? edges : defaultEdges;

  // Simple static coordinates mapping for aesthetic visualization
  const positions = {
    "A2": { x: 100, y: 150 },
    "A1": { x: 300, y: 100 },
    "M3": { x: 250, y: 280 },
    "M1": { x: 500, y: 80 },
    "M2": { x: 500, y: 200 },
    "T1": { x: 700, y: 150 },
  };

  // Generate fallback positions dynamically for unknown nodes
  activeNodes.forEach((node, idx) => {
    if (!positions[node.id]) {
      positions[node.id] = {
        x: 200 + (idx % 3) * 180,
        y: 100 + Math.floor(idx / 3) * 100
      };
    }
  });

  const getNodeColor = (type) => {
    switch (type) {
      case "actor":
        return { border: "border-red-500", bg: "bg-red-950/80", text: "text-red-400", fill: "#ef4444" };
      case "audio":
        return { border: "border-purple-500", bg: "bg-purple-950/80", text: "text-purple-400", fill: "#a855f7" };
      case "video":
        return { border: "border-fuchsia-500", bg: "bg-fuchsia-950/80", text: "text-fuchsia-400", fill: "#d946ef" };
      case "image":
        return { border: "border-amber-500", bg: "bg-amber-950/80", text: "text-amber-400", fill: "#f59e0b" };
      case "target":
        return { border: "border-cyan-500", bg: "bg-cyan-950/80", text: "text-cyan-400", fill: "#06b6d4" };
      default:
        return { border: "border-slate-500", bg: "bg-slate-900/80", text: "text-slate-400", fill: "#64748b" };
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onNodeSelect) onNodeSelect(node);
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-2xl relative overflow-hidden flex flex-col h-full">
      {/* Background cyber grid lines */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black_70%)] opacity-35 -z-10" />

      <div className="flex items-center justify-between mb-4 border-b border-slate-800/60 pb-3 shrink-0">
        <div>
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Topological Threat Campaign Network</h3>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">Misinformation loops & adversarial correlation graph</p>
        </div>
        <div className="flex gap-2 text-[9px] font-bold uppercase text-slate-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span> Actor</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500"></span> Audio</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-fuchsia-500"></span> Video</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-500"></span> Target</span>
        </div>
      </div>

      <div className="flex-1 relative min-h-[300px] border border-slate-950 bg-slate-950/80 rounded-xl overflow-hidden shadow-inner">
        {/* SVG Container for Edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155" />
            </marker>
            <marker id="arrow-active" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#06b6d4" />
            </marker>
          </defs>

          {activeEdges.map((edge, idx) => {
            const p1 = positions[edge.source];
            const p2 = positions[edge.target];
            if (!p1 || !p2) return null;

            const isSelected = selectedNode && (selectedNode.id === edge.source || selectedNode.id === edge.target);
            const isHovered = hoveredNode && (hoveredNode.id === edge.source || hoveredNode.id === edge.target);

            return (
              <g key={idx}>
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={isSelected || isHovered ? "#06b6d4" : "#1e293b"}
                  strokeWidth={isSelected || isHovered ? "2" : "1.2"}
                  strokeDasharray={edge.relation === "HOST" ? "4,4" : "0"}
                  markerEnd={isSelected || isHovered ? "url(#arrow-active)" : "url(#arrow)"}
                  className="transition-all duration-300"
                />
                {(isSelected || isHovered) && (
                  <text
                    x={(p1.x + p2.x) / 2}
                    y={(p1.y + p2.y) / 2 - 6}
                    fill="#06b6d4"
                    fontSize="8"
                    fontWeight="black"
                    textAnchor="middle"
                    className="font-mono tracking-widest uppercase bg-slate-950"
                  >
                    {edge.relation}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Nodes Positioning */}
        {activeNodes.map((node) => {
          const pos = positions[node.id] || { x: 100, y: 100 };
          const theme = getNodeColor(node.type);
          const isSelected = selectedNode?.id === node.id;
          const isHovered = hoveredNode?.id === node.id;

          return (
            <button
              key={node.id}
              onClick={() => handleNodeClick(node)}
              onMouseEnter={() => setHoveredNode(node)}
              onMouseLeave={() => setHoveredNode(null)}
              style={{ left: `${pos.x}px`, top: `${pos.y}px` }}
              className={`absolute -translate-x-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-full border bg-slate-900 shadow-lg cursor-pointer transition-all duration-300 z-10 ${
                isSelected 
                  ? `${theme.border} scale-125 shadow-cyan-500/20 bg-slate-950` 
                  : isHovered 
                  ? `${theme.border} scale-110 shadow-slate-500/10` 
                  : "border-slate-800 hover:border-slate-650"
              }`}
            >
              {/* Inner dot representing severity */}
              <div 
                className="w-3.5 h-3.5 rounded-full transition-all duration-300"
                style={{ 
                  backgroundColor: theme.fill, 
                  opacity: node.severity ? 0.3 + node.severity * 0.7 : 0.7,
                  boxShadow: isSelected ? `0 0 12px ${theme.fill}` : "none"
                }}
              />

              {/* Tooltip Label */}
              <span className={`absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[9px] font-mono tracking-wider font-bold transition-all duration-200 px-1.5 py-0.5 rounded bg-slate-950/90 border border-slate-900 ${
                isSelected || isHovered ? "opacity-100 text-white border-slate-850" : "opacity-60 text-slate-500"
              }`}>
                {node.id}
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Node Details Box */}
      {selectedNode ? (
        <div className="mt-4 bg-slate-950/60 border border-slate-850 rounded-xl p-4 shrink-0 transition-all duration-300 animate-fadeIn">
          <div className="flex justify-between items-start">
            <div className="flex gap-2 items-center">
              <span className={`w-2 h-2 rounded-full`} style={{ backgroundColor: getNodeColor(selectedNode.type).fill }} />
              <h4 className="text-xs font-black uppercase text-white font-mono tracking-wide">{selectedNode.label}</h4>
            </div>
            <button 
              onClick={() => setSelectedNode(null)} 
              className="text-slate-500 hover:text-white font-mono text-[9px] font-bold uppercase"
            >
              [Close]
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
            <div className="flex flex-col">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Node ID</span>
              <span className="text-xs font-bold text-slate-350 font-mono">{selectedNode.id}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Anomaly Type</span>
              <span className="text-xs font-bold text-slate-350 font-mono capitalize">{selectedNode.type}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Risk Coefficient</span>
              <span className="text-xs font-bold font-mono text-cyan-400">
                {(selectedNode.severity * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[8px] text-slate-500 font-bold uppercase">Forensic Parameter</span>
              <span className="text-xs font-bold text-slate-350 font-mono truncate">
                {selectedNode.ip || selectedNode.format || selectedNode.platform || "N/A"}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-4 text-center border border-dashed border-slate-900 rounded-xl py-4 shrink-0">
          <span className="text-[10px] text-slate-650 font-bold uppercase tracking-widest">
            Select a network node to isolate propagation links
          </span>
        </div>
      )}
    </div>
  );
}
