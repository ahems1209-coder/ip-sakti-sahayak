import React from 'react';
import { X, ExternalLink, ShieldCheck, CheckCircle2, FileText, Lock } from 'lucide-react';

export default function CitationModal({ citation, onClose }) {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-xl w-full border border-slate-200 shadow-2xl overflow-hidden animate-fadeIn">
        {/* Modal Header */}
        <div className="bg-gov-navy text-white p-5 flex justify-between items-start">
          <div className="space-y-1">
            <span className="text-xs font-bold text-gov-accent uppercase tracking-wider">Verified Source Citation</span>
            <h3 className="text-lg font-bold">{citation.document_title || 'Legal Source Document'}</h3>
            <div className="text-xs text-slate-300 font-mono">Chunk ID: {citation.chunk_id}</div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 text-xs">
          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Verification Status: {citation.verification_status || 'verified'}
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-50 text-blue-800 border border-blue-200 font-semibold">
              Jurisdiction: {citation.jurisdiction || 'India'}
            </span>
          </div>

          {/* Details Table */}
          <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <span className="text-slate-500 font-bold block">Authority</span>
              <span className="text-slate-900 font-semibold">{citation.authority || 'Authority not specified'}</span>
            </div>
            <div>
              <span className="text-slate-500 font-bold block">Section / Provision</span>
              <span className="text-slate-900 font-semibold">{citation.section || 'Statutory Provision'}</span>
            </div>
            {citation.version_date && (
              <div>
                <span className="text-slate-500 font-bold block">Version Date</span>
                <span className="text-slate-900 font-mono">{citation.version_date}</span>
              </div>
            )}
          </div>

          {/* Official URL */}
          {citation.official_source_url && (
            <div className="space-y-1">
              <span className="font-bold text-slate-700 uppercase">Official Source Web Reference</span>
              <a
                href={citation.official_source_url}
                target="_blank"
                rel="noreferrer"
                className="p-2.5 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg hover:bg-blue-100 flex items-center justify-between font-mono break-all"
              >
                <span>{citation.official_source_url}</span>
                <ExternalLink className="w-4 h-4 flex-shrink-0 ml-2 text-blue-600" />
              </a>
            </div>
          )}

          {/* Statutory Excerpt if available */}
          {citation.excerpt && (
            <div className="space-y-1">
              <span className="font-bold text-slate-700 uppercase">Exact Statutory Excerpt</span>
              <div className="p-3 bg-slate-900 text-slate-200 rounded-lg font-mono text-[11px] leading-relaxed max-h-40 overflow-y-auto">
                {citation.excerpt}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-100 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gov-navy text-white rounded-lg text-xs font-bold hover:bg-slate-800 transition-colors"
          >
            Close Citation
          </button>
        </div>
      </div>
    </div>
  );
}
