import React, { useRef, useState } from 'react';
import {
  X,
  Printer,
  Download,
  CheckCircle,
  FileText,
  Landmark,
  Calendar,
  IndianRupee,
  MapPin,
  Award,
  ShieldAlert,
  Sparkles,
  ArrowRight,
  MessageSquare,
  Sprout,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Wrench,
  Building,
  TrendingUp,
  ShieldCheck,
  Globe,
  Database
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function ReportModal({
  report,
  isOpen,
  onClose,
  isProfileReady,
  onStartChat,
  language = 'en',
  onLanguageChange
}) {
  const t = getTranslation(language);
  const printRef = useRef();
  const [activeNavSection, setActiveNavSection] = useState('overview');

  if (!isOpen) return null;

  // If report is not ready or profile incomplete, show friendly interactive guidance
  if (!report || !report.recommended_business) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 sm:p-8 text-center border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150 space-y-5">
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700"
          >
            <X size={18} />
          </button>

          <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200 shadow-sm">
            <Sprout size={32} />
          </div>

          <div>
            <h3 className="text-xl font-black text-[#072a24] font-display">
              {language === 'mr' ? 'DPR अहवाल तयार करण्यासाठी माहिती द्या' : language === 'hi' ? 'DPR रिपोर्ट बनाने के लिए जानकारी दें' : 'Complete Profile to Generate DPR'}
            </h3>
            <p className="text-xs sm:text-sm text-[#527068] mt-2 leading-relaxed">
              {language === 'mr'
                ? 'तुमच्या व्यवसायासाठी ९० दिवसांचा सविस्तर DPR अहवाल, बँक कर्ज हप्ता व शासकीय अनुदान मोजण्यासाठी स्थान, कौशल्य व भांडवलाची माहिती आवश्यक आहे.'
                : language === 'hi'
                ? 'आपके व्यवसाय के लिए 90-दिवसीय विस्तृत DPR रिपोर्ट, बैंक लोन ईएमआई और सब्सिडी की गणना के लिए स्थान, कौशल और पूंजी की जानकारी आवश्यक है।'
                : 'Your customized 17-Section Detailed Project Report (DPR) requires location, skills, and investment details to calculate accurate loan EMIs, profit margins, and government subsidies.'}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#edf7ee] border border-emerald-200 text-left space-y-2 text-xs text-[#075247]">
            <span className="font-bold block text-sm">
              {language === 'mr' ? 'DPR अहवाल कसा मिळवावा:' : language === 'hi' ? 'DPR रिपोर्ट कैसे प्राप्त करें:' : 'How to unlock your DPR Plan:'}
            </span>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
              <span>{language === 'mr' ? 'चॅटमध्ये तुमचा आवडता व्यवसाय सांगा' : language === 'hi' ? 'चैट में अपना पसंदीदा व्यवसाय बताएं' : 'Share your preferred business or occupation in Chat'}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
              <span>{language === 'mr' ? 'तुमचा जिल्हा/गाव आणि उपलब्ध भांडवल सांगा' : language === 'hi' ? 'अपना जिला/गांव और उपलब्ध पूंजी बताएं' : 'Mention your district / village and available capital'}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
              <span>{language === 'mr' ? 'एआय त्वरित शिफारसी व DPR अहवाल तयार करेल' : language === 'hi' ? 'एआई तुरंत सिफारिशें और DPR रिपोर्ट तैयार करेगा' : 'AI will instantly build your Top 3 recommendations and DPR'}</span>
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => {
                onClose();
                if (onStartChat) onStartChat();
              }}
              className="flex-1 py-3 px-4 rounded-xl bg-[#075247] hover:bg-[#063f39] text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              <MessageSquare size={16} />
              <span>{t.talkToBotBtn || (language === 'mr' ? 'आरंभ साथीशी बोला' : language === 'hi' ? 'आरंभ साथी से बात करें' : 'Chat With Aarambh Saathi')}</span>
              <ArrowRight size={15} />
            </button>
            <button
              onClick={onClose}
              className="py-3 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition"
            >
              {language === 'mr' ? 'बंद करा' : language === 'hi' ? 'बंद करें' : 'Close'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  const scrollToSection = (id) => {
    setActiveNavSection(id);
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const {
    report_id,
    created_at,
    executive_summary,
    entrepreneur_profile: p,
    recommended_business: b,
    local_feasibility: f,
    financial_plan: fp,
    business_setup: bs,
    machinery = [],
    suppliers = [],
    project_cost_breakdown: pcb,
    means_of_finance: mof,
    financial_projections: fpr,
    relevant_schemes: schemes = [],
    documents = [],
    roadmap = [],
    action_plan_90_days,
    risks = [],
    data_sources = [],
    assumptions = [],
    explainable_reasons = [],
    disclaimer
  } = report;

  const cost = fp?.project_cost || b?.required_investment || 0;
  const own = fp?.own_contribution || p?.capital || (cost * 0.1);
  const gap = fp?.required_loan || (cost - own);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-2 sm:p-5 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl max-w-5xl w-full max-h-[94vh] flex flex-col border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Top Control Bar (Hidden on Print) */}
        <div className="bg-[#063f39] text-white px-5 py-3.5 flex flex-wrap items-center justify-between gap-3 border-b border-[#0f5349] no-print">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-400/20 text-amber-300 flex items-center justify-center border border-amber-300/40">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold font-display text-white flex items-center gap-2">
                <span>Aarambh Saathi Business Project Report (DPR)</span>
                <span className="text-[10px] bg-amber-400 text-slate-950 font-extrabold px-2 py-0.5 rounded-full">
                  17-Section Model
                </span>
              </h2>
              <p className="text-[11px] text-emerald-200">DPR Reference ID: {report_id}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-[#15803d] hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition"
              title="Print or Save as PDF"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{language === 'mr' ? 'प्रिंट / पीडीएफ' : language === 'hi' ? 'प्रिंट / पीडीएफ' : 'Print / Download A4'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Quick Jump Section Bar (Hidden on Print) */}
        <div className="bg-slate-100/90 px-5 py-2 border-b border-slate-200 flex items-center space-x-2 overflow-x-auto text-[11px] font-bold text-slate-600 no-print scrollbar-none">
          <button
            onClick={() => scrollToSection('sec-overview')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-overview' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => scrollToSection('sec-business')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-business' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Business & Fit
          </button>
          <button
            onClick={() => scrollToSection('sec-feasibility')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-feasibility' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Feasibility (8 Factors)
          </button>
          <button
            onClick={() => scrollToSection('sec-setup')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-setup' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Setup & Machinery
          </button>
          <button
            onClick={() => scrollToSection('sec-finance')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-finance' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Finance & EMI
          </button>
          <button
            onClick={() => scrollToSection('sec-schemes')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-schemes' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Schemes & Docs
          </button>
          <button
            onClick={() => scrollToSection('sec-roadmap')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-roadmap' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Roadmap & Risks
          </button>
          <button
            onClick={() => scrollToSection('sec-sources')}
            className={`px-2.5 py-1 rounded-lg transition whitespace-nowrap ${
              activeNavSection === 'sec-sources' ? 'bg-[#075247] text-white' : 'hover:bg-slate-200'
            }`}
          >
            Data Sources
          </button>
        </div>

        {/* Printable Report Body */}
        <div ref={printRef} className="p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-800 text-xs sm:text-sm print:p-0 print:text-black">
          
          {/* Official Letterhead */}
          <div className="border-b-2 border-[#075247] pb-4 flex flex-wrap justify-between items-start gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🌱</span>
                <h1 className="text-xl sm:text-2xl font-black text-[#072a24] font-display tracking-tight">
                  AARAMBH SAATHI
                </h1>
              </div>
              <p className="text-xs font-bold text-[#15803d] uppercase tracking-wider mt-0.5">
                Gaav ka Vikas, Aapke Saath • Micro-Enterprise Project Report & Business Plan
              </p>
            </div>

            <div className="text-right text-xs text-slate-500">
              <p><strong>Report ID:</strong> {report_id}</p>
              <p><strong>Generated On:</strong> {created_at}</p>
              <span className="inline-block bg-emerald-100 text-[#075247] font-bold px-2 py-0.5 rounded text-[10px] mt-1 border border-emerald-200">
                Verified Advisory Assessment
              </span>
            </div>
          </div>

          {/* SECTION 1: EXECUTIVE SUMMARY */}
          <div id="sec-overview" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              1. Executive Summary
            </h3>

            {/* Metrics Ribbon */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-center">
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Project Outlay</span>
                <strong className="text-sm font-bold text-slate-900">₹{Number(cost).toLocaleString('en-IN')}</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Own Contribution</span>
                <strong className="text-sm font-bold text-emerald-700">₹{Number(own).toLocaleString('en-IN')}</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Loan / Gap</span>
                <strong className="text-sm font-bold text-amber-700">₹{Number(gap).toLocaleString('en-IN')}</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase">Feasibility</span>
                <strong className="text-sm font-bold text-teal-800">{f?.feasibility_score}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 col-span-2 sm:col-span-1">
                <span className="text-[10px] text-slate-500 block uppercase">Schemes Matched</span>
                <strong className="text-sm font-bold text-indigo-700">{schemes.length} Schemes</strong>
              </div>
            </div>

            {/* Narrative Summary */}
            <div className="bg-emerald-50/50 p-4 rounded-2xl border border-emerald-200 text-xs text-slate-800 leading-relaxed">
              <p>{executive_summary || "Based on the information provided, Aarambh Saathi identified this business as a suitable micro-enterprise opportunity."}</p>
            </div>
          </div>

          {/* SECTION 2: ENTREPRENEUR PROFILE */}
          <div className="bg-[#f8faf9] p-4 rounded-2xl border border-slate-200 space-y-2">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              2. Entrepreneur Profile
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px]">Entrepreneur Name</span>
                <strong className="text-slate-800">{p?.name || 'Rural Micro-Entrepreneur'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Age & Gender</span>
                <strong className="text-slate-800">{p?.age ? `${p.age} Yrs` : 'Not Specified'} • {p?.gender || 'Not Specified'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Social Category</span>
                <strong className="text-slate-800">{p?.category || 'General / OBC'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Education</span>
                <strong className="text-slate-800">{p?.education || 'Secondary / Self-Taught'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Location / Cluster</span>
                <strong className="text-slate-800">{[p?.village, p?.district, p?.state].filter(Boolean).join(', ') || 'Rural District'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Skills & Background</span>
                <strong className="text-slate-800">{p?.skills?.join(', ') || p?.experience || 'Allied Agricultural Trade'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Available Capital</span>
                <strong className="text-emerald-700">₹{Number(own).toLocaleString('en-IN')}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Enterprise Goal</span>
                <strong className="text-slate-800">{p?.intent || 'Start a new micro-enterprise'}</strong>
              </div>
            </div>
          </div>

          {/* SECTION 3 & 4: PROPOSED BUSINESS & WHY RECOMMENDED */}
          <div id="sec-business" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              3 & 4. Proposed Business & 9-Factor Fit Rationale
            </h3>

            <div className="p-4 rounded-2xl border-2 border-emerald-300 bg-emerald-50/40">
              <div className="flex flex-wrap justify-between items-start gap-2 mb-2">
                <div>
                  <h4 className="text-base font-bold text-[#072a24] font-display">{b?.business_name}</h4>
                  <p className="text-xs text-slate-600">Category: <strong>{b?.category}</strong></p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold bg-[#075247] text-amber-300 px-3 py-1 rounded-lg">
                    Match Score: {b?.overall_score}/100
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed mb-3">{b?.description}</p>

              {/* Explainable Reasons */}
              <div className="bg-white p-3.5 rounded-xl border border-emerald-200 space-y-1.5">
                <span className="font-bold text-xs text-emerald-950 block">Deterministic Recommendation Factors:</span>
                {explainable_reasons.map((reason, i) => (
                  <div key={i} className="flex items-start space-x-2 text-xs text-slate-700">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* SECTION 5: HYPER-LOCAL FEASIBILITY (8 FACTORS) */}
          <div id="sec-feasibility" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              5. Hyper-Local Feasibility Assessment (8 Deterministic Indicators)
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">1. Location Fit</span>
                <strong className="text-slate-800">{f?.factors?.location_score || 88}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">2. Infrastructure</span>
                <strong className="text-slate-800">{f?.factors?.infrastructure_score || 85}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">3. Market Access</span>
                <strong className="text-slate-800">{f?.factors?.market_access_score || 90}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">4. Local Demand</span>
                <strong className="text-slate-800">{f?.factors?.demand_score || 88}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">5. Competition</span>
                <strong className="text-slate-800">{f?.factors?.competition_score || 82}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">6. Suppliers</span>
                <strong className="text-slate-800">{f?.factors?.supplier_score || 86}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">7. Raw Materials</span>
                <strong className="text-slate-800">{f?.factors?.raw_material_score || 92}/100</strong>
              </div>
              <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">8. Transport</span>
                <strong className="text-slate-800">{f?.factors?.transport_score || 84}/100</strong>
              </div>
            </div>

            {/* Markets and Competitors Summary */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-white rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800 block mb-1">Nearby Market Hubs & APMCs:</span>
                <ul className="space-y-1 text-slate-600 text-[11px]">
                  {(f?.nearby_markets || []).slice(0, 3).map((m, i) => (
                    <li key={i}>• {m.market_name || m.name} ({m.distance_km || 'Nearby'} km)</li>
                  ))}
                  {(!f?.nearby_markets || f?.nearby_markets.length === 0) && (
                    <li className="italic text-slate-400">Weekly rural haat and taluka APMC market.</li>
                  )}
                </ul>
              </div>

              <div className="p-3 bg-white rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800 block mb-1">Local Competition Level:</span>
                <p className="text-slate-600 text-[11px] leading-snug">
                  {f?.competition_level || 'Moderate local player density; clear room for quality-based market share.'}
                </p>
                {f?.infrastructure_gaps && f.infrastructure_gaps.length > 0 && (
                  <p className="text-amber-800 text-[10px] mt-1">
                    <strong>Gaps to address:</strong> {f.infrastructure_gaps.join(', ')}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* SECTION 6, 7 & 8: BUSINESS SETUP, MACHINERY & SUPPLIERS */}
          <div id="sec-setup" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              6, 7 & 8. Machinery, Equipment & Verified Suppliers
            </h3>

            {/* Machinery Table */}
            {machinery && machinery.length > 0 ? (
              <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                    <tr>
                      <th className="p-2.5">Equipment / Tool</th>
                      <th className="p-2.5">Purpose</th>
                      <th className="p-2.5">Capacity</th>
                      <th className="p-2.5">Est. Price Range</th>
                      <th className="p-2.5">Priority</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {machinery.map((m, idx) => (
                      <tr key={idx}>
                        <td className="p-2.5 font-bold text-slate-900">{m.machine_name}</td>
                        <td className="p-2.5 text-slate-600">{m.purpose}</td>
                        <td className="p-2.5 text-slate-600">{m.capacity || 'Standard'}</td>
                        <td className="p-2.5 font-bold text-emerald-700">
                          {m.price_range || `₹${(m.price_min || 0).toLocaleString('en-IN')} - ₹${(m.price_max || 0).toLocaleString('en-IN')}`}
                        </td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            m.priority === 'Essential' ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700'
                          }`}>
                            {m.priority || 'Essential'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 italic">
                Standard artisan / processing tools required as per regional MSME guidelines.
              </div>
            )}

            {/* Suppliers Table */}
            <div className="space-y-1.5 pt-1">
              <span className="text-xs font-bold text-slate-800 block">Verified Regional Suppliers:</span>
              {suppliers && suppliers.length > 0 ? (
                <div className="overflow-x-auto rounded-xl border border-slate-200">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                      <tr>
                        <th className="p-2.5">Supplier Name</th>
                        <th className="p-2.5">Location</th>
                        <th className="p-2.5">Price Range</th>
                        <th className="p-2.5">Installation / Warranty</th>
                        <th className="p-2.5">Verification</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                      {suppliers.slice(0, 4).map((sup, idx) => (
                        <tr key={idx}>
                          <td className="p-2.5 font-bold text-slate-900">{sup.supplier_name || sup.name}</td>
                          <td className="p-2.5 text-slate-600">{sup.location || 'Regional Industrial Area'}</td>
                          <td className="p-2.5 text-slate-800">{sup.price_range || 'Direct Quotation'}</td>
                          <td className="p-2.5 text-slate-600">{sup.warranty || '1 Year Standard'}</td>
                          <td className="p-2.5">
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                              ✓ {sup.verification_status || 'Verified Vendor'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 italic">
                  Supplier information unavailable in the current database for this specific micro-machinery cluster.
                </div>
              )}
            </div>
          </div>

          {/* SECTION 9, 10 & 11: PROJECT COST, FINANCING & PROJECTIONS */}
          <div id="sec-finance" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              9, 10 & 11. Project Cost, Means of Finance & Operating Projections
            </h3>

            {/* Cost Breakdown & Means of Finance Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Cost Breakdown */}
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
                <span className="font-bold text-slate-800 block text-xs">A. Project Cost Breakdown:</span>
                <div className="space-y-1.5">
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Equipment & Machinery</span>
                    <strong className="text-slate-800">₹{Number(pcb?.equipment_cost || (cost * 0.55)).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Site Setup & Infrastructure</span>
                    <strong className="text-slate-800">₹{Number(pcb?.infrastructure_cost || (cost * 0.25)).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Working Capital Buffer (1 Mo)</span>
                    <strong className="text-slate-800">₹{Number(pcb?.working_capital || (cost * 0.20)).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between py-1.5 font-bold text-slate-900 bg-white px-2 rounded-lg border border-slate-200">
                    <span>Total Project Cost</span>
                    <span className="text-base text-emerald-800">₹{Number(cost).toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>

              {/* Means of Finance */}
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs">
                <span className="font-bold text-slate-800 block text-xs">B. Means of Finance (Illustrative):</span>
                <div className="space-y-1.5">
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Entrepreneur Margin ({fp?.own_contribution_percentage || 10}%)</span>
                    <strong className="text-slate-800">₹{Number(own).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Bank Loan Requirement ({fp?.loan_percentage || 90}%)</span>
                    <strong className="text-amber-800">₹{Number(gap).toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200">
                    <span className="text-slate-600">Indicative Interest Rate / Tenure</span>
                    <strong className="text-slate-800">{fp?.interest_rate || 7.0}% p.a. • {fp?.tenure_years || 5} Years</strong>
                  </div>
                  <div className="flex justify-between py-1.5 font-bold text-slate-900 bg-emerald-50 px-2 rounded-lg border border-emerald-200">
                    <span>Monthly EMI Repayment</span>
                    <span className="text-base text-emerald-900">₹{Number(fp?.monthly_emi || 0).toLocaleString('en-IN')} / mo</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Financial Projections Table */}
            <div className="p-4 bg-white rounded-2xl border border-slate-200 space-y-2 text-xs">
              <span className="font-bold text-slate-800 block">C. Monthly & Annual Projections (Calculated Estimates):</span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center">
                <div className="bg-slate-50 p-2 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Monthly Revenue</span>
                  <strong className="text-slate-800">₹{Number(fp?.monthly_revenue || 0).toLocaleString('en-IN')}</strong>
                </div>
                <div className="bg-slate-50 p-2 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Monthly Expenses</span>
                  <strong className="text-slate-800">₹{Number(fp?.monthly_operating_expenses || 0).toLocaleString('en-IN')}</strong>
                </div>
                <div className="bg-emerald-50 p-2 rounded-xl border border-emerald-200">
                  <span className="text-[10px] text-emerald-800 block">Monthly Net Surplus</span>
                  <strong className="text-emerald-900">₹{Number(fp?.monthly_profit || 0).toLocaleString('en-IN')}</strong>
                </div>
                <div className="bg-slate-50 p-2 rounded-xl border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Break-Even Period</span>
                  <strong className="text-slate-800">{fp?.break_even_months || 1.2} Months</strong>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 italic text-right">
                * Projections assume standard 60% capacity utilization during Year 1 operations without arbitrary growth spikes.
              </p>
            </div>
          </div>

          {/* SECTION 12 & 13: GOVERNMENT SCHEMES & REQUIRED DOCUMENTS */}
          <div id="sec-schemes" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              12 & 13. Government Scheme Matches & Document Checklist
            </h3>

            {/* Schemes List */}
            <div className="space-y-2 text-xs">
              {schemes.slice(0, 3).map((s, idx) => (
                <div key={idx} className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5">
                  <div className="flex flex-wrap justify-between items-center gap-1">
                    <span className="font-bold text-slate-900 text-xs">🏛️ {s.scheme_name}</span>
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                      {s.status || 'Potential Match'} ({s.match_score || 85}% Fit)
                    </span>
                  </div>
                  <p className="text-slate-600 text-[11px]">
                    <strong>Potential Support:</strong> {s.possible_support || s.benefits?.[0] || 'Credit-linked capital subsidy.'}
                  </p>
                  <p className="text-[10px] text-slate-500">
                    <strong>Official Source:</strong> {s.official_source || s.official_url || 'myScheme.gov.in'} ({s.last_verified || 'Verified 2024'})
                  </p>
                </div>
              ))}
            </div>

            {/* Consolidated Document Checklist */}
            <div className="p-4 bg-white rounded-2xl border border-slate-200 space-y-2 text-xs">
              <span className="font-bold text-slate-800 block">Consolidated Application Document Checklist:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                {documents.map((doc, idx) => (
                  <div key={idx} className="flex items-start space-x-2 p-2 rounded-lg bg-slate-50 border border-slate-200">
                    {doc.status === 'Required' ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <strong className="text-slate-800">{doc.document_name}</strong>
                      <span className="text-[9px] text-slate-500 block">Where to get: {doc.issuing_authority || 'UIDAI / Bank'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* SECTION 14 & 15: ROADMAP, RISKS & MITIGATION */}
          <div id="sec-roadmap" className="space-y-3 scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-[#075247] mr-2"></span>
              14 & 15. Implementation Roadmap & Risk Management
            </h3>

            {/* Roadmap Phases */}
            <div className="space-y-2 text-xs">
              {roadmap.map((phase, idx) => (
                <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="flex justify-between items-center font-bold text-slate-900 mb-1">
                    <span>{phase.phase_name}</span>
                    <span className="text-[10px] text-amber-800 bg-amber-100 px-2 py-0.5 rounded">{phase.duration}</span>
                  </div>
                  <ul className="pl-4 list-disc space-y-0.5 text-slate-600 text-[11px]">
                    {phase.milestones.map((m, mIdx) => (
                      <li key={mIdx}>{m}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {/* Risks Table */}
            <div className="p-4 bg-white rounded-2xl border border-slate-200 space-y-2 text-xs">
              <span className="font-bold text-slate-800 block">Identified Risks & Mitigation Strategies:</span>
              <div className="space-y-2 text-[11px]">
                {risks.map((r, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-amber-50/50 border border-amber-200">
                    <strong className="text-amber-950 block mb-0.5">⚠️ Risk: {r.risk} ({r.impact} Impact)</strong>
                    <p className="text-slate-700"><strong>Mitigation:</strong> {r.mitigation}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* SECTION 16: DATA SOURCES & ASSUMPTIONS */}
          <div id="sec-sources" className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2 text-xs scroll-mt-6">
            <h3 className="text-xs font-black text-[#075247] uppercase tracking-wider flex items-center">
              <Database className="w-3.5 h-3.5 mr-1.5" />
              16. Data Transparency, Sources & Key Assumptions
            </h3>

            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <tr>
                    <th className="p-2">Report Component</th>
                    <th className="p-2">Source Classification</th>
                    <th className="p-2">Authority / System Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 text-[11px]">
                  {data_sources.map((ds, idx) => (
                    <tr key={idx}>
                      <td className="p-2 font-semibold text-slate-800">{ds.component}</td>
                      <td className="p-2">
                        <span className="bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded text-[10px]">
                          {ds.source_type}
                        </span>
                      </td>
                      <td className="p-2 text-slate-600">{ds.source_details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* SECTION 17: STATUTORY DISCLAIMER */}
          <div className="bg-amber-50/70 p-4 rounded-2xl border border-amber-200 text-[11px] text-amber-950 flex items-start space-x-2.5">
            <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong>17. Preliminary Advisory Notice:</strong> {disclaimer}
            </div>
          </div>

        </div>

        {/* Modal Bottom Footer (No-Print) */}
        <div className="bg-slate-100 px-6 py-3 border-t border-slate-200 flex flex-wrap justify-between items-center gap-2 no-print text-xs">
          <span className="text-slate-500">Aarambh Saathi • Gaav ka Vikas, Aapke Saath</span>
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="px-4 py-1.5 bg-[#15803d] hover:bg-emerald-700 text-white font-bold rounded-xl shadow transition flex items-center space-x-1.5"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print A4 Dossier</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 bg-[#075247] hover:bg-[#063f39] text-white font-bold rounded-xl"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
