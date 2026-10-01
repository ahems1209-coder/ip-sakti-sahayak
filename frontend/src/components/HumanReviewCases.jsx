import React, { useEffect, useState } from 'react';
import { UserCheck, RefreshCw, AlertCircle, FileText, CheckCircle2, Clock } from 'lucide-react';
import { fetchHumanReviewCases } from '../services/api';

export default function HumanReviewCases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHumanReviewCases();
      setCases(data);
    } catch (err) {
      console.error('Failed to load review cases:', err);
      setError('Failed to load human review cases from backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gov-navy flex items-center gap-2">
            <UserCheck className="w-6 h-6 text-gov-blue" />
            Escalated Cases & Human Review Queue
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Review escalated complex legal queries, missing evidence profiles, and expert facilitator assignments.
          </p>
        </div>

        <button
          onClick={loadCases}
          className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors text-slate-600 flex items-center gap-1.5 text-xs font-medium"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Queue
        </button>
      </div>

      {/* Cases List */}
      <div className="gov-card overflow-hidden p-6 space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm flex items-center justify-center gap-2">
            <RefreshCw className="w-5 h-5 animate-spin" />
            Loading human review queue...
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 text-red-800 rounded-lg text-sm">{error}</div>
        ) : cases.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-sm border border-dashed rounded-lg">
            No active human review cases in queue. Click "Request Human Review" on any AI assessment to escalate a complex query.
          </div>
        ) : (
          <div className="space-y-4">
            {cases.map((c) => (
              <div key={c.case_id} className="p-5 border border-slate-200 rounded-xl bg-white shadow-sm space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-gov-accent font-bold">{c.case_id}</span>
                    <h3 className="text-base font-bold text-gov-navy mt-0.5">"{c.user_question}"</h3>
                  </div>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">
                    <Clock className="w-3.5 h-3.5 text-amber-600" />
                    {c.status}
                  </span>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                  <div className="font-bold text-slate-700 uppercase">Reason for Escalation</div>
                  <p className="text-slate-800">{c.reason_for_escalation}</p>
                </div>

                <div className="flex justify-between items-center text-xs text-slate-500 pt-2 border-t border-slate-100">
                  <span>Target Jurisdiction: <strong className="text-slate-800">{c.jurisdiction}</strong></span>
                  <span>Escalated At: <strong className="text-slate-800">{new Date(c.created_at).toLocaleString()}</strong></span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
