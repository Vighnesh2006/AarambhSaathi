import React, { useState, useEffect } from 'react';
import {
  Landmark,
  ExternalLink,
  FileCheck,
  HelpCircle,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Info,
  DollarSign,
  Layers,
  ArrowRight,
  Sparkles,
  BookOpen,
  Building2,
  FileText
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function SchemesCard({ schemes, userProfile, language = 'en', onUpdateProfile }) {
  const t = getTranslation(language);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'matched' | 'conditional' | 'insufficient'
  const [expandedScheme, setExpandedScheme] = useState(null);
  const [cardSection, setCardSection] = useState({}); // scheme_id -> 'eligibility' | 'benefits' | 'documents' | 'process'
  const [stats, setStats] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);
  const [showIncomeModal, setShowIncomeModal] = useState(false);
  const [selectedIncome, setSelectedIncome] = useState(null);

  // Normalize scheme lists from either SchemeMatchResponse or legacy Array
  let matchedList = [];
  let conditionalList = [];
  let insufficientList = [];
  let notEligibleList = [];
  let userSummary = null;
  let projectSummary = null;
  let dataQuality = null;

  if (schemes && typeof schemes === 'object' && !Array.isArray(schemes)) {
    matchedList = schemes.matched_schemes || [];
    conditionalList = schemes.conditional_schemes || [];
    insufficientList = schemes.insufficient_data_schemes || [];
    notEligibleList = schemes.not_eligible_schemes || [];
    userSummary = schemes.user_profile_summary || null;
    projectSummary = schemes.project_summary || null;
    dataQuality = schemes.data_quality || null;
  } else if (Array.isArray(schemes)) {
    schemes.forEach((s) => {
      const st = s.status || 'MATCHED';
      if (st === 'MATCHED') matchedList.push(s);
      else if (st === 'CONDITIONALLY MATCHED') conditionalList.push(s);
      else if (st === 'INSUFFICIENT DATA') insufficientList.push(s);
      else notEligibleList.push(s);
    });
  }

  // Combined suitable schemes
  const allSuitable = [...matchedList, ...conditionalList, ...insufficientList];

  useEffect(() => {
    fetchStats();
  }, []);

  // Auto-expand the first matched scheme on initial load
  useEffect(() => {
    if (allSuitable.length > 0 && !expandedScheme) {
      setExpandedScheme(allSuitable[0].scheme_id);
    }
  }, [schemes]);

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

  const getFilteredSchemes = () => {
    if (activeTab === 'matched') return matchedList;
    if (activeTab === 'conditional') return conditionalList;
    if (activeTab === 'insufficient') return insufficientList;
    return allSuitable;
  };

  const displayedSchemes = getFilteredSchemes();

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Eligible Match</span>
          </span>
        );
      case 'CONDITIONALLY MATCHED':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Conditionally Matched</span>
          </span>
        );
      case 'INSUFFICIENT DATA':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-sky-700 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full">
            <Info className="w-3.5 h-3.5 text-sky-600" />
            <span>Verification Required</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-slate-600 bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full">
            <span>{status}</span>
          </span>
        );
    }
  };

  if (!schemes || allSuitable.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-card border border-gv-border text-center">
        <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mx-auto mb-3">
          <Landmark className="w-6 h-6" />
        </div>
        <h3 className="text-sm font-bold text-slate-800">{t.schemesTitle}</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          {language === 'mr'
            ? 'आपले कौशल्य व भांडवल सांगून शासकीय अनुदान योजनांची माहिती मिळवा.'
            : language === 'hi'
            ? 'अपनी जानकारी देकर सरकारी सब्सिडी योजनाओं की जानकारी प्राप्त करें।'
            : 'Complete your business profile in the chat to discover targeted central & state credit-linked subsidies.'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-surface via-amber-50/70 to-emerald-50 px-5 py-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center text-sm font-bold shadow-2xs">
            <Landmark className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-black text-slate-900 font-display">
                {t.schemesTitle || 'Government Support'}
              </h3>
              <span className="text-[10px] bg-amber-100 text-amber-900 font-bold px-2.5 py-0.5 rounded-full border border-amber-200">
                Deterministic Engine
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Targeted Central & State credit-linked subsidies matched deterministically for your profile
            </p>
          </div>
        </div>

        {/* Sync / Refresh Button */}
        <div className="flex items-center space-x-2">
          {syncMessage ? (
            <span className="text-xs text-emerald-700 font-medium flex items-center space-x-1.5 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>{syncMessage}</span>
            </span>
          ) : (
            <button
              onClick={handleSync}
              disabled={syncing}
              title="Sync latest schemes from myScheme master catalogue"
              className="text-xs flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium shadow-2xs transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${syncing ? 'animate-spin' : ''}`} />
              <span>{syncing ? 'Syncing...' : 'Sync myScheme'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Tabs Filter Bar */}
      <div className="bg-slate-50/80 px-5 py-2.5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'all'
                ? 'bg-slate-900 text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-200/70'
            }`}
          >
            All Relevant ({allSuitable.length})
          </button>
          <button
            onClick={() => setActiveTab('matched')}
            className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'matched'
                ? 'bg-emerald-700 text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-200/70'
            }`}
          >
            Matched ({matchedList.length})
          </button>
          {conditionalList.length > 0 && (
            <button
              onClick={() => setActiveTab('conditional')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'conditional'
                  ? 'bg-amber-700 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-200/70'
              }`}
            >
              Conditional ({conditionalList.length})
            </button>
          )}
          {insufficientList.length > 0 && (
            <button
              onClick={() => setActiveTab('insufficient')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'insufficient'
                  ? 'bg-sky-700 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-200/70'
              }`}
            >
              Missing Info ({insufficientList.length})
            </button>
          )}
        </div>

        {/* Financial Context Pill */}
        {projectSummary && projectSummary.project_cost > 0 && (
          <div className="text-[11px] text-slate-500 flex items-center gap-2 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
            <span>Project Cost: <strong className="text-slate-800">₹{projectSummary.project_cost.toLocaleString('en-IN')}</strong></span>
            <span>•</span>
            <span>Own: <strong className="text-emerald-700">₹{(projectSummary.own_contribution || 0).toLocaleString('en-IN')}</strong></span>
            <span>•</span>
            <span>Funding Gap: <strong className="text-amber-700">₹{(projectSummary.funding_requirement || 0).toLocaleString('en-IN')}</strong></span>
          </div>
        )}
      </div>

      {/* Schemes List */}
      <div className="p-4 sm:p-5 space-y-4">
        {displayedSchemes.map((s) => {
          const isExpanded = expandedScheme === s.scheme_id;
          const currentSection = cardSection[s.scheme_id] || 'eligibility';
          const matchScore = s.match_score || 85;

          return (
            <div
              key={s.scheme_id}
              className={`rounded-2xl border transition-all duration-200 ${
                isExpanded
                  ? 'border-amber-400 bg-amber-50/10 shadow-md ring-1 ring-amber-400/20'
                  : 'border-slate-200 hover:border-slate-300 bg-white shadow-2xs'
              }`}
            >
              {/* Main Card Header */}
              <div
                onClick={() => setExpandedScheme(isExpanded ? null : s.scheme_id)}
                className="p-4 sm:p-5 cursor-pointer select-none"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 text-white flex items-center justify-center font-bold text-sm shadow-2xs flex-shrink-0 mt-0.5">
                      🏛️
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h4 className="text-sm sm:text-base font-bold text-slate-900 font-display">
                          {s.scheme_name}
                        </h4>
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-md">
                          {s.scheme_level || 'Central'} Scheme
                        </span>
                      </div>

                      {/* Primary Rationale */}
                      <p className="text-xs text-emerald-800 font-medium mt-1 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                        <span>{s.why_relevant || s.why_matched?.[0] || 'Matches your rural micro-enterprise profile.'}</span>
                      </p>

                      {/* Quick Tags: Ministry & Financial fit */}
                      <div className="flex flex-wrap items-center gap-1.5 mt-2 text-[10px]">
                        {s.ministry && (
                          <span className="text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                            {s.ministry}
                          </span>
                        )}
                        {s.financial_fit && (
                          <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
                            ✓ {s.financial_fit.status}
                          </span>
                        )}
                        {s.last_verified && (
                          <span className="text-slate-400 italic">
                            Verified: {s.last_verified.split(' ')[0]} {s.last_verified.split(' ')[1] || ''}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Status & Relevance Score */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 flex-shrink-0">
                    <div className="flex items-center gap-2">
                      {getStatusBadge(s.status)}
                      <span className="text-xs font-black text-amber-900 bg-amber-100 px-2 py-0.5 rounded-lg border border-amber-200">
                        {matchScore}% Fit
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-600 font-medium">
                      <span>{isExpanded ? 'Hide Details' : 'View Full Details'}</span>
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </div>
                </div>
              </div>

              {/* Expandable Deep-Dive Drawer */}
              {isExpanded && (
                <div className="px-4 sm:px-5 pb-5 pt-0 border-t border-slate-100 space-y-4">
                  
                  {/* Internal Sub-Navigation Tabs */}
                  <div className="flex items-center space-x-2 border-b border-slate-200 pt-3 pb-2 overflow-x-auto">
                    <button
                      onClick={() => setCardSection({ ...cardSection, [s.scheme_id]: 'eligibility' })}
                      className={`text-xs font-bold pb-1.5 px-2 border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
                        currentSection === 'eligibility'
                          ? 'border-amber-600 text-amber-900'
                          : 'border-transparent text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Eligibility Criteria ({s.eligibility?.length || 0})</span>
                    </button>

                    <button
                      onClick={() => setCardSection({ ...cardSection, [s.scheme_id]: 'benefits' })}
                      className={`text-xs font-bold pb-1.5 px-2 border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
                        currentSection === 'benefits'
                          ? 'border-amber-600 text-amber-900'
                          : 'border-transparent text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <DollarSign className="w-3.5 h-3.5" />
                      <span>Benefits & Subsidies</span>
                    </button>

                    <button
                      onClick={() => setCardSection({ ...cardSection, [s.scheme_id]: 'documents' })}
                      className={`text-xs font-bold pb-1.5 px-2 border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
                        currentSection === 'documents'
                          ? 'border-amber-600 text-amber-900'
                          : 'border-transparent text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <FileCheck className="w-3.5 h-3.5" />
                      <span>Document Checklist ({s.documents?.length || s.required_documents?.length || 0})</span>
                    </button>

                    <button
                      onClick={() => setCardSection({ ...cardSection, [s.scheme_id]: 'process' })}
                      className={`text-xs font-bold pb-1.5 px-2 border-b-2 transition-all flex items-center gap-1.5 whitespace-nowrap ${
                        currentSection === 'process'
                          ? 'border-amber-600 text-amber-900'
                          : 'border-transparent text-slate-500 hover:text-slate-800'
                      }`}
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                      <span>Application Steps</span>
                    </button>
                  </div>

                  {/* TAB 1: ELIGIBILITY EVALUATION */}
                  {currentSection === 'eligibility' && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                        {(s.eligibility || []).map((el, idx) => {
                          const isPass = el.status === 'Eligible';
                          const isCond = el.status === 'Conditionally Eligible';
                          const isMissing = el.status === 'Insufficient Data';
                          const isFail = el.status === 'Not Eligible';

                          return (
                            <div
                              key={idx}
                              className={`p-3 rounded-xl border text-xs ${
                                isPass
                                  ? 'bg-emerald-50/50 border-emerald-200'
                                  : isCond
                                  ? 'bg-amber-50/50 border-amber-200'
                                  : isMissing
                                  ? 'bg-sky-50/50 border-sky-200'
                                  : isFail
                                  ? 'bg-rose-50/50 border-rose-200'
                                  : 'bg-slate-50 border-slate-200'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-bold text-slate-800">{el.condition}</span>
                                <span
                                  className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                                    isPass
                                      ? 'bg-emerald-100 text-emerald-800'
                                      : isCond
                                      ? 'bg-amber-100 text-amber-800'
                                      : isMissing
                                      ? 'bg-sky-100 text-sky-800'
                                      : isFail
                                      ? 'bg-rose-100 text-rose-800'
                                      : 'bg-slate-200 text-slate-700'
                                  }`}
                                >
                                  {el.status}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-600 leading-snug">{el.reason}</p>
                              {el.source && (
                                <span className="block text-[9px] text-slate-400 mt-1.5 italic">
                                  Source: {el.source}
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {/* Summary box */}
                      {s.eligibility_summary && (
                        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                          <span className="font-bold text-slate-700 block mb-1">Official Eligibility Overview:</span>
                          <p className="text-slate-600 text-[11px] leading-relaxed">{s.eligibility_summary}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 2: BENEFITS & SUBSIDY STRUCTURE */}
                  {currentSection === 'benefits' && (
                    <div className="space-y-3">
                      {/* Financial compatibility card */}
                      {s.financial_fit && (
                        <div className="bg-emerald-50/70 p-3.5 rounded-xl border border-emerald-200">
                          <span className="text-xs font-bold text-emerald-900 block mb-1">
                            📊 Financial Compatibility Assessment:
                          </span>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2 text-xs">
                            <div className="bg-white p-2 rounded-lg border border-emerald-100">
                              <span className="text-[10px] text-slate-500 block">Project Outlay</span>
                              <strong className="text-slate-800 font-bold">₹{s.financial_fit.project_cost.toLocaleString('en-IN')}</strong>
                            </div>
                            <div className="bg-white p-2 rounded-lg border border-emerald-100">
                              <span className="text-[10px] text-slate-500 block">Max Scheme Ceiling</span>
                              <strong className="text-emerald-700 font-bold">
                                {s.financial_fit.max_limit ? `₹${s.financial_fit.max_limit.toLocaleString('en-IN')}` : 'No strict cap'}
                              </strong>
                            </div>
                            <div className="bg-white p-2 rounded-lg border border-emerald-100">
                              <span className="text-[10px] text-slate-500 block">Own Margin (5-10%)</span>
                              <strong className="text-slate-800 font-bold">₹{(s.financial_fit.own_contribution || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div className="bg-white p-2 rounded-lg border border-emerald-100">
                              <span className="text-[10px] text-slate-500 block">Bank Loan / Gap</span>
                              <strong className="text-amber-700 font-bold">₹{(s.financial_fit.funding_requirement || 0).toLocaleString('en-IN')}</strong>
                            </div>
                          </div>
                          <p className="text-[10px] text-emerald-800 mt-2 italic">
                            * {s.financial_fit.notes || 'Appears financially compatible based on available scheme data.'}
                          </p>
                        </div>
                      )}

                      {/* Benefits Bullets */}
                      <div className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-2">
                        <span className="text-xs font-bold text-slate-800 block">
                          💰 Key Financial Support & Subsidy Terms:
                        </span>
                        <div className="space-y-1.5">
                          {(s.benefits || []).map((ben, idx) => (
                            <div key={idx} className="flex items-start space-x-2 text-xs text-slate-700">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 flex-shrink-0"></span>
                              <span className="leading-relaxed">{ben}</span>
                            </div>
                          ))}
                        </div>
                        {s.possible_support && (
                          <div className="pt-2 mt-2 border-t border-slate-100 text-[11px] text-slate-600">
                            <strong>Official Notification Text:</strong> {s.possible_support}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* TAB 3: PERSONALIZED DOCUMENT CHECKLIST */}
                  {currentSection === 'documents' && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                        {(s.documents || []).map((doc, idx) => {
                          const isReq = doc.status === 'Required';
                          const isCond = doc.status === 'Conditionally Required';

                          return (
                            <div
                              key={idx}
                              className={`p-3 rounded-xl border text-xs flex flex-col justify-between ${
                                isReq
                                  ? 'bg-emerald-50/30 border-emerald-200'
                                  : isCond
                                  ? 'bg-amber-50/30 border-amber-200'
                                  : 'bg-slate-50 border-slate-200 opacity-80'
                              }`}
                            >
                              <div>
                                <div className="flex items-start justify-between gap-1 mb-1">
                                  <div className="flex items-center space-x-1.5 font-bold text-slate-800">
                                    {isReq ? (
                                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                                    ) : (
                                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                                    )}
                                    <span>{doc.document_name}</span>
                                  </div>
                                  <span
                                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0 ${
                                      isReq
                                        ? 'bg-emerald-100 text-emerald-800'
                                        : 'bg-amber-100 text-amber-800'
                                    }`}
                                  >
                                    {doc.status}
                                  </span>
                                </div>
                                <p className="text-[11px] text-slate-600 mt-1">{doc.description}</p>
                              </div>

                              <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-[10px] text-slate-500 space-y-0.5">
                                <div><strong>Issuing Authority:</strong> {doc.where_to_get}</div>
                                {doc.format && <div><strong>Format:</strong> {doc.format}</div>}
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      {/* Fallback legacy list if structured docs empty */}
                      {(!s.documents || s.documents.length === 0) && s.required_documents && (
                        <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1 text-xs">
                          {s.required_documents.map((d, i) => (
                            <div key={i} className="flex items-center space-x-2 text-slate-700">
                              <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                              <span>{d}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 4: APPLICATION STEPS & PORTALS */}
                  {currentSection === 'process' && (
                    <div className="space-y-3">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5">
                        <span className="text-xs font-bold text-slate-800 block">
                          🚀 Recommended Application Roadmap:
                        </span>
                        <div className="space-y-2 text-xs text-slate-700">
                          {(s.application_process || []).map((step, idx) => (
                            <div key={idx} className="flex items-start space-x-2.5">
                              <span className="w-5 h-5 rounded-full bg-amber-600 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0 mt-0.5">
                                {idx + 1}
                              </span>
                              <p className="leading-snug pt-0.5">{step}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Footer & Official Portal Links */}
                  <div className="flex flex-wrap items-center justify-between gap-2.5 pt-2 border-t border-slate-200">
                    <div className="text-[10px] text-slate-400 italic">
                      {s.notes ? `Note: ${s.notes}` : 'Apply online or consult your nearest District Industries Centre (DIC) / Bank.'}
                    </div>

                    <div className="flex items-center space-x-2">
                      {s.myscheme_url && (
                        <a
                          href={s.myscheme_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-xs font-semibold text-blue-700 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-xl border border-blue-200 transition"
                        >
                          <span>myScheme Portal</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {s.official_url && (
                        <a
                          href={s.official_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-xs font-semibold text-emerald-800 hover:text-emerald-900 bg-emerald-50 hover:bg-emerald-100 px-3 py-1.5 rounded-xl border border-emerald-200 transition"
                        >
                          <span>Official Portal ↗</span>
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

        {/* Advisory Disclaimer */}
        <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-600 flex items-start space-x-2 leading-relaxed">
          <ShieldCheck className="w-4 h-4 text-emerald-700 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Deterministic Assistance Layer:</strong> Aarambh Saathi identifies potentially relevant schemes based on verified government guidelines. It does not replace official nodal agencies. Final credit sanction, interest subvention, and subsidy release are subject to formal application, DPR submission, and bank appraisal.
          </span>
        </div>
      </div>
    </div>
  );
}
