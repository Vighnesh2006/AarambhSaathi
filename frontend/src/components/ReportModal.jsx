import React, { useRef } from 'react';
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
  Sprout
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function ReportModal({
  report,
  isOpen,
  onClose,
  isProfileReady,
  onStartChat,
  language = 'en'
}) {
  const t = getTranslation(language);
  const printRef = useRef();

  if (!isOpen) return null;

  // If report is not ready or profile incomplete, show a friendly interactive helper state
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
                : 'Your customized 90-Day Detailed Project Report (DPR) requires your location, skills, and investment details so the AI can calculate accurate loan EMIs, profit margins, and government subsidies.'}
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

  const {
    report_id,
    created_at,
    entrepreneur_profile: p,
    recommended_business: b,
    local_feasibility: f,
    financial_plan: fp,
    relevant_schemes: schemes,
    explainable_reasons,
    action_plan_90_days,
    disclaimer
  } = report;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Top Action Bar (No-Print) */}
        <div className="bg-[#063f39] text-white px-6 py-4 flex items-center justify-between border-b border-[#0f5349] no-print">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-400/20 text-amber-300 flex items-center justify-center border border-amber-300/40">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold font-display text-white">
                Aarambh Saathi {t.journey5Sub}
              </h2>
              <p className="text-xs text-emerald-200">Ref ID: {report_id}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="flex items-center space-x-1.5 px-4 py-2 bg-[#15803d] hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow transition"
              title="Print or Save as PDF"
            >
              <Printer className="w-4 h-4" />
              <span>{language === 'mr' ? 'प्रिंट / पीडीएफ डाउनलोड' : language === 'hi' ? 'प्रिंट / पीडीएफ डाउनलोड' : 'Print / Download PDF'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-300 hover:text-white hover:bg-white/10 rounded-xl transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Report Body */}
        <div ref={printRef} className="p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-800 text-xs sm:text-sm print:p-0">
          
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
                Gaav ka Vikas, Aapke Saath • Micro-Enterprise Advisory & Financial Structuring Model
              </p>
            </div>

            <div className="text-right text-xs text-slate-500">
              <p><strong>Report ID:</strong> {report_id}</p>
              <p><strong>Date of Generation:</strong> {created_at}</p>
              <span className="inline-block bg-emerald-100 text-[#075247] font-bold px-2 py-0.5 rounded text-[10px] mt-1 border border-emerald-200">
                Verified Advisory Assessment
              </span>
            </div>
          </div>

          {/* Section 1: Entrepreneur Profile */}
          <div className="bg-[#f8faf9] p-4 rounded-2xl border border-slate-200">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider mb-2.5 flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              1. Entrepreneur & Location Profile
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-slate-400 block text-[10px]">Entrepreneur Name</span>
                <strong className="text-slate-800">{p?.name || 'Rural Micro-Entrepreneur'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Location / Cluster</span>
                <strong className="text-slate-800">{[p?.location, p?.district, p?.state].filter(Boolean).join(', ') || 'Rural District'}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Available Margin Capital</span>
                <strong className="text-emerald-700">₹{Number(p?.capital || 0).toLocaleString('en-IN')}</strong>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">Existing Experience</span>
                <strong className="text-slate-800">{p?.experience || 'Practicing artisan/farmer'}</strong>
              </div>
            </div>
          </div>

          {/* Section 2: Recommended Business & Explainability */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              2. Recommended Micro-Enterprise & Decision Explainability
            </h3>

            <div className="p-4 rounded-2xl border-2 border-emerald-300 bg-emerald-50/40">
              <div className="flex flex-wrap justify-between items-start gap-2 mb-2">
                <div>
                  <h4 className="text-base font-bold text-[#072a24] font-display">{b?.business_name}</h4>
                  <p className="text-xs text-slate-600">Category: <strong>{b?.category}</strong></p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold bg-[#075247] text-amber-300 px-2.5 py-1 rounded-lg">
                    Match Score: {b?.overall_score}/100
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed mb-3">{b?.description}</p>

              {/* Explainable Factors */}
              <div className="bg-white p-3 rounded-xl border border-emerald-200 space-y-1.5">
                <span className="font-bold text-xs text-emerald-950 block">Why Aarambh Saathi Recommends This:</span>
                {explainable_reasons?.map((reason, i) => (
                  <div key={i} className="flex items-start space-x-1.5 text-xs text-slate-700">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 3: Hyper-Local Feasibility */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              3. Hyper-Local Feasibility Analysis
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Feasibility Score</span>
                <strong className="text-base text-teal-800">{f?.feasibility_score}/100</strong>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Local Market Demand</span>
                <strong className="text-slate-800">{f?.market_opportunity}</strong>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Competition Density</span>
                <strong className="text-slate-800">{f?.competition_level}</strong>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-slate-400 block text-[10px]">Resource Availability</span>
                <strong className="text-slate-800">{f?.resource_availability}</strong>
              </div>
            </div>
          </div>

          {/* Section 4: Financial Structure & EMI Plan */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              4. Financial Structuring & Credit Model (Micro-Enterprise Lending Framework)
            </h3>

            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200">
              <div className="bg-white p-2.5 rounded-xl border border-amber-300 text-xs font-semibold text-slate-800 mb-3 flex items-center justify-between">
                <span>Applied Scheme Tier: <strong>{fp?.scheme_tier}</strong></span>
                <span className="text-amber-800 bg-amber-100 px-2 py-0.5 rounded text-[10px]">
                  Interest: {fp?.interest_rate}% p.a.
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="bg-white p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 block text-[10px]">Total Project Cost</span>
                  <strong className="text-slate-900 text-sm">₹{Number(fp?.project_cost || 0).toLocaleString('en-IN')}</strong>
                </div>
                <div className="bg-white p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 block text-[10px]">Own Margin Contribution</span>
                  <strong className="text-slate-900 text-sm">₹{Number(fp?.own_contribution || 0).toLocaleString('en-IN')} ({fp?.own_contribution_percentage}%)</strong>
                </div>
                <div className="bg-white p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 block text-[10px]">Sanctionable Bank Loan</span>
                  <strong className="text-[#075247] text-sm">₹{Number(fp?.required_loan || 0).toLocaleString('en-IN')} ({fp?.loan_percentage}%)</strong>
                </div>
                <div className="bg-white p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 block text-[10px]">Monthly EMI Installment</span>
                  <strong className="text-amber-700 text-sm">₹{Number(fp?.monthly_emi || 0).toLocaleString('en-IN')} / month</strong>
                </div>
                <div className="bg-white p-2.5 rounded-xl border border-slate-200">
                  <span className="text-slate-400 block text-[10px]">Repayment Tenure</span>
                  <strong className="text-slate-800">{fp?.tenure_years} Years ({fp?.moratorium_months} mo moratorium)</strong>
                </div>
                <div className="bg-emerald-50 p-2.5 rounded-xl border border-emerald-200">
                  <span className="text-emerald-800 block text-[10px]">Estimated Monthly Net Profit</span>
                  <strong className="text-emerald-900 text-sm">₹{Number(fp?.monthly_profit || 0).toLocaleString('en-IN')}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Section 5: Government Schemes */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              5. Matched Government Credit & Subsidy Programs
            </h3>

            <div className="space-y-2 text-xs">
              {schemes?.map((s, idx) => (
                <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="flex justify-between items-center font-bold text-slate-800 mb-1">
                    <span>🏛️ {s.scheme_name}</span>
                    <span className="text-[10px] text-[#075247] bg-emerald-100 px-2 py-0.5 rounded">Eligible Category</span>
                  </div>
                  <p className="text-slate-600 text-[11px] mb-1"><strong>Benefit:</strong> {s.possible_support}</p>
                  <p className="text-slate-500 text-[10px]"><strong>Required Documents:</strong> {s.required_documents?.join(', ')}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 6: 90-Day Structured Action Plan */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#075247] uppercase tracking-wider flex items-center">
              <span className="w-2 h-2 rounded-full bg-[#075247] mr-1.5"></span>
              6. Structured 90-Day Execution Action Plan
            </h3>

            <div className="space-y-3 text-xs">
              {action_plan_90_days && Object.entries(action_plan_90_days).map(([phase, tasks], idx) => (
                <div key={idx} className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200">
                  <h4 className="font-bold text-[#072a24] text-xs mb-2 flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-amber-600" />
                    <span>{phase}</span>
                  </h4>
                  <ul className="space-y-1 pl-4 list-disc text-slate-700 text-[11px]">
                    {tasks.map((task, tIdx) => (
                      <li key={tIdx} className="leading-relaxed">{task}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Section 7: Statutory Disclaimer */}
          <div className="bg-amber-50/60 p-3.5 rounded-2xl border border-amber-200/80 text-[10px] text-amber-950 flex items-start space-x-2">
            <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong>Aarambh Saathi Advisory Notice:</strong> {disclaimer || "Aarambh Saathi provides indicative decision support and financial structuring. Final loan sanctions and subsidies depend on official bank and nodal agency appraisal."}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-100 px-6 py-3 border-t border-slate-200 flex justify-between items-center no-print text-xs">
          <span className="text-slate-500">Aarambh Saathi • Gaav ka Vikas, Aapke Saath</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#075247] hover:bg-[#063f39] text-white font-bold rounded-xl"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
