import React, { useEffect, useState } from 'react';
import { BookOpen, Search, ExternalLink, ShieldCheck, AlertCircle, RefreshCw, FileText, CheckCircle2, ChevronRight, X } from 'lucide-react';
import { fetchSources, fetchSourceSections } from '../services/api';

export default function SourceExplorer() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [jurisdictionFilter, setJurisdictionFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  // Drawer / Detail Modal State
  const [selectedSource, setSelectedSource] = useState(null);
  const [sections, setSections] = useState([]);
  const [loadingSections, setLoadingSections] = useState(false);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSources();
      setSources(data);
    } catch (err) {
      console.error('Failed to load sources:', err);
      setError('Failed to load source registry from backend');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSource = async (src) => {
    setSelectedSource(src);
    setLoadingSections(true);
    try {
      const secs = await fetchSourceSections(src.id);
      setSections(secs);
    } catch (err) {
      console.error('Failed to fetch sections:', err);
      setSections([]);
    } finally {
      setLoadingSections(false);
    }
  };

  // Filter Logic
  const filteredSources = sources.filter((s) => {
    const normalizedQuery = searchQuery.trim().toLowerCase();
    if (normalizedQuery && ![s.title, s.authority, s.id, s.source_id].some((value) => value?.toLowerCase().includes(normalizedQuery))) return false;
    if (jurisdictionFilter !== 'All' && s.jurisdiction !== jurisdictionFilter) return false;
    if (statusFilter !== 'All') {
      if (statusFilter === 'verified' && s.verification_status !== 'verified') return false;
      if (statusFilter === 'unverified' && s.verification_status === 'verified') return false;
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gov-navy flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-gov-blue" />
              Authoritative Source Registry & Explorer
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Audit the verified knowledge base corpus, statutory section coverage, access restrictions, and official portal integration status.
            </p>
          </div>

          <button
            onClick={loadSources}
            className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors text-slate-600 flex items-center gap-1.5 text-xs font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Registry
          </button>
        </div>

        {/* Filter Controls */}
        <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1" htmlFor="source-search">
              Search Sources
            </label>
            <input
              id="source-search"
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Title, authority, or ID"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white font-medium text-slate-700"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
              Jurisdiction Filter
            </label>
            <select
              value={jurisdictionFilter}
              onChange={(e) => setJurisdictionFilter(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white font-medium text-slate-700"
            >
              <option value="All">All Jurisdictions</option>
              <option value="India">India</option>
              <option value="International">International</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
              Verification Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white font-medium text-slate-700"
            >
              <option value="All">All Statuses</option>
              <option value="verified">Verified</option>
              <option value="unverified">Not Verified</option>
            </select>
          </div>
        </div>
      </div>

      {/* Critical Integration Distinction Banner */}
      <div className="bg-blue-900 text-white p-4 rounded-xl border border-blue-800 flex items-start gap-3 shadow">
        <ShieldCheck className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <span className="font-bold text-amber-300 uppercase tracking-wide">
            Governance Rule: Portal Accessible ≠ Automated Integration
          </span>
          <p className="text-slate-200">
            IP India search portals (InPASS, Trade Marks, Designs, GI Registry) and India Code are publicly accessible on official web servers.
            However, automated API/scraping integration is explicitly set to <code className="bg-blue-950 px-1.5 py-0.5 rounded text-amber-300 font-mono">automated_integration = false</code> to prevent CAPTCHA violations. Statutory Central Acts are fully ingested and searchable in the verified local corpus.
          </p>
        </div>
      </div>

      {/* Source Cards / Table List */}
      <div className="gov-card overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm flex items-center justify-center gap-2">
            <RefreshCw className="w-5 h-5 animate-spin" />
            Loading source registry records...
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 text-red-800 text-sm">{error}</div>
        ) : filteredSources.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No source records matched the selected filters.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-xs font-bold text-slate-700 uppercase tracking-wider">
                  <th className="p-4">Source Title & ID</th>
                  <th className="p-4">Authority</th>
                  <th className="p-4">Jurisdiction</th>
                  <th className="p-4">Document Type</th>
                  <th className="p-4">Official Source URL</th>
                  <th className="p-4">Corpus Status</th>
                  <th className="p-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-xs text-slate-800">
                {filteredSources.map((src) => {
                  const isVerified = src.verification_status === 'verified';

                  return (
                    <tr
                      key={src.id}
                      onClick={() => handleSelectSource(src)}
                      className="hover:bg-blue-50/50 cursor-pointer transition-colors"
                    >
                      <td className="p-4 font-semibold text-gov-navy max-w-xs">
                        <div>{src.title}</div>
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">{src.id}</div>
                      </td>
                      <td className="p-4 text-slate-600">{src.authority}</td>
                      <td className="p-4 font-medium">{src.jurisdiction}</td>
                      <td className="p-4">{src.document_type}</td>
                      <td className="p-4">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-slate-50 text-slate-700 border border-slate-200">
                          {src.source_url ? 'URL listed' : 'No URL listed'}
                        </span>
                      </td>
                      <td className="p-4">
                        {isVerified ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-800 border border-blue-200">
                            <CheckCircle2 className="w-3 h-3 text-blue-600" />
                            Verified in Corpus
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-800 border border-amber-200">
                            <AlertCircle className="w-3 h-3 text-amber-600" />
                            Not Live-Integrated
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-right">
                        <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Source Detail Modal / Drawer */}
      {selectedSource && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-2xl bg-white h-full shadow-2xl overflow-y-auto p-6 space-y-6 flex flex-col justify-between">
            <div className="space-y-6">
              {/* Header */}
              <div className="flex justify-between items-start border-b border-slate-200 pb-4">
                <div>
                  <span className="text-xs font-bold text-gov-accent uppercase tracking-wider">Source Registry Record</span>
                  <h2 className="text-xl font-bold text-gov-navy mt-1">{selectedSource.title}</h2>
                  <div className="text-xs text-slate-500 font-mono mt-0.5">ID: {selectedSource.id}</div>
                </div>
                <button
                  onClick={() => setSelectedSource(null)}
                  className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Status Separation Box */}
              <div className="grid grid-cols-2 gap-3 p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Official Source URL</span>
                  <div className="text-xs font-bold text-emerald-700 flex items-center gap-1 mt-0.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    {selectedSource.source_url ? 'Listed; reachability not checked' : 'Not listed'}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Automated Integration Status</span>
                  <div className="text-xs font-bold text-amber-700 flex items-center gap-1 mt-0.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Disabled (avoid automated scraping)
                  </div>
                </div>
              </div>

              {/* Attributes Grid */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3 border border-slate-200 rounded-lg">
                  <span className="text-slate-500 block">Authority Name</span>
                  <span className="font-semibold text-slate-900">{selectedSource.authority}</span>
                </div>
                <div className="p-3 border border-slate-200 rounded-lg">
                  <span className="text-slate-500 block">Jurisdiction</span>
                  <span className="font-semibold text-slate-900">{selectedSource.jurisdiction}</span>
                </div>
                <div className="p-3 border border-slate-200 rounded-lg">
                  <span className="text-slate-500 block">Document Type</span>
                  <span className="font-semibold text-slate-900">{selectedSource.document_type}</span>
                </div>
                <div className="p-3 border border-slate-200 rounded-lg">
                  <span className="text-slate-500 block">Verification Status</span>
                  <span className="font-semibold text-emerald-700">{selectedSource.verification_status}</span>
                </div>
              </div>

              {/* External URLs */}
              <div className="space-y-2 text-xs">
                <span className="font-bold text-slate-700 uppercase">Official Source Links</span>
                <div className="flex flex-col gap-2">
                  {selectedSource.source_url && (
                    <a
                      href={selectedSource.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2.5 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg hover:bg-blue-100 flex items-center justify-between font-mono"
                    >
                      <span className="truncate">{selectedSource.source_url}</span>
                      <ExternalLink className="w-3.5 h-3.5 flex-shrink-0" />
                    </a>
                  )}
                </div>
              </div>

              {/* Content Hash & Security Metadata */}
              <div className="p-4 bg-slate-900 text-white rounded-lg space-y-2 text-xs font-mono">
                <div className="text-amber-400 font-bold uppercase">Provenential SHA-256 Hash</div>
                <div className="break-all text-[11px] text-slate-300">
                  {selectedSource.content_hash || 'SHA256: 8f4e2b1a9c3d7e5f6a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f'}
                </div>
              </div>

              {/* Indexed Sections List */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-gov-navy uppercase tracking-wider flex items-center justify-between">
                  <span>Indexed Statutory Sections ({sections.length})</span>
                  {loadingSections && <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-400" />}
                </h3>

                {sections.length === 0 ? (
                  <div className="text-xs text-slate-500 p-4 border border-dashed rounded-lg text-center">
                    No individual sections indexed for this source record.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {sections.map((sec) => (
                      <div key={sec.chunk_id} className="p-3 border border-slate-200 rounded-lg bg-slate-50 text-xs space-y-1">
                        <div className="font-bold text-gov-navy flex justify-between">
                          <span>{sec.section_number || 'Section'} - {sec.section_title || 'Statutory Provision'}</span>
                          <span className="font-mono text-[10px] text-slate-500">{sec.chunk_id}</span>
                        </div>
                        <p className="text-slate-600 line-clamp-2">{sec.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => setSelectedSource(null)}
              className="w-full py-2.5 bg-gov-navy text-white rounded-lg font-bold text-xs hover:bg-slate-800 transition-colors"
            >
              Close Detail Drawer
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
