import React from 'react';
import { Award, CheckCircle, TrendingUp, AlertTriangle, ChevronRight, BarChart2, ShieldCheck, Sparkles } from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function RecommendationCard({
  recommendations,
  selectedBusinessId,
  onSelectBusiness,
  calculationMethod,
  language = 'en'
}) {
  const t = getTranslation(language);

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-card border border-gv-border text-center">
        <div className="w-12 h-12 rounded-full bg-emerald-50 text-gv-primary flex items-center justify-center mx-auto mb-3">
          <Award className="w-6 h-6 text-gv-accent" />
        </div>
        <h3 className="text-sm font-bold text-slate-800">{t.recTitle}</h3>
        <p className="text-xs text-slate-500 mt-1">
          {language === 'mr'
            ? 'आरंभ साथी सोबत संवाद साधून तुमचे कौशल्य, भांडवल व ठिकाण सांगा.'
            : language === 'hi'
            ? 'आरंभ साथी से बात करके अपना कौशल, पूंजी और स्थान साझा करें।'
            : 'Chat with Aarambh Saathi to share your skills, capital, and location to generate deterministic Top 3 matches.'}
        </p>
      </div>
    );
  }

  const medals = ['🥇', '🥈', '🥉'];

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-primary to-gv-secondary px-5 py-3.5 text-white flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-amber-300 border border-amber-300/30 font-bold">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold font-display flex items-center space-x-1.5">
              <span>{t.recTitle}</span>
              <span className="text-[10px] bg-amber-400/20 text-amber-300 px-1.5 py-0.5 rounded border border-amber-400/30">
                {t.recEngineBadge}
              </span>
            </h3>
            <p className="text-[11px] text-emerald-100">
              {t.recEngineDesc}
            </p>
          </div>
        </div>
      </div>

      {/* List of 3 Recommendations */}
      <div className="p-4 space-y-3.5">
        {recommendations.map((rec, index) => {
          const isSelected = selectedBusinessId === rec.business_id;

          return (
            <div
              key={rec.business_id}
              onClick={() => onSelectBusiness(rec.business_id)}
              className={`p-4 rounded-xl border-2 transition-all cursor-pointer relative ${
                isSelected
                  ? 'border-gv-primary bg-emerald-50/40 shadow-md ring-1 ring-gv-primary/30'
                  : 'border-slate-200 hover:border-gv-secondary/60 hover:bg-slate-50/70'
              }`}
            >
              {/* Top Row: Medal, Title, Score */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start space-x-2.5">
                  <span className="text-2xl flex-shrink-0">{medals[index] || '⭐'}</span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="font-bold text-slate-900 text-sm sm:text-base font-display">
                        {rec.business_name}
                      </h4>
                      {isSelected && (
                        <span className="text-[10px] bg-gv-primary text-white font-semibold px-2 py-0.5 rounded-full">
                          {language === 'mr' ? 'निवडलेला पर्याय' : language === 'hi' ? 'चयनित विकल्प' : 'Active Selection'}
                        </span>
                      )}
                    </div>
                    <span className="inline-block text-[11px] font-medium text-slate-500 mt-0.5">
                      {language === 'mr' ? 'श्रेणी: ' : language === 'hi' ? 'श्रेणी: ' : 'Category: '}
                      <strong className="text-slate-700">{rec.category}</strong>
                    </span>
                  </div>
                </div>

                {/* Score Badge */}
                <div className="text-right flex-shrink-0">
                  <div className="inline-flex items-baseline space-x-0.5 bg-gradient-to-br from-gv-dark to-gv-primary text-white px-2.5 py-1 rounded-lg shadow-xs">
                    <span className="text-base font-extrabold text-amber-300">{rec.overall_score}</span>
                    <span className="text-[10px] text-slate-300 font-normal">/100</span>
                  </div>
                  <span className="block text-[9px] text-slate-400 font-medium mt-0.5 uppercase tracking-wider">
                    {language === 'mr' ? 'जुळणी गुण' : language === 'hi' ? 'मैच स्कोर' : 'Match Score'}
                  </span>
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-600 mt-2 line-clamp-2 leading-relaxed">
                {rec.description}
              </p>

              {/* Financial Snapshot */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3 pt-2.5 border-t border-slate-200/80 text-[11px]">
                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'लागणारे भांडवल' : language === 'hi' ? 'आवश्यक पूंजी' : 'Recommended Investment'}
                  </span>
                  <span className="font-bold text-slate-800">
                    ₹{Number(rec.required_investment).toLocaleString('en-IN')}
                  </span>
                </div>
                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">{t.ownCapitalContrib}</span>
                  <span className="font-bold text-emerald-700">
                    ₹{Number(rec.user_capital).toLocaleString('en-IN')}
                  </span>
                </div>
                <div className="col-span-2 sm:col-span-1 bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'व्यवसाय वाढ क्षमता' : language === 'hi' ? 'व्यापार विस्तार क्षमता' : 'Scalability'}
                  </span>
                  <span className="font-bold text-amber-800">{rec.scalability}</span>
                </div>
              </div>

              {/* 5-Factor Deterministic Breakdown Bars */}
              <div className="mt-3 bg-white p-2.5 rounded-lg border border-slate-200/70 space-y-1.5 text-[10px]">
                <div className="flex justify-between font-semibold text-slate-600 mb-1">
                  <span>{language === 'mr' ? 'निर्णय घटक विश्लेषण:' : language === 'hi' ? 'निर्णय कारक विश्लेषण:' : 'Deterministic Factor Breakdown:'}</span>
                  <span className="text-gv-primary">Aarambh Saathi Engine</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                  {/* Skill (25) */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">
                      {language === 'mr' ? 'कौशल्य जुळणी (२५%):' : language === 'hi' ? 'कौशल मैच (25%):' : 'Skill Match (25%):'}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-600 h-full rounded-full"
                          style={{ width: `${(rec.breakdown.skill_match_score / 25) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{rec.breakdown.skill_match_score}/25</span>
                    </div>
                  </div>

                  {/* Capital (25) */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">
                      {language === 'mr' ? 'भांडवल जुळणी (२५%):' : language === 'hi' ? 'पूंजी मैच (25%):' : 'Capital Match (25%):'}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-amber-500 h-full rounded-full"
                          style={{ width: `${(rec.breakdown.capital_match_score / 25) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{rec.breakdown.capital_match_score}/25</span>
                    </div>
                  </div>

                  {/* Resource (20) */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">
                      {language === 'mr' ? 'साधने जुळणी (२०%):' : language === 'hi' ? 'संसाधन मैच (20%):' : 'Resource Match (20%):'}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-blue-500 h-full rounded-full"
                          style={{ width: `${(rec.breakdown.resource_match_score / 20) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{rec.breakdown.resource_match_score}/20</span>
                    </div>
                  </div>

                  {/* Market (20) */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">
                      {language === 'mr' ? 'बाजार मागणी (२०%):' : language === 'hi' ? 'बाजार मांग (20%):' : 'Market Potential (20%):'}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-500 h-full rounded-full"
                          style={{ width: `${(rec.breakdown.market_potential_score / 20) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{rec.breakdown.market_potential_score}/20</span>
                    </div>
                  </div>

                  {/* Risk (10) */}
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">
                      {language === 'mr' ? 'जोखीम घटक (१०%):' : language === 'hi' ? 'जोखिम प्रोफ़ाइल (10%):' : 'Risk Profile (10%):'}
                    </span>
                    <div className="flex items-center space-x-1.5">
                      <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-teal-500 h-full rounded-full"
                          style={{ width: `${(rec.breakdown.risk_score / 10) * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{rec.breakdown.risk_score}/10</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Explainable Why it matches */}
              <div className="mt-3 space-y-1">
                <span className="text-[11px] font-semibold text-slate-700 block">
                  {language === 'mr' ? 'हा पर्याय योग्य का आहे:' : language === 'hi' ? 'यह विकल्प उपयुक्त क्यों है:' : 'Why this matches:'}
                </span>
                {rec.why_matches.map((reason, idx) => (
                  <div key={idx} className="flex items-start space-x-1.5 text-[11px] text-slate-600">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>

              {/* Opportunity & Risk flags */}
              <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-col sm:flex-row gap-2 text-[10px]">
                <div className="flex-1 flex items-center space-x-1 text-emerald-800 bg-emerald-50/70 p-1.5 rounded">
                  <TrendingUp className="w-3 h-3 flex-shrink-0 text-emerald-600" />
                  <span>
                    <strong>{language === 'mr' ? 'मुख्य संधी:' : language === 'hi' ? 'मुख्य अवसर:' : 'Opportunity:'}</strong> {rec.main_opportunity}
                  </span>
                </div>
                <div className="flex-1 flex items-center space-x-1 text-amber-900 bg-amber-50/70 p-1.5 rounded">
                  <AlertTriangle className="w-3 h-3 flex-shrink-0 text-amber-600" />
                  <span>
                    <strong>{language === 'mr' ? 'मुख्य जोखीम:' : language === 'hi' ? 'मुख्य जोखिम:' : 'Main Risk:'}</strong> {rec.main_risk}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

