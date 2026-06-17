"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { LayoutDashboard, Users, Lightbulb, Shield, Grid, Search, Zap, AlertTriangle } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const tabs = [
    { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Competitors", href: "/dashboard/competitors", icon: Users },
    { name: "Insights", href: "/dashboard/insights", icon: Lightbulb },
    { name: "Battlecards", href: "/dashboard/battlecards", icon: Shield },
    { name: "Alerts", href: "/dashboard/alerts", icon: AlertTriangle },
    { name: "Matrix", href: "/dashboard/matrix", icon: Grid },
  ];

  return (
    <div className="min-h-screen bg-[#030014] text-white flex flex-col font-sans selection:bg-indigo-500/30 print:bg-white print:text-black">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#030014]/80 backdrop-blur-xl px-6 py-4 flex items-center justify-between print:hidden">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/25 relative overflow-hidden">
              <Zap className="h-4 w-4 text-white relative z-10" fill="currentColor" />
            </div>
            <span className="font-bold text-lg tracking-tight text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-indigo-400 group-hover:to-cyan-400 transition-all">IntelScout</span>
          </Link>
          <nav className="hidden md:flex items-center gap-1 p-1 bg-white/[0.02] border border-white/5 rounded-full">
            {tabs.map((tab) => {
              const isActive = pathname === tab.href;
              return (
                <Link key={tab.name} href={tab.href} className="relative px-4 py-2 rounded-full group">
                  {isActive && (
                    <motion.div
                      layoutId="dashboardTab"
                      className="absolute inset-0 bg-white/10 rounded-full border border-white/10"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                  <div className={`flex items-center gap-2 relative z-10 transition-colors ${isActive ? "text-white font-semibold" : "text-slate-400 group-hover:text-slate-200"}`}>
                    <tab.icon className="w-4 h-4" />
                    <span className="text-sm">{tab.name}</span>
                  </div>
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center mr-12">
          <UserButton 
            showName={true} 
            appearance={{ 
              elements: { 
                userButtonOuterIdentifier: "!text-white !font-bold !text-lg",
                userButtonAvatarBox: "w-8 h-8",
                userButtonBox: "!flex-row-reverse !gap-1"
              } 
            }} 
          />
        </div>
      </header>
      
      {/* Background glow effects for dashboard */}
      <div className="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0 print:hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[50%] bg-purple-500/20 rounded-full blur-[120px]" />
      </div>

      <main className="flex-1 p-6 lg:p-8 max-w-[1600px] mx-auto w-full relative z-10">
        {children}
      </main>
    </div>
  );
}
