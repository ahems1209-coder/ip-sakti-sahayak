import React, { useEffect, useState } from 'react';
import { Search, FileCheck, BookOpen, ShieldCheck, Database, AlertCircle, Lock, ArrowRight, CheckCircle2 } from 'lucide-react';
import { fetchSources } from '../services/api';

export default function Dashboard({ setActiveTab, onSelectDemoQuery }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSources()
      .then((data) => {
        setSources(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load sources:', err);
        setLoading(false);
      });
  }, []);

  const ingestedCount = sources.filter((s) => s.ingestion_status === 'ingested' || s.verification_status === 'verified').length;

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Header Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm relative overflow-hidden">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-medium mb-4">
            <ShieldCheck className="w-4 h-4 text-blue-600" />
            <span>Authoritative Decision-Support Platform</span>
          </div>
          <h1 className="text-3xl font-bold text-gov-navy tracking-tight mb-2">
            IP-SAKTI Sahayak
          </h1>
          <p className="text-lg font-medium text-gov-slate mb-3">
            Evidence-grounded IP & Regulatory Intelligence for Ayurveda
          </p>
          <p className="text-sm text-slate-600 leading-relaxed mb-6">
            Find relevant IP, traditional-knowledge and regulatory evidence from an authoritative, traceable corpus.
            Every substantive conclusion is strictly mapped to verified legal section chunks with zero artificial hallucination.
          </p>

          {/* Quick Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setActiveTab('assistant')}
              className="bg-gov-navy hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2 shadow-sm"
            >
              <Search className="w-4 h-4" />
              Ask IP-SAKTI
            </button>
            <button
              onClick={() => setActiveTab('assessment')}
              className="bg-gov-accent hover:bg-amber-600 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2 shadow-sm"
            >
              <FileCheck className="w-4 h-4" />
              Assess Formulation
            </button>
            <button
              onClick={() => setActiveTab('explorer')}
              className="bg-white hover:bg-slate-50 text-gov-navy border border-slate-300 px-5 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2"
            >
              <BookOpen className="w-4 h-4" />
              Explore Sources
            </button>
          </div>
        </div>
      </div>

      {/* Backend Source Coverage Summary Cards */}
      <div>
        <h2 className="text-lg font-bold text-gov-navy mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-700" />
          Authoritative Corpus Coverage Summary
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="gov-card p-5 border-l-4 border-l-emerald-600">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Ingested & Searchable</span>
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            </div>
            <div className="text-2xl font-bold text-gov-navy">{loading ? '...' : ingestedCount}</div>
            <p className="text-xs text-slate-500 mt-1">Verified Central Acts & Treaties indexed with structural chunking</p>
          </div>

          <div className="gov-card p-5 border-l-4 border-l-amber-500">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Live Portal Integration</span>
              <AlertCircle className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-lg font-bold text-gov-navy">Disabled</div>
            <p className="text-xs text-slate-500 mt-1">Automated portal access is off; source URLs remain available in the registry</p>
          </div>

          <div className="gov-card p-5 border-l-4 border-l-purple-600">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Restricted Knowledge</span>
              <Lock className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-lg font-bold text-gov-navy">TKDL</div>
            <p className="text-xs text-slate-500 mt-1">Detailed formulation records require authorized access and are not searchable here</p>
          </div>

          <div className="gov-card p-5 border-l-4 border-l-slate-400">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Insufficient Evidence Policy</span>
              <ShieldCheck className="w-5 h-5 text-slate-600" />
            </div>
            <div className="text-sm font-bold text-gov-navy">Strict Abstention</div>
            <p className="text-xs text-slate-500 mt-1">Zero legal hallucination; returns explicit warning when corpus lacks evidence</p>
          </div>
        </div>
      </div>

      {/* Sample Legal Queries Section */}
      <div className="gov-card p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-base font-bold text-gov-navy">Sample Legal & Regulatory Queries</h3>
            <p className="text-xs text-slate-500">Run pre-indexed queries grounded strictly in verified corpus sections</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            onClick={() => onSelectDemoQuery("Is a classical Ayurvedic polyherbal formulation patentable under Section 3(p) or 3(e) of the Indian Patents Act, 1970?")}
            className="p-4 border border-slate-200 rounded-lg hover:border-gov-accent cursor-pointer transition-all bg-slate-50 hover:bg-white group"
          >
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs font-semibold text-blue-800">Patents & Traditional Knowledge</span>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-gov-accent transition-colors" />
            </div>
            <p className="text-sm font-medium text-gov-navy">Ayurvedic Formulation Patentability (Neem & Haldi)</p>
            <p className="text-xs text-slate-500 mt-1">Section 3(p) & 3(e) Patent Act 1970 analysis</p>
          </div>

          <div
            onClick={() => onSelectDemoQuery("Are foreign companies required to obtain National Biodiversity Authority (NBA) approval before applying for IP on Indian bio-resources?")}
            className="p-4 border border-slate-200 rounded-lg hover:border-gov-accent cursor-pointer transition-all bg-slate-50 hover:bg-white group"
          >
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs font-semibold text-emerald-800">Biodiversity & ABS</span>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-gov-accent transition-colors" />
            </div>
            <p className="text-sm font-medium text-gov-navy">National Biodiversity Authority (NBA) ABS Rules</p>
            <p className="text-xs text-slate-500 mt-1">Section 3 & Section 6 Biological Diversity Act 2002 analysis</p>
          </div>
        </div>
      </div>
    </div>
  );
}
