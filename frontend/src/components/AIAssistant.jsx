import React, { useState } from 'react';
import { Search, ShieldAlert, CheckCircle2, AlertTriangle, ExternalLink, Lock, FileText, Globe, ArrowRight, RefreshCw } from 'lucide-react';
import { sendQuery } from '../services/api';

export default function AIAssistant({
  initialQuery = "",
  language,
  setLanguage,
  confidentialMode,
  onOpenCitationModal
}) {
  const [queryText, setQueryText] = useState(initialQuery);
  const [jurisdiction, setJurisdiction] = useState('India');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!queryText.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const payload = {
        query: queryText,
        jurisdiction: jurisdiction,
        language: language,
        confidential_mode: confidentialMode
      };
      const res = await sendQuery(payload);
      setResponse(res);
    } catch (err) {
      console.error('Error in query submission:', err);
      setError(err.message || 'Error communicating with IP-SAKTI backend');
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "I developed an Ayurvedic formulation containing Ashwagandha and Brahmi. Can I patent it?",
    "Does TKDL contain the exact formulation Ashwagandha + Brahmi + Shatavari?",
    "I am an Indian company using a biological resource for commercial purposes. Do I need ABS compliance?",
    "Do foreign companies require National Biodiversity Authority (NBA) approval under the Biological Diversity Act?"
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-gov-navy flex items-center gap-2">
          <Search className="w-6 h-6 text-gov-blue" />
          AI Legal & Regulatory Assistant
        </h1>
        <p className="text-sm text-slate-600 mt-1">
          Query the verified knowledge base for evidence-grounded legal and regulatory guidance on Ayurveda IP, Traditional Knowledge, and ABS compliance.
        </p>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="What do you need to know? (e.g. Can I patent a classical Ayurvedic polyherbal formulation?)"
                className="w-full pl-4 pr-12 py-3 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-gov-blue focus:border-gov-blue shadow-sm"
              />
            </div>
            <select
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-3 text-sm bg-white font-medium text-slate-700 shadow-sm"
            >
              <option value="India">Jurisdiction: India</option>
              <option value="International">Jurisdiction: International</option>
              <option value="All">Jurisdiction: All</option>
            </select>
            <button
              type="submit"
              disabled={loading || !queryText.trim()}
              className="bg-gov-navy hover:bg-slate-800 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium text-sm transition-all shadow flex items-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Retrieving Evidence...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Analyze
                </>
              )}
            </button>
          </div>

          {/* Sample Question Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs font-semibold text-slate-500">Sample Queries:</span>
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQueryText(q);
                }}
                className="text-xs bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-800 border border-slate-200 rounded-md px-2.5 py-1 transition-colors text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Response Card */}
      {response && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden divide-y divide-slate-100">
          {/* Status Header */}
          <div className="p-6 bg-slate-50 flex justify-between items-center border-b border-slate-200">
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Target Jurisdiction:</span>
              <span className="text-sm font-bold text-gov-navy bg-white border border-slate-300 px-3 py-0.5 rounded">
                {response.jurisdiction}
              </span>
            </div>

            <div className="flex items-center gap-3">
              {response.confidence === 'evidence_supported' && (
                <span className="gov-badge-verified">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Evidence Status: Citations Verified
                </span>
              )}

              {response.confidence === 'insufficient_evidence' && (
                <span className="gov-badge-warning">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Evidence Status: INSUFFICIENT EVIDENCE
                </span>
              )}

              {response.needs_review && (
                <span className="gov-badge-restricted">
                  <Lock className="w-4 h-4 text-purple-600" />
                  Review Status: Restricted / Needs Review
                </span>
              )}
            </div>
          </div>

          {/* Main Answer Section */}
          <div className="p-6 space-y-4">
            <h2 className="text-base font-bold text-gov-navy uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-5 h-5 text-gov-blue" />
              Verified Legal Assessment & Answer
            </h2>

            {/* Controlled Abstention Banner */}
            {response.confidence === 'insufficient_evidence' && (
              <div className="bg-amber-50 border-l-4 border-l-amber-500 p-4 rounded-r-lg text-amber-900 text-sm space-y-1">
                <div className="font-bold flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  INSUFFICIENT EVIDENCE ABSTENTION NOTICE
                </div>
                <p>{response.answer}</p>
              </div>
            )}

            {/* Evidence Supported Answer */}
            {response.confidence !== 'insufficient_evidence' && (
              <div className="text-sm text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
                {response.answer}
              </div>
            )}
          </div>

          {/* Structured Claims & Citations List */}
          {response.claims && response.claims.length > 0 && (
            <div className="p-6 space-y-4">
              <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider">
                Verifiable Claims & Mapped Source Chunks
              </h3>
              <div className="space-y-3">
                {response.claims.map((claim, idx) => (
                  <div key={idx} className="p-4 border border-slate-200 rounded-lg bg-white space-y-2">
                    <p className="text-sm font-medium text-slate-900">"{claim.text}"</p>
                    <div className="flex flex-wrap items-center gap-2 pt-1">
                      <span className="text-xs text-slate-500 font-semibold">Supporting Chunk IDs:</span>
                      {claim.source_chunks.map((chunkId) => {
                        const cit = response.citations.find((c) => c.chunk_id === chunkId);
                        return (
                          <button
                            key={chunkId}
                            onClick={() => cit && onOpenCitationModal(cit)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono bg-blue-50 hover:bg-blue-100 text-blue-800 border border-blue-200 transition-colors"
                          >
                            <span>{chunkId}</span>
                            <ExternalLink className="w-3 h-3 text-blue-600" />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Citations Summary Footer */}
          {response.citations && response.citations.length > 0 && (
            <div className="p-6 bg-slate-50 space-y-3">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Authoritative Citations & Source Origins
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {response.citations.map((c) => (
                  <div
                    key={c.chunk_id}
                    onClick={() => onOpenCitationModal(c)}
                    className="p-3 border border-slate-200 rounded-lg bg-white hover:border-blue-400 cursor-pointer transition-colors flex justify-between items-center"
                  >
                    <div>
                      <div className="text-xs font-bold text-gov-navy">{c.document_title}</div>
                      <div className="text-xs text-slate-500">{c.authority} • {c.section || 'General'}</div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-400" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statutory Disclaimer */}
          <div className="p-4 bg-slate-100 text-xs text-slate-500 border-t border-slate-200 text-center font-medium">
            IP-SAKTI Sahayak provides evidence-grounded informational support and is not a substitute for professional legal or regulatory advice.
          </div>
        </div>
      )}
    </div>
  );
}
