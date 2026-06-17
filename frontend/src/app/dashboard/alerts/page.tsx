"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { format } from "date-fns";
import AnimatedCard from "@/components/AnimatedCard";
import AnimatedText from "@/components/AnimatedText";
import GridBackground from "@/components/GridBackground";

interface Alert {
  id: number;
  competitor_id: number;
  detected_changes: string;
  possible_goal: string;
  threat_level: string;
  recommended_action: string;
  confidence_score: number;
  created_at: string;
}

interface Snapshot {
  id: number;
  snapshot_date: string;
  pricing_data: string;
  feature_list: string;
  messaging: string;
  sentiment?: string;
  sentiment_score?: number;
  sentiment_reason?: string;
}
import { useAuth } from "@clerk/nextjs";

export default function AlertsPage() {
  const { userId } = useAuth();
  const headers = { 'x-user-id': userId };

  const [competitors, setCompetitors] = useState<any[]>([]);
  const [selectedCompId, setSelectedCompId] = useState<number | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userId) {
      fetchCompetitors();
    }
  }, [userId]);

  useEffect(() => {
    if (selectedCompId) {
      fetchAlerts(selectedCompId);
    }
  }, [selectedCompId]);

  const fetchCompetitors = async () => {
    try {
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/competitors`, { headers });
      setCompetitors(res.data);
      if (res.data.length > 0) {
        setSelectedCompId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async (id: number) => {
    setLoading(true);
    try {
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/alerts/${id}`, { headers });
      setAlerts(res.data.alerts);
      setSnapshots(res.data.snapshots);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getThreatColor = (level: string) => {
    if (level === "High") return "text-red-500 bg-red-500/10 border-red-500/20";
    if (level === "Medium") return "text-orange-500 bg-orange-500/10 border-orange-500/20";
    return "text-green-500 bg-green-500/10 border-green-500/20";
  };

  const getSentimentBadge = (sentiment?: string, score?: number) => {
    if (!sentiment) return null;
    const scoreText = score ? ` → ${score.toFixed(2)}` : "";
    if (sentiment.toLowerCase() === "positive") {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">🟢 {sentiment}{scoreText}</span>;
    }
    if (sentiment.toLowerCase() === "negative") {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">🔴 {sentiment}{scoreText}</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">🟡 {sentiment}{scoreText}</span>;
  };

  if (loading && !competitors.length) {
    return <div className="p-8 text-white">Loading V2 Alerts...</div>;
  }

  return (
    <div className="relative min-h-screen text-white p-8">
      <GridBackground />
      <div className="relative z-10 max-w-6xl mx-auto space-y-8">
        <header className="mb-12">
          <AnimatedText 
            text="Autonomous Intelligence Alerts" 
            className="text-4xl font-black bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent"
          />
          <p className="text-white/60 mt-2 text-lg">Change Detection & Executive Strategy Recommendations</p>
        </header>

        <div className="flex gap-4 overflow-x-auto pb-4">
          {competitors.map((comp) => (
            <button
              key={comp.id}
              onClick={() => setSelectedCompId(comp.id)}
              className={`px-6 py-3 rounded-xl transition-all font-semibold border ${
                selectedCompId === comp.id
                  ? "bg-red-500/20 border-red-500/50 text-white shadow-[0_0_15px_rgba(239,68,68,0.3)]"
                  : "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:text-white"
              }`}
            >
              {comp.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-white/60 animate-pulse">Scanning Agent Database...</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <h2 className="text-2xl font-bold mb-4">🚨 Recent Alerts</h2>
              {alerts.length === 0 ? (
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-white/50">
                  No alerts generated yet. Wait for the Autonomous Pipeline to scan.
                </div>
              ) : (
                alerts.map((alert) => (
                  <AnimatedCard key={alert.id} className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getThreatColor(alert.threat_level)}`}>
                        {alert.threat_level} THREAT
                      </div>
                      <div className="text-sm text-white/40">
                        {format(new Date(alert.created_at), "MMM d, yyyy - HH:mm")}
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-1">Detected Change</h4>
                        <p className="text-lg font-medium">{alert.detected_changes}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-black/40 border border-white/5">
                          <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-1">Estimated Goal</h4>
                          <p className="text-white/80">{alert.possible_goal}</p>
                        </div>
                        <div className="p-4 rounded-xl bg-black/40 border border-white/5">
                          <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-1">Confidence Score</h4>
                          <p className="text-xl font-bold text-blue-400">{(alert.confidence_score * 100).toFixed(1)}%</p>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-white/10">
                        <h4 className="text-sm font-semibold text-orange-400 uppercase tracking-wider mb-2">⚡ Strategy Agent Recommendation</h4>
                        <p className="text-white/90 leading-relaxed text-lg">{alert.recommended_action}</p>
                      </div>
                    </div>
                  </AnimatedCard>
                ))
              )}
            </div>

            <div className="space-y-6">
              <h2 className="text-2xl font-bold mb-4">🕰️ Historical Snapshots</h2>
              {snapshots.length === 0 ? (
                <div className="text-white/50">No snapshots taken.</div>
              ) : (
                snapshots.map((snap) => (
                  <div key={snap.id} className="p-5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                    <div className="text-xs text-white/40 mb-3 border-b border-white/10 pb-2">
                      {format(new Date(snap.snapshot_date), "MMMM d, yyyy")}
                    </div>
                    <div className="space-y-3">
                      <div>
                        <h5 className="text-xs font-semibold text-white/40 uppercase">Pricing</h5>
                        <p className="text-sm text-white/80 line-clamp-2">{snap.pricing_data}</p>
                      </div>
                      <div>
                        <h5 className="text-xs font-semibold text-white/40 uppercase">Messaging</h5>
                        <p className="text-sm text-white/80 line-clamp-2">{snap.messaging}</p>
                      </div>
                      {snap.sentiment && (
                        <div className="pt-2 border-t border-white/10 mt-2">
                          <h5 className="text-xs font-semibold text-white/40 uppercase mb-1">Customer Sentiment</h5>
                          <div className="mb-1">{getSentimentBadge(snap.sentiment, snap.sentiment_score)}</div>
                          {snap.sentiment_reason && (
                            <p className="text-xs text-white/60 italic leading-relaxed">"{snap.sentiment_reason}"</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
