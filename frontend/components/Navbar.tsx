"use client";
import React from 'react';
import { Rocket, Github, Menu, X } from 'lucide-react';
import Link from 'next/link';

export default function Navbar() {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Rocket className="w-6 h-6 text-primary" />
            </div>
            <span className="text-xl font-bold tracking-tight text-gradient">FounderSim</span>
          </div>
          
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">Home</Link>
              <Link href="/analyze" className="text-sm font-medium hover:text-primary transition-colors">Analyze</Link>
              <Link href="/about" className="text-sm font-medium hover:text-primary transition-colors">About</Link>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="p-2 hover:bg-white/5 rounded-full transition-colors">
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>

          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="p-2">
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden glass border-t border-white/10">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link href="/" className="block px-3 py-2 text-base font-medium hover:text-primary">Home</Link>
            <Link href="/analyze" className="block px-3 py-2 text-base font-medium hover:text-primary">Analyze</Link>
            <Link href="/about" className="block px-3 py-2 text-base font-medium hover:text-primary">About</Link>
          </div>
        </div>
      )}
    </nav>
  );
}
