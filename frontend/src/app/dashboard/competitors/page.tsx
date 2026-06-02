"use client";

import React, { useState, useEffect, memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { useAuth } from "@clerk/nextjs";
import { 
  Users, 
  Plus, 
  Trash2, 
  Globe, 
  Search,
  Activity,
  Loader2,
  Eye,
  EyeOff,
  RefreshCw,
  FileText,
  X,
  Download,
  MessageSquare,
  ChevronRight,
  ChevronDown,
  Zap
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MemoizedMarkdown = memo(({ content }: { content: string }) => {
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>;
});

const CustomSelect = ({ value, onChange, options }: { value: string, onChange: (val: string) => void, options: string[] }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between bg-black/20 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
      >
        <span>{value === "Short" ? "Short Report" : value === "Long" ? "Deep Dive Report" : value}</span>
        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="absolute z-50 w-full mt-2 bg-[#0f172a] border border-white/10 rounded-lg shadow-[0_8px_30px_rgb(0,0,0,0.5)] overflow-hidden"
            >
              {options.map(opt => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => { onChange(opt); setIsOpen(false); }}
                  className={`w-full text-left px-4 py-3 text-sm transition-colors ${value === opt ? "bg-blue-600/20 text-blue-400 font-medium" : "text-slate-300 hover:bg-white/10 hover:text-white"}`}
                >
                  {opt === "Short" ? "Short Report" : opt === "Long" ? "Deep Dive Report" : opt}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
};

interface Competitor {
  id: number;
  name: string;
  timeframe: string;
  status: string;
  report: string | null;
  is_watched: boolean;
  lastScraped: string;
}

export default function CompetitorsPage() {
  const { userId } = useAuth();
  const headers = { 'x-user-id': userId };

  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Competitor | null>(null);

  // Report Q&A State
  const [reportQuery, setReportQuery] = useState("");
  const [reportAnswer, setReportAnswer] = useState("");
  const [reportSources, setReportSources] = useState<any[]>([]);
  const [isSearchingReport, setIsSearchingReport] = useState(false);
  const [reportSearchError, setReportSearchError] = useState("");

  const handleOpenReport = (competitor: Competitor) => {
    setSelectedReport(competitor);
    setReportQuery("");
    setReportAnswer("");
    setReportSources([]);
    setReportSearchError("");
  };

  const handleReportSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportQuery.trim() || !selectedReport) return;

    setIsSearchingReport(true);
    setReportSearchError("");
    
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/search`, {
        params: { q: reportQuery, competitor: selectedReport.name },
        timeout: 45000
      });
      
      const data = response.data.results || response.data || [];
      setReportSources(Array.isArray(data) ? data : [data]);
      if (response.data.answer) {
        setReportAnswer(response.data.answer);
      } else {
        setReportAnswer('');
      }
    } catch (error: any) {
      console.error(error);
      setReportSearchError("Failed to search report data.");
    } finally {
      setIsSearchingReport(false);
    }
  };

  const [formData, setFormData] = useState({
    name: "",
    timeframe: "Since Launch",
    report_type: "Short",
  });

  const fetchCompetitors = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`, { headers });
      setCompetitors(res.data);
    } catch (error) {
      console.error("Failed to fetch competitors", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompetitors();
  }, []);

  // Background polling for researching competitors
  useEffect(() => {
    const isAnyResearching = competitors.some(c => c.status === "Researching...");
    if (!isAnyResearching) return;

    const intervalId = setInterval(async () => {
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`, { headers });
        setCompetitors(res.data);
      } catch (error) {
        console.error("Failed to poll competitors", error);
      }
    }, 5000); // Check every 5 seconds

    return () => clearInterval(intervalId);
  }, [competitors]);

  const handleAddCompetitor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors?name=${encodeURIComponent(formData.name)}&timeframe=${encodeURIComponent(formData.timeframe)}&report_type=${encodeURIComponent(formData.report_type)}`
      );
      setFormData({ name: "", timeframe: "Since Launch", report_type: "Short" });
      setShowAddForm(false);
      // Refresh list after adding
      await fetchCompetitors();
    } catch (error) {
      console.error("Failed to add competitor", error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors/${id}`, { headers });
      setCompetitors(competitors.filter((c) => c.id !== id));
    } catch (error) {
      console.error("Failed to delete competitor", error);
    }
  };

  const handleToggleWatch = async (id: number) => {
    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors/${id}/watch`, {}, { headers });
      setCompetitors(competitors.map(c => 
        c.id === id ? { ...c, is_watched: res.data.is_watched } : c
      ));
    } catch (error) {
      console.error("Failed to toggle watch", error);
    }
  };

  const handleRescrape = async (id: number) => {
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors/${id}/rescrape`, {}, { headers });
      // Update status locally
      setCompetitors(competitors.map(c => 
        c.id === id ? { ...c, status: "Researching..." } : c
      ));
    } catch (error) {
      console.error("Failed to rescrape", error);
    }
  };

  const filteredCompetitors = competitors.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="pb-10">
      <div className={`space-y-8 ${selectedReport ? 'print:hidden' : ''}`}>
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold tracking-tight text-white flex items-center gap-3"
          >
            <Users className="w-8 h-8 text-blue-400" />
            Competitors
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 mt-1"
          >
            Manage and track your competitive landscape.
          </motion.p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search competitors..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white/[0.03] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all w-full md:w-64"
            />
          </div>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors border border-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.2)]"
          >
            {showAddForm ? <Users className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {showAddForm ? "View Grid" : "Add New"}
          </button>
        </div>
      </div>

      {/* Add Competitor Form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div 
            initial={{ opacity: 0, height: 0, overflow: "hidden" }}
            animate={{ opacity: 1, height: "auto", overflow: "visible" }}
            exit={{ opacity: 0, height: 0, overflow: "hidden" }}
            className="bg-white/[0.02] border border-white/10 rounded-xl p-6 backdrop-blur-md relative z-40"
          >
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              Track New Competitor
            </h2>
            <form onSubmit={handleAddCompetitor} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-300">Company Name</label>
                  <input 
                    required
                    type="text" 
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="e.g. OpenAI, Anthropic" 
                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-300">Timeframe</label>
                  <CustomSelect 
                    value={formData.timeframe}
                    onChange={(val) => setFormData({...formData, timeframe: val})}
                    options={["Since Launch", "Last 6 Months", "Last 1 Year", "Last 3 Months"]}
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-300">Report Type</label>
                  <CustomSelect 
                    value={formData.report_type}
                    onChange={(val) => setFormData({...formData, report_type: val})}
                    options={["Short", "Long"]}
                  />
                </div>
              </div>
              <div className="flex justify-end pt-2">
                <button 
                  type="submit" 
                  disabled={submitting}
                  className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-600/50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors border border-emerald-500/50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Starting Research...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      Add & Research
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Competitors Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : filteredCompetitors.length === 0 ? (
        <div className="bg-white/[0.02] border border-white/5 rounded-xl p-12 text-center flex flex-col items-center">
          <Globe className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-lg font-medium text-white mb-1">No competitors found</h3>
          <p className="text-slate-400 text-sm max-w-md mx-auto mb-6">
            {searchQuery 
              ? "No competitors matching your search. Try adjusting your filters." 
              : "You aren't tracking any competitors yet. Add your first competitor to start analyzing."}
          </p>
          {!searchQuery && !showAddForm && (
            <button 
              onClick={() => setShowAddForm(true)}
              className="bg-white/[0.05] hover:bg-white/[0.1] text-white px-4 py-2 rounded-lg text-sm transition-colors border border-white/10"
            >
              Add First Competitor
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredCompetitors.map((competitor, idx) => (
              <motion.div 
                key={competitor.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="bg-white/[0.02] border border-white/10 rounded-xl p-5 hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col"
              >
                {/* Subtle gradient blob on hover */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-blue-500/20 transition-colors pointer-events-none" />
                
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 flex items-center justify-center text-lg font-bold text-white shadow-inner">
                      {competitor.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-white group-hover:text-blue-400 transition-colors line-clamp-1">
                        {competitor.name}
                      </h3>
                      <span className={`text-xs flex items-center gap-1 ${competitor.status === "Active" ? "text-emerald-400" : "text-amber-400"}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${competitor.status === "Active" ? "bg-emerald-400" : "bg-amber-400 animate-pulse"}`} />
                        {competitor.status}
                      </span>
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDelete(competitor.id)}
                    className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors opacity-0 group-hover:opacity-100"
                    title="Delete competitor"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="text-sm text-slate-400 mb-4 flex-grow">
                  <span className="text-xs text-slate-500">Timeframe: </span>
                  <span className="text-slate-300">{competitor.timeframe}</span>
                </div>

                {/* Report preview */}
                {competitor.report && (
                  <button
                    onClick={() => handleOpenReport(competitor)}
                    className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 mb-3 transition-colors"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    View Report
                  </button>
                )}
                
                <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs text-slate-500">
                  <span className="flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-emerald-500/70" />
                    {competitor.lastScraped}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleToggleWatch(competitor.id)}
                      className={`p-1.5 rounded-md transition-colors ${competitor.is_watched ? "text-amber-400 hover:bg-amber-400/10" : "text-slate-500 hover:text-slate-300 hover:bg-white/5"}`}
                      title={competitor.is_watched ? "Unwatch" : "Watch"}
                    >
                      {competitor.is_watched ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => handleRescrape(competitor.id)}
                      className="p-1.5 text-slate-500 hover:text-blue-400 hover:bg-blue-400/10 rounded-md transition-colors"
                      title="Rescrape"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
      </div>

      {/* Report Modal */}
      <AnimatePresence>
        {selectedReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-12 pt-24 md:pt-28 pb-10 print:static print:p-0 print:block">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedReport(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-md print:hidden"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-4xl max-h-full glass-card rounded-2xl shadow-2xl flex flex-col overflow-hidden print:max-w-none print:shadow-none print:border-none print:rounded-none print:overflow-visible print:max-h-none print:h-auto print:bg-white"
            >
              <div className="flex items-center justify-between p-6 border-b border-white/10 bg-white/[0.02] print:hidden">
                <h2 className="text-xl font-medium text-white flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
                    <FileText className="w-5 h-5 text-indigo-400" />
                  </div>
                  {selectedReport.name} Intelligence Report
                </h2>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => window.print()}
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 rounded-lg transition-all border border-transparent hover:border-indigo-500/20"
                    title="Export to PDF"
                  >
                    <Download className="w-4 h-4" />
                    <span className="hidden sm:inline">Export PDF</span>
                  </button>
                  <button 
                    onClick={() => handleOpenReport(null as any)}
                    className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-xl transition-all"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div className="p-8 overflow-y-auto custom-scrollbar bg-black/20 print:overflow-visible print:bg-white print:p-8">
                
                {/* Embedded Report Q&A */}
                <div className="mb-10 bg-white/[0.02] border border-white/10 rounded-2xl p-6 print:hidden">
                  <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-indigo-400" />
                    Chat with this Report
                  </h3>
                  <form onSubmit={handleReportSearch} className="relative flex items-center gap-3 mb-6">
                    <div className="relative flex-1">
                      <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-slate-500">
                        <Search className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        value={reportQuery}
                        onChange={(e) => setReportQuery(e.target.value)}
                        placeholder={`Ask a question about ${selectedReport.name}...`}
                        className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-11 pr-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all text-sm"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={isSearchingReport || !reportQuery.trim()}
                      className="h-[46px] px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-medium transition-colors text-sm flex items-center justify-center min-w-[100px]"
                    >
                      {isSearchingReport ? <Loader2 className="w-4 h-4 animate-spin" /> : "Ask"}
                    </button>
                  </form>

                  {reportSearchError && (
                    <div className="text-red-400 text-sm mb-4 px-2">{reportSearchError}</div>
                  )}

                  <AnimatePresence>
                    {reportAnswer && (
                      <motion.div 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 backdrop-blur-md mb-4"
                      >
                        <div className="flex items-center gap-2 mb-3">
                          <Zap className="w-4 h-4 text-indigo-400" />
                          <h4 className="font-semibold text-indigo-100 text-sm">AI Answer</h4>
                        </div>
                        <div className="prose prose-invert max-w-none prose-p:text-slate-300 prose-p:text-sm prose-p:leading-relaxed">
                          <ReactMarkdown>{reportAnswer}</ReactMarkdown>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Markdown Report Render */}
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
                  <MemoizedMarkdown content={selectedReport.report || ""} />
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}