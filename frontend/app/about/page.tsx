"use client";
import React from 'react';
import Navbar from '@/components/Navbar';
import { motion } from 'framer-motion';
import { Brain, Cpu, Rocket, Shield, Users, Zap } from 'lucide-react';

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      
      <div className="pt-32 pb-20 max-w-5xl mx-auto px-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl font-black mb-6 tracking-tight">The <span className="text-gradient">Intelligence</span> Behind FounderSim</h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            We've built a multi-agent orchestration layer that simulates an entire venture capital firm 
            and a market research agency in seconds.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center mb-20">
          <div className="space-y-6">
            <h2 className="text-3xl font-bold">How it works</h2>
            <p className="text-slate-400 leading-relaxed">
              FounderSim utilizes the latest in agentic AI. When you submit an idea, eight specialized 
              agents—ranging from Senior Market Analysts to Skeptical Customers—are deployed to 
              stress-test your vision.
            </p>
            <div className="space-y-4">
              <AboutItem 
                icon={<Brain className="w-5 h-5 text-primary" />}
                title="Sarvam AI 105B"
                description="Leveraging high-parameter models for deep reasoning and strategic planning."
              />
              <AboutItem 
                icon={<Cpu className="w-5 h-5 text-primary" />}
                title="Agentic Orchestration"
                description="Agents collaborate, peer-review, and synthesize reports autonomously."
              />
              <AboutItem 
                icon={<Zap className="w-5 h-5 text-primary" />}
                title="Real-time Research"
                description="Live web searching across global startup databases and news."
              />
            </div>
          </div>
          <div className="relative p-8 rounded-3xl glass border-primary/20 aspect-square flex items-center justify-center">
            <div className="absolute inset-0 premium-gradient opacity-10 rounded-3xl" />
            <div className="grid grid-cols-2 gap-4 relative z-10">
              <div className="w-20 h-20 rounded-2xl glass flex items-center justify-center animate-bounce [animation-delay:-0.2s]">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <div className="w-20 h-20 rounded-2xl glass flex items-center justify-center animate-bounce [animation-delay:0.1s]">
                <Users className="w-8 h-8 text-accent" />
              </div>
              <div className="w-20 h-20 rounded-2xl glass flex items-center justify-center animate-bounce [animation-delay:-0.4s]">
                <Rocket className="w-8 h-8 text-rose-500" />
              </div>
              <div className="w-20 h-20 rounded-2xl glass flex items-center justify-center animate-bounce [animation-delay:0.3s]">
                <Brain className="w-8 h-8 text-emerald-500" />
              </div>
            </div>
          </div>
        </div>

        <div className="p-12 rounded-3xl glass text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to test your vision?</h2>
          <p className="text-slate-400 mb-8">Stop guessing. Start building with data-driven confidence.</p>
          <a href="/" className="inline-flex px-8 py-4 rounded-2xl premium-gradient font-bold text-lg hover:scale-105 transition-transform">
            Back to Home
          </a>
        </div>
      </div>
    </main>
  );
}

function AboutItem({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="flex gap-4">
      <div className="mt-1">{icon}</div>
      <div>
        <h4 className="font-bold">{title}</h4>
        <p className="text-sm text-slate-400">{description}</p>
      </div>
    </div>
  );
}
