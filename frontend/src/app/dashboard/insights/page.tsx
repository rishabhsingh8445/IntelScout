"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { 
  Lightbulb, 
  AlertCircle, 
  TrendingUp, 
  Clock, 
  CheckCircle2,
  ChevronRight,
  ShieldAlert,
  Zap,
  Activity
} from "lucide-react";

interface Insight {
  id: number;
  competitor_id: number;
  competitor: string;
  category: string;
  title: string;
  summary: string;
  time: string;
  score: number;
  sourceUrl: string;
}

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string>("All");

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/insights`);
        setInsights(Array.isArray(response.data) ? response.data : []);
        setError(null);
      } catch (err: any) {
        console.error("Error fetching insights:", err);
        setError("Failed to load insights. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  const getCategoryIcon = (category?: string) => {
    switch (category?.toLowerCase()) {
      case 'product':
        return <Zap className="w-5 h-5 text-indigo-400" />;
      case 'funding':
      case 'financial':
        return <TrendingUp className="w-5 h-5 text-emerald-400" />;
      case 'hiring':
      case 'team':
        return <Activity className="w-5 h-5 text-amber-400" />;
      case 'partnership':
        return <CheckCircle2 className="w-5 h-5 text-cyan-400" />;
      default:
        return <Lightbulb className="w-5 h-5 text-blue-400" />;
    }
  };

  const getCategoryColor = (category?: string) => {
    switch (category?.toLowerCase()) {
      case 'product':
        return 'bg-indigo-500/10 border-indigo-500/20';
      case 'funding':
      case 'financial':
        return 'bg-emerald-500/10 border-emerald-500/20';
      case 'hiring':
      case 'team':
        return 'bg-amber-500/10 border-amber-500/20';
      case 'partnership':
        return 'bg-cyan-500/10 border-cyan-500/20';
      default:
        return 'bg-blue-500/10 border-blue-500/20';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-rose-400';
    if (score >= 75) return 'text-amber-400';
    return 'text-emerald-400';
  };

  const uniqueCompanies = ["All", ...Array.from(new Set(insights.map(i => i.competitor)))];
  const filteredInsights = selectedCompany === "All" 
    ? insights 
    : insights.filter(i => i.competitor === selectedCompany);

  return (
    <div className="space-y-6 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold tracking-tight text-white mb-2"
          >
            Insights Feed
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 max-w-2xl"
          >
            AI-extracted competitive signals and market intelligence from your tracked competitors.
          </motion.p>
        </div>
      </div>

      {/* Filters */}
      {!loading && !error && insights.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2 custom-scrollbar">
          {uniqueCompanies.map(company => (
            <button
              key={company}
              onClick={() => setSelectedCompany(company)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all border ${
                selectedCompany === company 
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' 
                  : 'bg-white/[0.02] text-slate-400 border-white/10 hover:bg-white/[0.05] hover:text-slate-300 hover:border-white/20'
              }`}
            >
              {company}
            </button>
          ))}
        </div>
      )}

      {error && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-amber-400 font-medium">Connection Error</h3>
            <p className="text-amber-500/80 text-sm mt-1">{error}</p>
          </div>
        </motion.div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="animate-pulse bg-white/[0.02] border border-white/10 rounded-xl h-64" />
          ))}
        </div>
      ) : (
        <div className="relative">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {filteredInsights.map((insight, index) => (
                <motion.div
                  key={insight.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                  className="bg-white/[0.02] border border-white/10 rounded-xl p-5 hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col"
                >
                  {/* Subtle gradient blob on hover */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-blue-500/20 transition-colors pointer-events-none" />
                  
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg flex-shrink-0 border flex items-center justify-center mt-1 ${getCategoryColor(insight.category)}`}>
                        {getCategoryIcon(insight.category)}
                      </div>
                      <div>
                        <h3 className="text-base font-semibold text-white group-hover:text-blue-400 transition-colors line-clamp-2 leading-tight mb-1">
                          {insight.title}
                        </h3>
                        <span className={`text-xs flex items-center gap-1 font-medium ${getScoreColor(insight.score)}`}>
                          <span className="capitalize">{insight.category}</span> • {insight.score}% confidence
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-sm text-slate-400 mb-6 flex-grow line-clamp-4 leading-relaxed">
                    {insight.summary}
                  </div>

                  <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs text-slate-500 mt-auto">
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {insight.time}
                    </span>
                    <span className="px-2 py-1 bg-white/5 rounded-md text-slate-300 font-medium border border-white/10 truncate max-w-[120px]">
                      {insight.competitor}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
            
          {insights.length === 0 && !error && (
            <div className="text-center py-20 bg-white/[0.02] border border-white/10 rounded-2xl">
              <Lightbulb className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-white mb-2">No insights yet</h3>
              <p className="text-slate-400">Add competitors and run research to generate AI-driven insights.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}