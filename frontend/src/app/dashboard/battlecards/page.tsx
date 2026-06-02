"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { useAuth } from "@clerk/nextjs";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  ShieldAlert, 
  Swords, 
  Zap, 
  Loader2, 
  Target,
  Building2,
  Download
} from "lucide-react";
import AnimatedCard from "@/components/AnimatedCard";
import AnimatedText from "@/components/AnimatedText";

export default function BattlecardsPage() {
  const { userId } = useAuth();
  const headers = { 'x-user-id': userId };

  const [report, setReport] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [companyA, setCompanyA] = useState("");
  const [companyB, setCompanyB] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [competitors, setCompetitors] = useState<{name: string}[]>([]);

  useEffect(() => {
    // Fetch existing competitors for suggestions
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`, { headers })
      .then((res) => setCompetitors(res.data || []))
      .catch(() => {});
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyA.trim() || !companyB.trim()) return;

    if (companyA.trim().toLowerCase() === companyB.trim().toLowerCase()) {
      setError("Please select two different companies to generate a battlecard.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setReport("");
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/battlecards`, {
        company_a: companyA,
        company_b: companyB,
      }, { headers });
      
      setReport(res.data.report || "No report generated.");
    } catch (err) {
      console.error("Failed to generate battlecard:", err);
      setError("Failed to generate battlecard. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 print:hidden">
        <div>
          <AnimatedText text="Battlecards" className="text-3xl font-bold tracking-tight text-white mb-2" />
          <p className="text-slate-400">AI-powered competitive battlecards for your sales team.</p>
        </div>
      </div>

      {/* Generation Form */}
      <AnimatedCard className="border border-white/10 bg-white/[0.02] rounded-xl p-6 backdrop-blur-sm print:hidden">
        <h3 className="font-semibold text-white flex items-center gap-2 mb-4">
          <Swords className="h-5 w-5 text-indigo-400" />
          Generate Battlecard
        </h3>
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-300">Your Company</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  list="comp-list"
                  type="text"
                  placeholder="e.g. IntelScout"
                  value={companyA}
                  onChange={(e) => setCompanyA(e.target.value)}
                  className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-300">Competitor</label>
              <div className="relative">
                <Target className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  list="comp-list"
                  type="text"
                  placeholder="e.g. Acme Corp"
                  value={companyB}
                  onChange={(e) => setCompanyB(e.target.value)}
                  className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                />
              </div>
            </div>
          </div>

          <datalist id="comp-list">
            {competitors.map((c, i) => (
              <option key={i} value={c.name} />
            ))}
          </datalist>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || !companyA.trim() || !companyB.trim() || companyA.trim().toLowerCase() === companyB.trim().toLowerCase()}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors border border-indigo-500/50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Researching & Generating...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  Generate Battlecard
                </>
              )}
            </button>
          </div>
        </form>
      </AnimatedCard>

      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3 print:hidden"
        >
          <ShieldAlert className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-200">{error}</p>
        </motion.div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-24 space-y-4">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-t-2 border-l-2 border-indigo-500 animate-spin"></div>
            <div className="absolute inset-0 w-16 h-16 rounded-full border-b-2 border-r-2 border-purple-500 animate-[spin_2s_reverse_infinite]"></div>
          </div>
          <p className="text-slate-400 font-medium animate-pulse">Scraping web data & generating battlecard...</p>
          <p className="text-slate-500 text-sm">This may take a minute while the AI researches both companies.</p>
        </div>
      )}
      {/* Result */}
      <AnimatePresence mode="wait">
        {report && !loading && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border border-white/10 bg-white/[0.02] rounded-xl backdrop-blur-sm overflow-hidden print:border-none print:shadow-none print:overflow-visible print:bg-white"
          >
            <div className="p-6 border-b border-white/10 bg-white/[0.01] print:hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/30">
                    <Target className="h-6 w-6 text-indigo-400" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">{companyA} vs {companyB}</h2>
                    <p className="text-sm text-slate-400 flex items-center gap-2">
                      <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
                      AI Generated Battlecard
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => window.print()}
                  className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-all border border-indigo-500/20"
                >
                  <Download className="w-4 h-4" />
                  Export PDF
                </button>
              </div>
            </div>
            
            <div className="p-8 overflow-y-auto custom-scrollbar bg-black/20 print:overflow-visible print:bg-white print:p-8">
              <div className="prose prose-invert max-w-none custom-print-content 
                prose-headings:font-medium prose-headings:tracking-tight 
                prose-h1:text-3xl prose-h1:text-white prose-h1:mb-8
                prose-h2:text-2xl prose-h2:text-indigo-100 prose-h2:mt-10 prose-h2:mb-4 prose-h2:pb-3 prose-h2:border-b prose-h2:border-white/10
                prose-h3:text-xl prose-h3:text-indigo-200 prose-h3:mt-8
                prose-p:text-slate-300 prose-p:leading-relaxed prose-p:text-[15px]
                prose-li:text-slate-300 prose-li:text-[15px]
                prose-strong:text-white prose-strong:font-semibold
                prose-table:border-collapse prose-table:w-full prose-table:mt-6
                prose-th:bg-white/5 prose-th:p-4 prose-th:text-left prose-th:border prose-th:border-white/10 prose-th:font-medium prose-th:text-slate-200
                prose-td:p-4 prose-td:border prose-td:border-white/5 prose-td:text-slate-300
                prose-blockquote:border-l-indigo-500 prose-blockquote:bg-indigo-500/5 prose-blockquote:py-2 prose-blockquote:px-5 prose-blockquote:rounded-r-xl prose-blockquote:not-italic prose-blockquote:text-slate-300"
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {report}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {!report && !loading && (
        <div className="border border-white/10 bg-white/[0.02] rounded-xl backdrop-blur-sm flex flex-col items-center justify-center p-12 text-center">
          <div className="h-20 w-20 rounded-full bg-white/5 flex items-center justify-center mb-6 border border-white/10">
            <Swords className="h-10 w-10 text-slate-500" />
          </div>
          <h3 className="text-2xl font-semibold text-white mb-3">Generate a Battlecard</h3>
          <p className="text-slate-400 max-w-md mx-auto text-lg">
            Enter two companies above and our AI will research and generate a comprehensive competitive battlecard.
          </p>
        </div>
      )}
    </div>
  );
}