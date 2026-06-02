"use client";

import { useState, useEffect } from "react";
import { Activity, Users, Lightbulb, Target, ArrowRight } from "lucide-react";
import AnimatedCard from "@/components/AnimatedCard";
import AnimatedText from "@/components/AnimatedText";
import axios from "axios";
import { useAuth } from "@clerk/nextjs";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";

export default function DashboardHome() {
  const { userId } = useAuth();
  const headers = { 'x-user-id': userId };

  const [stats, setStats] = useState({ competitors: 0, insights: 0 });
  const [briefing, setBriefing] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [compRes, insRes] = await Promise.all([
          axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`, { headers }).catch(() => ({ data: [] })),
          axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/insights`, { headers }).catch(() => ({ data: [] }))
        ]);
        
        setStats({
          competitors: compRes.data?.length || 0,
          insights: insRes.data?.length || 0
        });
      } catch (error) {
        console.error("Error fetching stats data", error);
      } finally {
        setLoading(false);
      }
    };
    
    const fetchBriefing = async () => {
      try {
        const briefRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/briefing`, { headers });
        setBriefing(briefRes.data?.briefing);
      } catch (error) {
        console.error("Error fetching briefing", error);
        setBriefing("No briefing available at the moment.");
      }
    };

    fetchStats();
    fetchBriefing();
  }, []);

  return (
    <div className="space-y-6">
      <AnimatedText text="Overview" className="text-3xl font-bold tracking-tight text-white mb-2" />
      <p className="text-slate-400 mb-8">Welcome back. Here is your competitive intelligence briefing.</p>
      
      {/* Daily Briefing Card */}
      {briefing && (
        <AnimatedCard delay={0.1} className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 p-6 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Lightbulb className="w-24 h-24 text-indigo-400" />
          </div>
          <div className="relative z-10">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" />
              Daily Executive Briefing
            </h2>
            <div className="prose prose-invert max-w-none mt-4
              prose-headings:font-medium prose-headings:tracking-tight 
              prose-h1:text-2xl prose-h1:text-white prose-h1:mb-6
              prose-h2:text-xl prose-h2:text-indigo-100 prose-h2:mt-6 prose-h2:mb-3 prose-h2:pb-2 prose-h2:border-b prose-h2:border-white/10
              prose-h3:text-lg prose-h3:text-indigo-200 prose-h3:mt-4
              prose-p:text-slate-300 prose-p:leading-relaxed prose-p:text-[15px]
              prose-li:text-slate-300 prose-li:text-[15px]
              prose-strong:text-white prose-strong:font-semibold
              prose-table:border-collapse prose-table:w-full prose-table:mt-4
              prose-th:bg-white/5 prose-th:p-3 prose-th:text-left prose-th:border prose-th:border-white/10 prose-th:font-medium prose-th:text-slate-200
              prose-td:p-3 prose-td:border prose-td:border-white/5 prose-td:text-slate-300"
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {briefing}
              </ReactMarkdown>
            </div>
          </div>
        </AnimatedCard>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link href="/dashboard/competitors">
          <AnimatedCard delay={0.2} className="bg-white/[0.02] border border-white/10 p-6 rounded-2xl flex flex-col gap-4 hover:border-indigo-500/50 transition-colors cursor-pointer">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-indigo-500/20 rounded-lg w-fit">
                <Users className="h-6 w-6 text-indigo-400" />
              </div>
              <span className="text-3xl font-bold text-white">{loading ? "-" : stats.competitors}</span>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Tracked Competitors</h3>
              <p className="text-slate-400 text-sm mt-1">Companies under active surveillance.</p>
            </div>
          </AnimatedCard>
        </Link>
        
        <Link href="/dashboard/insights">
          <AnimatedCard delay={0.3} className="bg-white/[0.02] border border-white/10 p-6 rounded-2xl flex flex-col gap-4 hover:border-purple-500/50 transition-colors cursor-pointer">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-purple-500/20 rounded-lg w-fit">
                <Target className="h-6 w-6 text-purple-400" />
              </div>
              <span className="text-3xl font-bold text-white">{loading ? "-" : stats.insights}</span>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Actionable Insights</h3>
              <p className="text-slate-400 text-sm mt-1">Total signals extracted by AI.</p>
            </div>
          </AnimatedCard>
        </Link>

        <Link href="/dashboard/competitors">
          <AnimatedCard delay={0.4} className="bg-white/[0.02] border border-white/10 p-6 rounded-2xl flex flex-col gap-4 hover:border-cyan-500/50 transition-colors cursor-pointer group">
            <div className="p-3 bg-cyan-500/20 rounded-lg w-fit group-hover:scale-110 transition-transform">
              <ArrowRight className="h-6 w-6 text-cyan-400" />
            </div>
            <div className="mt-auto">
              <h3 className="text-xl font-semibold text-white group-hover:text-cyan-400 transition-colors">Deep Dive</h3>
              <p className="text-slate-400 text-sm mt-1">View the full competitive matrix.</p>
            </div>
          </AnimatedCard>
        </Link>
      </div>
    </div>
  );
}