"use client";
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Loader2, Globe, Users, Target, Info, Rocket } from 'lucide-react';
import { StartupIdea } from '@/lib/api';

interface AnalysisFormProps {
  onAnalyze: (data: StartupIdea) => void;
  isLoading: boolean;
}

export default function AnalysisForm({ onAnalyze, isLoading }: AnalysisFormProps) {
  const [loadingStep, setLoadingStep] = useState(0);
  const steps = [
    "Deploying Global Market Analyst...",
    "Tier-1 VC Partner reviewing vision...",
    "Competitor Mapper scanning markets...",
    "Customer Skeptic stress-testing...",
    "Distribution Strategist mapping GTM...",
    "Moat Analyzer evaluating defensibility...",
    "UX & Brand Director defining identity...",
    "Strategic Synthesizer finalising report..."
  ];

  React.useEffect(() => {
    let interval: any;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % steps.length);
      }, 3000);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const [formData, setFormData] = useState<StartupIdea>({
    idea: '',
    problem: '',
    audience: '',
    website: '',
    startup_name: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.idea) {
      onAnalyze(formData);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto p-8 rounded-3xl glass shadow-2xl relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
        <Sparkles className="w-32 h-32 text-primary" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-2 col-span-full">
            <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              What's your startup idea?
            </label>
            <textarea
              required
              placeholder="e.g. An AI-powered platform for rural farmers in India to predict crop yields and connect with buyers directly..."
              className="w-full h-32 bg-white/5 border border-white/10 rounded-2xl p-4 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none text-lg"
              value={formData.idea}
              onChange={(e) => setFormData({...formData, idea: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" />
              Specific Problem
            </label>
            <input
              type="text"
              placeholder="What pain point are you solving?"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              value={formData.problem}
              onChange={(e) => setFormData({...formData, problem: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Users className="w-4 h-4 text-primary" />
              Target Audience
            </label>
            <input
              type="text"
              placeholder="Who are your customers?"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              value={formData.audience}
              onChange={(e) => setFormData({...formData, audience: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Globe className="w-4 h-4 text-primary" />
              Website (Optional)
            </label>
            <input
              type="text"
              placeholder="https://yourstartup.com"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              value={formData.website}
              onChange={(e) => setFormData({...formData, website: e.target.value})}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Info className="w-4 h-4 text-primary" />
              Startup Name
            </label>
            <input
              type="text"
              placeholder="What do you call it?"
              className="w-full bg-white/5 border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              value={formData.startup_name}
              onChange={(e) => setFormData({...formData, startup_name: e.target.value})}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 rounded-2xl premium-gradient font-bold text-lg hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center gap-3"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>{steps[loadingStep]}</span>
            </>
          ) : (
            <>
              <Rocket className="w-5 h-5" />
              <span>Begin Deep Analysis</span>
            </>
          )}
        </button>
      </form>
    </motion.div>
  );
}
