"use client";
import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import AnalysisForm from '@/components/AnalysisForm';
import ReportView from '@/components/ReportView';
import { analyzeStartup, StartupIdea } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';

export default function AnalyzePage() {
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
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-32 pb-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <AnimatePresence mode="wait">
          {!report ? (
            <div key="form" className="space-y-12">
              <div className="text-center">
                <h1 className="text-4xl font-black mb-4 tracking-tight">Deploy the <span className="text-gradient">Agents</span></h1>
                <p className="text-slate-400">Fill in your startup details to begin the deep research process.</p>
              </div>
              <AnalysisForm onAnalyze={handleAnalyze} isLoading={loading} />
            </div>
          ) : (
            <motion.div
              key="report"
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
    </main>
  );
}
