import React from 'react';
import { Shield, BookOpen, Search, FileCheck, Database, Globe, UserCheck } from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  demoMode,
  setDemoMode,
  confidentialMode,
  setConfidentialMode,
  language,
  setLanguage
}) {
  return (
    <header className="bg-gov-navy text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Emblem & Clean Title */}
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => setActiveTab('dashboard')}
          >
            <div className="bg-gov-accent text-slate-950 p-2 rounded-lg font-bold shadow">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white">
                IP-SAKTI Sahayak
              </h1>
              <p className="text-xs text-slate-300">
                Evidence-Grounded IP & Regulatory Intelligence for Ayurveda
              </p>
            </div>
          </div>

          {/* Clean Navigation Links */}
          <nav className="flex items-center space-x-1">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'dashboard'
                  ? 'bg-blue-900 text-white border border-blue-700 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Database className="w-4 h-4" />
              Dashboard
            </button>

            <button
              onClick={() => setActiveTab('assistant')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'assistant'
                  ? 'bg-blue-900 text-white border border-blue-700 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Search className="w-4 h-4" />
              AI Assistant
            </button>

            <button
              onClick={() => setActiveTab('assessment')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'assessment'
                  ? 'bg-blue-900 text-white border border-blue-700 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <FileCheck className="w-4 h-4" />
              Formulation Assessment
            </button>

            <button
              onClick={() => setActiveTab('explorer')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'explorer'
                  ? 'bg-blue-900 text-white border border-blue-700 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Source Explorer
            </button>

            <button
              onClick={() => setActiveTab('cases')}
              className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                activeTab === 'cases'
                  ? 'bg-blue-900 text-white border border-blue-700 shadow-sm'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              Cases / Human Review
            </button>
          </nav>

          {/* Clean Language Selector */}
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-slate-300" />
            <button
              onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-white transition-colors"
            >
              {language === 'en' ? 'English | हिंदी' : 'हिंदी | English'}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
