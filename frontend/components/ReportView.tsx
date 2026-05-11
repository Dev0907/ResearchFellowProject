"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, ScatterChart, Scatter, ZAxis
} from 'recharts';
import { 
  Shield, AlertTriangle, TrendingUp, Users, 
  Zap, Globe, Award, Info, CheckCircle2
} from 'lucide-react';

interface ReportViewProps {
  report: any;
}

const COLORS = ['#6366f1', '#a855f7', '#ec4899', '#f43f5e', '#f59e0b'];

export default function ReportView({ report }: ReportViewProps) {
  if (!report) return null;

  const {
    executive_summary,
    market_opportunity,
    investor_concerns,
    competitive_landscape,
    customer_objections,
    distribution_strategy,
    moat_strength,
    survival_probability,
    brutal_truth,
    success_factors
  } = report;

  // Data for Market Scores Bar Chart
  const marketData = [
    { name: 'Potential', value: market_opportunity?.score || 0 },
    { name: 'Moat', value: moat_strength?.score || 0 },
    { name: 'Survival', value: (survival_probability?.percentage || 0) / 10 },
  ];

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Summary */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-8"
      >
        <div className="lg:col-span-2 p-8 rounded-3xl glass border-primary/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4">
            <Award className="w-12 h-12 text-primary opacity-20" />
          </div>
          <h2 className="text-3xl font-bold mb-4 text-gradient">{report.startup_name}</h2>
          <p className="text-xl text-slate-300 leading-relaxed italic">
            "{executive_summary?.verdict}"
          </p>
          <div className="mt-8 grid grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Biggest Strength</span>
              <p className="mt-1 text-sm">{executive_summary?.biggest_strength}</p>
            </div>
            <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-400">Biggest Weakness</span>
              <p className="mt-1 text-sm">{executive_summary?.biggest_weakness}</p>
            </div>
          </div>
        </div>

        <div className="p-8 rounded-3xl glass flex flex-col items-center justify-center text-center">
          <div className="relative w-48 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { value: survival_probability?.percentage || 0 },
                    { value: 100 - (survival_probability?.percentage || 0) }
                  ]}
                  innerRadius={60}
                  outerRadius={80}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                >
                  <Cell fill="#6366f1" />
                  <Cell fill="rgba(255,255,255,0.05)" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold">{survival_probability?.percentage}%</span>
              <span className="text-xs text-slate-400 uppercase">Survival Prob.</span>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-400 px-4 leading-snug">
            {survival_probability?.reasoning}
          </p>
        </div>
      </motion.div>

      {/* Market & Moat Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="p-8 rounded-3xl glass space-y-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-primary" />
            <h3 className="text-xl font-bold">Market Dynamics</h3>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={marketData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" hide />
                <Tooltip 
                  contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '12px' }}
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {marketData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Timing Assessment:</span>
              <span className="font-medium">{market_opportunity?.timing}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Competitive Intensity:</span>
              <span className="font-medium">{market_opportunity?.competitive_intensity}</span>
            </div>
          </div>
        </div>

        <div className="p-8 rounded-3xl glass space-y-6">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-primary" />
            <h3 className="text-xl font-bold">Defensibility & Moat</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {moat_strength?.moat_types?.map((type: string) => (
              <span key={type} className="px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-xs font-medium text-primary">
                {type}
              </span>
            ))}
          </div>
          <div className="p-4 rounded-2xl bg-white/5 space-y-4">
            <p className="text-sm text-slate-300">
              <span className="font-bold text-white">Outlook:</span> {moat_strength?.time_to_build} to build a defensible moat.
            </p>
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Key Recommendations:</span>
              <ul className="space-y-1">
                {moat_strength?.recommendations?.map((rec: string, i: number) => (
                  <li key={i} className="text-sm flex gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Global Competition */}
      <div className="p-8 rounded-3xl glass">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Globe className="w-6 h-6 text-primary" />
            <h3 className="text-xl font-bold">Global Competitive Landscape</h3>
          </div>
          <span className="text-xs text-slate-400 uppercase">Real-time Data Active</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {competitive_landscape?.direct_competitors?.map((comp: any, i: number) => (
            <motion.div 
              key={i}
              whileHover={{ y: -5 }}
              className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-primary/50 transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <h4 className="font-bold text-lg">{comp.name || comp}</h4>
                {comp.funding && <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded-full">{comp.funding}</span>}
              </div>
              <p className="text-sm text-slate-400 line-clamp-3 mb-4">{comp.description || comp.value_proposition}</p>
              <div className="flex flex-wrap gap-1">
                {comp.features?.slice(0, 3).map((f: string) => (
                  <span key={f} className="text-[9px] px-2 py-0.5 bg-white/5 rounded-md">{f}</span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        
        <div className="mt-8 p-6 rounded-2xl border border-rose-500/20 bg-rose-500/5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-rose-500" />
            <h4 className="font-bold text-rose-500">Biggest Competitive Threat</h4>
          </div>
          <p className="text-sm text-slate-300">{competitive_landscape?.biggest_threat}</p>
        </div>
      </div>

      {/* Investor & Customer Reality */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <h3 className="text-xl font-bold flex items-center gap-3 px-4">
            <Zap className="w-6 h-6 text-amber-500" />
            Investor Hardball
          </h3>
          <div className="space-y-4">
            {investor_concerns?.map((item: any, i: number) => (
              <div key={i} className="p-6 rounded-2xl glass border-white/5">
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-bold">{item.concern}</h5>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                    item.severity === 'high' ? 'bg-rose-500/20 text-rose-400' : 
                    item.severity === 'medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {item.severity} severity
                  </span>
                </div>
                <p className="text-sm text-slate-400 mb-3">{item.explanation}</p>
                <div className="text-xs text-primary font-medium flex gap-2">
                  <span className="shrink-0 font-bold uppercase">Fix:</span>
                  {item.how_to_address}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <h3 className="text-xl font-bold flex items-center gap-3 px-4">
            <Users className="w-6 h-6 text-primary" />
            Customer Skepticism
          </h3>
          <div className="space-y-4">
            {customer_objections?.map((item: any, i: number) => (
              <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/5">
                <h5 className="font-bold mb-1">"{item.objection}"</h5>
                <p className="text-sm text-slate-400 mb-3 italic">{item.category}</p>
                <div className="text-sm text-slate-200 bg-white/5 p-3 rounded-xl border border-white/5">
                  {item.how_to_address}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Brutal Truths & Success Factors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="p-8 rounded-3xl bg-rose-500/10 border border-rose-500/20">
          <h3 className="text-xl font-bold text-rose-400 mb-6 flex items-center gap-3">
            <AlertTriangle className="w-6 h-6" />
            The Brutal Truth
          </h3>
          <ul className="space-y-4">
            {brutal_truth?.map((truth: string, i: number) => (
              <li key={i} className="flex gap-4 items-start text-slate-300">
                <span className="w-6 h-6 rounded-full bg-rose-500/20 flex items-center justify-center shrink-0 text-rose-500 font-bold text-xs">
                  {i+1}
                </span>
                {truth}
              </li>
            ))}
          </ul>
        </div>

        <div className="p-8 rounded-3xl bg-emerald-500/10 border border-emerald-500/20">
          <h3 className="text-xl font-bold text-emerald-400 mb-6 flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6" />
            Critical Success Factors
          </h3>
          <ul className="space-y-4">
            {success_factors?.map((factor: string, i: number) => (
              <li key={i} className="flex gap-4 items-start text-slate-300">
                <span className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 text-emerald-400 font-bold text-xs">
                  {i+1}
                </span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
