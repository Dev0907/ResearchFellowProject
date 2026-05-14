"use client";
import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import AnalysisForm from '@/components/AnalysisForm';
import ReportView from '@/components/ReportView';
import { analyzeStartup, StartupIdea } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Rocket, Shield, Globe, TrendingUp } from 'lucide-react';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (data: StartupIdea) => {
    setLoading(true);
    setReport(null);
    setError(null);
    try {
      const response = await analyzeStartup(data);
      if (response.status === 'success') {
        setReport(response.report);
      } else {
        setError(response.report?.error || 'Analysis failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/30">
      <Navbar />
      
      {/* Hero Section */}
      <div className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full opacity-20 pointer-events-none">
          <div className="absolute top-0 left-0 w-96 h-96 bg-primary/40 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent/40 rounded-full blur-[120px]" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          {!report && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
                <Rocket className="w-4 h-4 text-primary" />
                <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Multi-Agent AI Intelligence</span>
              </div>
              <h1 className="text-6xl md:text-8xl font-black mb-8 tracking-tighter">
                Stress-test your <br />
                <span className="text-gradient">startup vision.</span>
              </h1>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed">
                Our global crew of specialized agents analyzes your idea across countries, 
                competitors, and the next 10 years of market evolution.
              </p>
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {!report ? (
              <AnalysisForm onAnalyze={handleAnalyze} isLoading={loading} />
            ) : (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-left"
              >
                <div className="flex items-center justify-between mb-8 border-b border-white/10 pb-6">
                  <div>
                    <h2 className="text-4xl font-black tracking-tight">Analysis Report</h2>
                    <p className="text-slate-400">Comprehensive breakdown of your startup potential</p>
                  </div>
                  <button 
                    onClick={() => setReport(null)}
                    className="px-6 py-2 rounded-xl glass hover:bg-white/10 transition-colors text-sm font-medium"
                  >
                    New Analysis
                  </button>
                </div>
                <ReportView report={report} />
              </motion.div>
            )}
          </AnimatePresence>

          {error && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-8 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm max-w-xl mx-auto"
            >
              {error}
            </motion.div>
          )}
        </div>
      </div>

      {/* Features Grid - Only show if no report */}
      {!report && !loading && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Globe className="w-6 h-6" />}
              title="Global Scope"
              description="Analyzes startups across USA, India, Europe and Asia in real-time."
            />
            <FeatureCard 
              icon={<TrendingUp className="w-6 h-6" />}
              title="10-Year Outlook"
              description="Strategic projections on how your idea and competitors evolve over a decade."
            />
            <FeatureCard 
              icon={<Shield className="w-6 h-6" />}
              title="Brutal Honesty"
              description="No sugar-coating. Real investor stress-tests and customer skepticism."
            />
          </div>
        </div>
      )}

      <footer className="border-t border-white/5 py-12 text-center text-slate-500 text-sm">
        <p>&copy; 2026 Founder Simulator. Powered by Groq & Tavily.</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-8 rounded-3xl glass border-white/5 hover:border-primary/30 transition-all group">
      <div className="p-3 bg-primary/10 rounded-2xl w-fit mb-6 group-hover:scale-110 transition-transform">
        {React.cloneElement(icon as React.ReactElement, { className: 'w-6 h-6 text-primary' })}
      </div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}
