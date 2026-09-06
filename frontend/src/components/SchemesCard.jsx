import React, { useState, useEffect } from 'react';
import { Landmark, ExternalLink, FileCheck, HelpCircle, ShieldCheck, ChevronDown, ChevronUp, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function SchemesCard({ schemes }) {
  const [expandedScheme, setExpandedScheme] = useState(schemes?.[0]?.scheme_id || null);
  const [stats, setStats] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/schemes/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      // ignore
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const res = await fetch('/api/schemes/sync', { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setStats(data.meta);
        setSyncMessage(`Synced ${data.meta?.total_schemes || 62} schemes!`);
        setTimeout(() => setSyncMessage(null), 3000);
      }
    } catch (e) {
      setSyncMessage('Sync failed');
      setTimeout(() => setSyncMessage(null), 3000);
    } finally {
      setSyncing(false);
    }
  };

  if (!schemes || schemes.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-card border border-gv-border text-center">
        <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto mb-3">
          <Landmark className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-bold text-slate-800">Government Schemes Matcher</h3>
        <p className="text-xs text-slate-500 mt-1">
          Complete your business profile in the chat to discover targeted central & state credit-linked subsidies.
        </p>
        <div className="mt-3 inline-flex items-center space-x-1 text-[11px] text-amber-700 font-medium bg-amber-50 px-2.5 py-1 rounded-full">
          <span>Trained on {stats?.total_schemes || '60+'} verified schemes from myScheme.gov.in</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-surface via-amber-50/70 to-emerald-50 px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-600 text-white flex items-center justify-center text-xs font-bold shadow-2xs">
            <Landmark className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 font-display flex items-center space-x-1.5">
              <span>Potentially Relevant Government Schemes</span>
              <span className="text-[10px] bg-amber-100 text-amber-900 px-2 py-0.5 rounded-full font-semibold">
                {schemes.length} Matched
              </span>
            </h3>
            <p className="text-[11px] text-slate-500 flex items-center space-x-1.5">
              <span>Cross-referenced with myScheme.gov.in</span>
              {stats?.total_schemes && (
                <span className="text-emerald-700 font-medium">({stats.total_schemes} in database)</span>
              )}
            </p>
          </div>
        </div>

        {/* Sync / Refresh Button */}
        <div className="flex items-center space-x-2">
          {syncMessage ? (
            <span className="text-[11px] text-emerald-700 font-medium flex items-center space-x-1 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-200">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              <span>{syncMessage}</span>
            </span>
          ) : (
            <button
              onClick={handleSync}
              disabled={syncing}
              title="Sync latest schemes from myScheme master catalogue"
              className="text-[11px] flex items-center space-x-1 px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition"
            >
              <RefreshCw className={`w-3 h-3 text-slate-500 ${syncing ? 'animate-spin' : ''}`} />
              <span>{syncing ? 'Syncing...' : 'Sync myScheme'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Schemes List */}
      <div className="p-4 sm:p-5 space-y-3">
        {schemes.map((s) => {
          const isExpanded = expandedScheme === s.scheme_id;

          return (
            <div
              key={s.scheme_id}
              className={`rounded-xl border transition-all ${
                isExpanded
                  ? 'border-amber-400/80 bg-amber-50/20 shadow-sm'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
            >
              {/* Header Bar */}
              <div
                onClick={() => setExpandedScheme(isExpanded ? null : s.scheme_id)}
                className="p-3.5 flex items-center justify-between cursor-pointer select-none"
              >
                <div className="flex items-start space-x-2.5">
                  <div className="w-6 h-6 rounded-md bg-amber-100 text-amber-800 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                    🏛️
                  </div>
                  <div>
                    <h4 className="text-xs sm:text-sm font-bold text-slate-900 font-display">
                      {s.scheme_name}
                    </h4>
                    <p className="text-[11px] text-emerald-800 font-medium mt-0.5">
                      ✓ {s.why_relevant}
                    </p>
                    {s.ministry && (
                      <span className="inline-block mt-1 text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {s.ministry}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                    Preliminary Match
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-3.5 pb-4 pt-1 border-t border-amber-200/50 space-y-3 text-xs">
                  {/* Financial Support / Subsidy */}
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-700 block text-[11px] mb-1">
                      💰 Financial Support & Subsidy Structure:
                    </span>
                    <p className="text-slate-600 leading-relaxed text-[11px]">{s.possible_support}</p>
                  </div>

                  {/* Basic Eligibility */}
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-700 block text-[11px] mb-1">
                      📋 Basic Eligibility Criteria:
                    </span>
                    <p className="text-slate-600 leading-relaxed text-[11px]">{s.eligibility_summary}</p>
                  </div>

                  {/* Required Documents */}
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-700 block text-[11px] mb-1.5 flex items-center">
                      <FileCheck className="w-3.5 h-3.5 text-gv-primary mr-1" /> Required Application Documents:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-[11px] text-slate-600">
                      {s.required_documents?.map((doc, idx) => (
                        <div key={idx} className="flex items-center space-x-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                          <span>{doc}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Footer & Official Portal Links */}
                  <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                    <span className="text-[10px] text-slate-400 italic">
                      Note: {s.notes || 'Apply online or visit your local District Industries Centre (DIC).'}
                    </span>
                    <div className="flex items-center space-x-2">
                      {s.myscheme_url && (
                        <a
                          href={s.myscheme_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-700 hover:text-blue-800 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200 transition"
                        >
                          <span>myScheme Portal</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {s.official_source && (
                        <a
                          href={s.official_source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-xs font-semibold text-gv-primary hover:text-gv-secondary bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 transition"
                        >
                          <span>Official Portal</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {/* Disclaimer */}
        <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-[10px] text-slate-500 flex items-start space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Eligibility Advisory:</strong> Matching is based on indicative guidelines cross-referenced with myScheme.gov.in. Final subsidy disbursement and loan sanctioning are subject to submission of DPR and formal verification by respective nodal agencies and lending institutions.
          </span>
        </div>
      </div>
    </div>
  );
}
