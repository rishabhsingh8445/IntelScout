"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Zap, Activity, Shield, Globe, ArrowRight, X } from "lucide-react";
import { useAuth, SignInButton } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";
import ParticleField from "@/components/ParticleField";
import FloatingOrbs from "@/components/FloatingOrbs";
import GridBackground from "@/components/GridBackground";
import AnimatedCard from "@/components/AnimatedCard";
import AnimatedText from "@/components/AnimatedText";

const stagger = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.3 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { 
    opacity: 1, y: 0, 
    transition: { duration: 0.7, ease: [0.23, 1, 0.32, 1] } 
  },
};

export default function LandingPage() {
  const { userId } = useAuth();
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);

  // Automatically open the dashboard if signed in, and close it if signed out
  useEffect(() => {
    if (userId) {
      setIsDashboardOpen(true);
    } else {
      setIsDashboardOpen(false);
    }
  }, [userId]);

  return (
    <div className="min-h-screen bg-[#030014] text-white selection:bg-indigo-500/30 overflow-x-hidden font-sans relative">
      
      {/* === BACKGROUND LAYERS === */}
      <ParticleField particleCount={150} />
      <FloatingOrbs />
      <GridBackground />
      
      {/* === NAVBAR === */}
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
        className="fixed top-6 left-0 right-0 z-50 flex justify-center pointer-events-none px-4"
      >
        <div className="flex items-center justify-between px-6 h-16 rounded-full w-full max-w-5xl pointer-events-auto border border-white/[0.08] shadow-[0_8px_32px_rgba(0,0,0,0.12)] backdrop-blur-md bg-white/[0.02]">
          <Link href="/" className="flex items-center gap-3 group">
            <motion.div 
              className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/25 relative overflow-hidden"
              whileHover={{ rotate: 180, scale: 1.1 }}
              transition={{ type: "spring" as any, stiffness: 200 }}
            >
              <div className="absolute inset-0 bg-white/10 animate-pulse-glow" />
              <Zap className="h-5 w-5 text-white relative z-10" fill="currentColor" />
            </motion.div>
            <span className="font-bold text-xl tracking-tight text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-indigo-400 group-hover:to-cyan-400 transition-all duration-300">IntelScout</span>
          </Link>
          <nav className="flex gap-8 items-center">
            <Link href="#features" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors tracking-wide">
              Features
            </Link>
            {userId ? (
              <button onClick={() => setIsDashboardOpen(true)} className="text-sm font-semibold glass-card border border-white/10 px-6 py-2.5 rounded-full hover:bg-white/10 transition-all cursor-pointer">
                Dashboard
              </button>
            ) : (
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <SignInButton mode="modal">
                  <button className="relative text-sm font-bold bg-white text-black px-6 py-2.5 rounded-full hover:bg-slate-200 transition-all inline-flex items-center justify-center overflow-hidden group shadow-[0_0_20px_rgba(255,255,255,0.15)] cursor-pointer">
                    <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/50 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
                    Sign In
                  </button>
                </SignInButton>
              </motion.div>
            )}
          </nav>
        </div>
      </motion.header>

      <main className="flex-1 flex flex-col items-center w-full relative z-10">
        
        {/* === HERO SECTION === */}
        <section className="w-full pt-32 pb-12 flex flex-col justify-center items-center relative min-h-[90vh]">
          <div className="container px-4 md:px-6 text-center flex flex-col items-center">
            
            {/* Decorative 3D ring */}
            <div className="absolute top-[20%] left-1/2 -translate-x-1/2 w-[500px] h-[500px] pointer-events-none opacity-[0.08]">
              <div
                className="w-full h-full rounded-full border-2 border-indigo-400"
                style={{ animation: "hero-ring-spin 15s linear infinite" }}
              />
              <div
                className="absolute inset-8 rounded-full border border-purple-400"
                style={{ animation: "hero-ring-spin 20s linear infinite reverse" }}
              />
            </div>
            
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-md px-4 py-1.5 text-sm font-medium text-indigo-300 mb-4 glow-border"
            >
              <span className="flex h-2 w-2 rounded-full bg-indigo-400 mr-2 animate-pulse" />
              The new standard for competitive intel
            </motion.div>

            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-[84px] font-extrabold tracking-tight leading-[1.05] mb-4 max-w-4xl">
              <motion.span 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="inline-block"
              >
                Automate your
              </motion.span>
              <br className="hidden sm:block" />
              <motion.span 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 inline-block" 
                style={{ backgroundSize: "200% auto", animation: "glow-line 4s ease-in-out infinite" }}
              >
                Competitive Intelligence.
              </motion.span>
            </h1>
            
            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 1.2 }}
              className="mx-auto max-w-[650px] text-slate-400 md:text-xl mb-8 leading-relaxed font-medium"
            >
              Stop manually tracking competitors. IntelScout autonomously scrapes websites, press releases, and job boards to synthesize real-time insights using AI.
            </motion.p>
            
            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 1.5 }}
              className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto justify-center mb-8"
            >
              <motion.div 
                whileHover={{ scale: 1.05, y: -3 }} 
                whileTap={{ scale: 0.95 }}
                className="relative group"
              >
                {/* Pulsing glow ring behind button */}
                <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full opacity-40 blur-lg group-hover:opacity-60 transition-opacity animate-pulse-glow" />
                {userId ? (
                  <button 
                    onClick={() => setIsDashboardOpen(true)}
                    className="relative inline-flex items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 px-10 py-4 text-base font-semibold text-white transition-all shadow-2xl shadow-indigo-500/20 cursor-pointer w-full sm:w-auto"
                  >
                    Launch Platform
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </button>
                ) : (
                  <SignInButton mode="modal">
                    <button className="relative inline-flex items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 px-10 py-4 text-base font-semibold text-white transition-all shadow-2xl shadow-indigo-500/20 cursor-pointer w-full sm:w-auto">
                      Launch Platform
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </button>
                  </SignInButton>
                )}
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* === FEATURES SECTION === */}
        <section id="features" className="w-full pt-4 pb-16 relative z-10">
          <div className="container px-4 md:px-6 mx-auto max-w-6xl">
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-10"
            >
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                Built for the <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">obsessed</span>
              </h2>
              <p className="text-slate-400 max-w-xl mx-auto text-lg">
                Every feature is designed to give you an unfair advantage.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 perspective-container">
              
              <AnimatedCard className="glass-card p-8 md:p-10" delay={0}>
                <div className="w-14 h-14 bg-gradient-to-br from-indigo-500/20 to-indigo-500/5 rounded-2xl flex items-center justify-center mb-8 border border-indigo-500/20 text-indigo-400">
                  <Globe className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Autonomous Web Scraping</h3>
                <p className="text-slate-400 leading-relaxed">Our headless browsers bypass anti-bot protections to scrape dynamic JS-rendered competitor sites, pricing pages, and job boards automatically.</p>
              </AnimatedCard>

              <AnimatedCard className="glass-card p-8 md:p-10" delay={0.1} glowColor="139, 92, 246">
                <div className="w-14 h-14 bg-gradient-to-br from-violet-500/20 to-violet-500/5 rounded-2xl flex items-center justify-center mb-8 border border-violet-500/20 text-violet-400">
                  <Zap className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">LLM Synthesis</h3>
                <p className="text-slate-400 leading-relaxed">We don&apos;t just dump raw data. Our AI models synthesize complex competitor changes into 1-sentence actionable insights for your team.</p>
              </AnimatedCard>

              <AnimatedCard className="glass-card p-8 md:p-10" delay={0.2} glowColor="34, 211, 238">
                <div className="w-14 h-14 bg-gradient-to-br from-cyan-500/20 to-cyan-500/5 rounded-2xl flex items-center justify-center mb-8 border border-cyan-500/20 text-cyan-400">
                  <Activity className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Live Timelines</h3>
                <p className="text-slate-400 leading-relaxed">View chronological feeds of competitor launches, feature updates, and messaging pivots in one centralized, real-time dashboard.</p>
              </AnimatedCard>

              <AnimatedCard className="glass-card p-8 md:p-10" delay={0.3} glowColor="236, 72, 153">
                <div className="w-14 h-14 bg-gradient-to-br from-pink-500/20 to-pink-500/5 rounded-2xl flex items-center justify-center mb-8 border border-pink-500/20 text-pink-400">
                  <Shield className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3">Instant Battlecards</h3>
                <p className="text-slate-400 leading-relaxed">Generate PDF-ready battlecards for your sales team in seconds. Automatically updated whenever a competitor changes their positioning.</p>
              </AnimatedCard>
            </div>
          </div>
        </section>
        
        {/* === FOOTER CTA === */}
        <motion.section
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="w-full py-16 z-10"
        >
          <div className="container px-4 text-center mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">Stop guessing. Start knowing.</h2>
            <p className="text-slate-400 mb-8 max-w-xl mx-auto text-lg font-medium">
              Join the elite product teams using IntelScout to dominate their market.
            </p>
            <motion.div whileHover={{ scale: 1.05, y: -3 }} whileTap={{ scale: 0.95 }}>
              {userId ? (
                <button onClick={() => setIsDashboardOpen(true)} className="inline-flex items-center justify-center rounded-full bg-white px-8 py-4 text-base font-semibold text-black transition-all hover:bg-slate-200 shadow-lg shadow-white/5 cursor-pointer">
                  Launch Dashboard
                </button>
              ) : (
                <SignInButton mode="modal">
                  <button className="inline-flex items-center justify-center rounded-full bg-white px-8 py-4 text-base font-semibold text-black transition-all hover:bg-slate-200 shadow-lg shadow-white/5 cursor-pointer">
                    Get Started for Free
                  </button>
                </SignInButton>
              )}
            </motion.div>
          </div>
        </motion.section>
      </main>

      {/* === FOOTER === */}
      <motion.footer
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="border-t border-white/[0.06] py-8 w-full flex justify-center z-10 relative"
      >
        <div className="container px-4 md:px-6 flex flex-col sm:flex-row justify-between items-center mx-auto">
          <div className="flex items-center gap-2 mb-4 sm:mb-0">
            <Zap className="h-4 w-4 text-slate-600" fill="currentColor" />
            <p className="text-sm font-medium text-slate-600">© 2026 IntelScout Inc.</p>
          </div>
          <nav className="flex gap-6">
            <Link href="https://github.com/rishabhsingh8445" target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-slate-600 hover:text-slate-300 transition-colors">GitHub</Link>
          </nav>
        </div>
      </motion.footer>

      {/* === DASHBOARD MODAL === */}
      <AnimatePresence>
        {isDashboardOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-md"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.95, y: 10, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="relative w-full max-w-[1800px] h-full max-h-[95vh] rounded-[2rem] overflow-hidden shadow-2xl flex flex-col bg-[#030014] border border-white/10"
            >
              <div className="absolute top-4 right-4 z-[999]">
                <button 
                  onClick={() => setIsDashboardOpen(false)}
                  className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 flex items-center justify-center text-white transition-colors backdrop-blur-md cursor-pointer shadow-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <iframe 
                src="/dashboard" 
                className="w-full h-full border-none bg-transparent flex-1"
                title="IntelScout Dashboard"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
