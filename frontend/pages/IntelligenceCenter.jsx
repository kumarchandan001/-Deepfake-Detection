import React, { useState } from "react";
import ThreatGraph from "../components/ThreatGraph";

export default function IntelligenceCenter() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchType, setSearchType] = useState("semantic"); // 'semantic' or 'perceptual'

  const mockSemanticResults = [
    {
      title: "Sybil Cloned Audio Propagation Campaign",
      score: 0.948,
      matches: "Matched voice signature from incident report INV-2026-9041.",
      tags: ["AUDIO_CLONE", "RUSSIA_SOURCE"],
      attribution: "Sybil Client-73"
    },
    {
      title: "VIP Extortion Video Splice Attempt",
      score: 0.812,
      matches: "Identified Laplacian boundary variance anomalies matching fake face models.",
      tags: ["VIDEO_SPOOF", "EXPLICIT_HOLD"],
      attribution: "Direct VPS Hosting"
    }
  ];

  const mockPerceptualResults = [
    {
      title: "Duplicate Image Hash Match - VIP Face",
      score: 0.985,
      matches: "Hamming distance 2 detected. Match verified against active campaign trackers.",
      tags: ["DUPLICATE_IMG", "HAMMING_MATCH"],
      attribution: "Instagram Web scraper"
    }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setTimeout(() => {
      if (searchType === "semantic") {
        setSearchResults(mockSemanticResults);
      } else {
        setSearchResults(mockPerceptualResults);
      }
      setIsSearching(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans py-8 px-6">
      <div className="max-w-7xl mx-auto flex flex-col gap-8">
        
        {/* Page Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-900 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-black text-white shadow-lg shadow-cyan-500/10">
              IC
            </div>
            <div>
              <h1 className="text-xl font-black uppercase tracking-widest text-white leading-none">Threat Intelligence Center</h1>
              <p className="text-[10px] text-slate-500 font-bold tracking-widest uppercase mt-0.5">Semantic search & perceptual campaign vector matching</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setSearchType("semantic")}
              className={`px-4 py-2 rounded-xl text-xs font-bold font-mono transition-all duration-200 border ${
                searchType === "semantic"
                  ? "bg-slate-900 border-slate-800 text-white shadow-sm"
                  : "border-transparent text-slate-500 hover:text-slate-350"
              }`}
            >
              [SEMANTIC VECTOR SEARCH]
            </button>
            <button
              onClick={() => setSearchType("perceptual")}
              className={`px-4 py-2 rounded-xl text-xs font-bold font-mono transition-all duration-200 border ${
                searchType === "perceptual"
                  ? "bg-slate-900 border-slate-800 text-white shadow-sm"
                  : "border-transparent text-slate-500 hover:text-slate-350"
              }`}
            >
              [PERCEPTUAL HASH INDEX]
            </button>
          </div>
        </div>

        {/* Search Input Panel */}
        <div className="bg-slate-900/60 border border-slate-850 p-6 rounded-2xl shadow-xl">
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            {searchType === "semantic" ? "Semantic Incident Memory Lookup" : "Perceptual Image Hash Matcher"}
          </h2>
          <p className="text-xs text-slate-500 mb-4 font-bold">
            {searchType === "semantic"
              ? "Query vector databases mapping sentence embedding similarities of high-profile deepfake campaigns."
              : "Search raw image fingerprints using aHash (average perceptual hashes) via Hamming sequence distance scans."}
          </p>

          <form onSubmit={handleSearch} className="flex gap-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={searchType === "semantic" ? "Enter query keywords (e.g. 'CEO voice clone campaign targeting financial markets')..." : "Enter 64-bit hexadecimal aHash string..."}
              className="flex-1 bg-slate-950 text-xs font-mono text-cyan-400 placeholder:text-slate-650 px-4 py-3 rounded-xl border border-slate-900 focus:outline-none focus:border-cyan-500/50 transition-all duration-200"
            />
            <button
              type="submit"
              disabled={isSearching || !searchQuery.trim()}
              className="px-6 py-3 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 font-bold text-xs uppercase tracking-wider text-white shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50 disabled:pointer-events-none transition-all duration-200"
            >
              Search
            </button>
          </form>
        </div>

        {/* Grid: Search Results & Threat Graph */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Results column */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            <div className="bg-slate-900/60 border border-slate-850 p-6 rounded-2xl shadow-xl flex-1 flex flex-col min-h-[350px]">
              <div className="border-b border-slate-800 pb-3 mb-4 shrink-0 flex justify-between items-center">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Scanned Matches</span>
                <span className="text-[9px] font-mono text-slate-500">FAISS CACHE DIRECTORY</span>
              </div>

              {isSearching ? (
                <div className="flex-1 flex flex-col items-center justify-center gap-2 font-mono">
                  <span className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></span>
                  <span className="text-[10px] text-slate-550 font-bold uppercase tracking-wider mt-2">Scanning vector space indices...</span>
                </div>
              ) : searchResults.length > 0 ? (
                <div className="space-y-4 overflow-y-auto max-h-[400px] pr-1">
                  {searchResults.map((res, idx) => (
                    <div key={idx} className="border border-slate-800/80 bg-slate-950/40 p-4 rounded-xl flex flex-col gap-2 hover:border-slate-700 transition-all duration-200">
                      <div className="flex justify-between items-start gap-2">
                        <h4 className="text-xs font-bold text-white leading-normal uppercase">{res.title}</h4>
                        <span className="text-[9px] font-mono font-black text-cyan-400 shrink-0">
                          {(res.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed font-bold">{res.matches}</p>
                      <div className="flex justify-between items-center border-t border-slate-900/60 pt-2 mt-1">
                        <div className="flex gap-1">
                          {res.tags.map((tag, tIdx) => (
                            <span key={tIdx} className="text-[8px] bg-slate-950 px-1.5 py-0.5 border border-slate-900 rounded font-mono font-bold text-slate-500 uppercase">
                              {tag}
                            </span>
                          ))}
                        </div>
                        <span className="text-[8px] font-mono text-slate-500">Actor: <span className="text-cyan-400 font-bold">{res.attribution}</span></span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center font-mono">
                  <span className="text-[10px] text-slate-650 font-bold uppercase tracking-widest">
                    Awaiting search parameters input query
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Graph Visualization column */}
          <div className="lg:col-span-2 h-[550px]">
            <ThreatGraph />
          </div>

        </div>

      </div>
    </div>
  );
}
