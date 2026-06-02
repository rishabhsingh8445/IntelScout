"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AnimatedCard from "@/components/AnimatedCard";
import AnimatedText from "@/components/AnimatedText";
import axios from "axios";
import { Loader2, ArrowRightLeft, Building2, Search, Zap, LayoutGrid, CheckCircle2, Download } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toPng } from "html-to-image";

export default function MatrixPage() {
  const [competitors, setCompetitors] = useState<{name: string}[]>([]);
  const [compA, setCompA] = useState("");
  const [compB, setCompB] = useState("");
  const [loading, setLoading] = useState(false);
  const [matrixResult, setMatrixResult] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // Fetch competitors to populate suggestions
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`)
      .then((res) => {
        setCompetitors(res.data || []);
      })
      .catch((err) => console.error("Failed to fetch competitors", err));
  }, []);

  const handleCompare = async () => {
    if (!compA.trim() || !compB.trim()) {
      setError("Please enter both companies to compare.");
      return;
    }
    setError("");
    setLoading(true);
    setMatrixResult("");
    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/matrix`, {
        our_company: compA,
        competitor: compB
      });
      setMatrixResult(res.data.matrix);
    } catch (err) {
      console.error(err);
      setError("Failed to generate matrix. The backend might be busy or unavailable.");
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const temp = compA;
    setCompA(compB);
    setCompB(temp);
  };

  const handleExportImage = async () => {
    const element = document.getElementById("matrix-content");
    if (!element) return;
    
    // Temporarily remove overflow so scrollbars are not rendered in the image
    element.classList.remove("overflow-x-auto");
    
    try {
      const dataUrl = await toPng(element, { 
        backgroundColor: '#0f172a', 
        pixelRatio: 2,
        style: {
          borderRadius: '16px', // keep the rounded corners in the export
          padding: '24px' // Add explicit padding for the export
        }
      });
      
      const link = document.createElement("a");
      link.download = `Matrix_${compA}_vs_${compB}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error("Failed to export image", err);
      setError("Failed to export HD Image. Please try again.");
    } finally {
      element.classList.add("overflow-x-auto");
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <AnimatedText text="Feature Matrix" className="text-4xl font-extrabold tracking-tight text-white mb-2" />
          <p className="text-slate-400">Generate a comprehensive feature comparison matrix against any competitor.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-400 text-sm font-medium">
          <Zap className="w-4 h-4" />
          AI-Powered Analysis
        </div>
      </div>

      <AnimatedCard className="bg-slate-900/40 border border-slate-700/50 backdrop-blur-xl p-6 md:p-8" glowColor="139, 92, 246">
        <div className="flex flex-col lg:flex-row items-center gap-6">
          
          {/* Company A Input */}
          <div className="flex-1 w-full relative">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Primary Company</label>
            <div className="relative group">
              <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
              <input
                list="competitors-list"
                value={compA}
                onChange={(e) => setCompA(e.target.value)}
                placeholder="e.g. IntelScout"
                className="w-full bg-slate-950/50 border border-slate-700 text-white rounded-xl py-3 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all shadow-inner placeholder-slate-600"
              />
            </div>
          </div>

          {/* Swap Button */}
          <button 
            onClick={handleSwap}
            className="p-3 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-300 hover:text-white transition-all hover:rotate-180 duration-500 shadow-lg mt-6 lg:mt-0 flex-shrink-0"
            title="Swap Companies"
          >
            <ArrowRightLeft className="w-5 h-5" />
          </button>

          {/* Company B Input */}
          <div className="flex-1 w-full relative">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Competitor</label>
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-purple-400 transition-colors" />
              <input
                list="competitors-list"
                value={compB}
                onChange={(e) => setCompB(e.target.value)}
                placeholder="e.g. Acme Corp"
                className="w-full bg-slate-950/50 border border-slate-700 text-white rounded-xl py-3 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all shadow-inner placeholder-slate-600"
              />
            </div>
          </div>

          <datalist id="competitors-list">
            {competitors.map((c, i) => (
              <option key={i} value={c.name} />
            ))}
          </datalist>

          {/* Action Button */}
          <div className="w-full lg:w-auto mt-6 lg:mt-0 lg:self-end flex-shrink-0">
            <button
              onClick={handleCompare}
              disabled={loading}
              className="w-full lg:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-semibold py-3 px-8 rounded-xl shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <LayoutGrid className="w-5 h-5" />}
              {loading ? "Analyzing..." : "Generate Matrix"}
            </button>
          </div>
        </div>
        
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0, marginTop: 0 }} 
              animate={{ opacity: 1, height: 'auto', marginTop: 16 }} 
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="text-red-400 text-sm flex items-center gap-2 bg-red-900/20 p-3 rounded-lg border border-red-900/50 overflow-hidden"
            >
              <CheckCircle2 className="w-4 h-4 text-red-500 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </AnimatedCard>

      {/* Result Section */}
      <AnimatePresence mode="wait">
        {loading && (
          <motion.div 
            key="loading"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col items-center justify-center py-24 space-y-4"
          >
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-t-2 border-l-2 border-indigo-500 animate-spin"></div>
              <div className="absolute inset-0 w-16 h-16 rounded-full border-b-2 border-r-2 border-purple-500 animate-[spin_2s_reverse_infinite]"></div>
            </div>
            <p className="text-slate-400 font-medium animate-pulse">Scraping web data & comparing features...</p>
          </motion.div>
        )}

        {matrixResult && !loading && (
          <motion.div
            key="result"
            id="matrix-table-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-900/40 border border-slate-700/50 rounded-2xl backdrop-blur-xl overflow-hidden shadow-2xl"
          >
            <div className="bg-gradient-to-r from-indigo-900/40 to-purple-900/40 border-b border-slate-700/50 p-4 md:p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white flex items-center gap-3">
                <LayoutGrid className="w-6 h-6 text-indigo-400" />
                Comparison Results
              </h2>
              <div className="flex items-center gap-4">
                <div className="flex gap-2 items-center">
                  <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-sm font-semibold border border-slate-700">{compA}</span>
                  <span className="text-slate-500 font-bold text-xs">VS</span>
                  <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-sm font-semibold border border-slate-700">{compB}</span>
                </div>
                <button 
                  onClick={handleExportImage}
                  className="flex items-center gap-2 px-4 py-1.5 text-sm font-medium text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-all border border-indigo-500/20"
                >
                  <Download className="w-4 h-4" />
                  <span className="hidden sm:inline">Export HD Image</span>
                </button>
              </div>
            </div>
            <div id="matrix-content" className="p-6 md:p-8 overflow-x-auto prose prose-invert prose-indigo max-w-none 
              prose-table:w-full prose-table:border-collapse prose-table:text-left
              prose-th:bg-slate-800/50 prose-th:p-4 prose-th:border prose-th:border-slate-700 prose-th:text-slate-200
              prose-td:p-4 prose-td:border prose-td:border-slate-700/50 prose-td:text-slate-300
              prose-tr:transition-colors hover:prose-tr:bg-slate-800/30">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {matrixResult}
              </ReactMarkdown>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}