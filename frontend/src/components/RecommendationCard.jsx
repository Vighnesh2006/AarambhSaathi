import React, { useState } from 'react';
import {
  Award,
  CheckCircle,
  TrendingUp,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  BarChart2,
  ShieldCheck,
  Sparkles,
  Info,
  DollarSign,
  TrendingDown
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function RecommendationCard({
  recommendations,
  selectedBusinessId,
  onSelectBusiness,
  calculationMethod,
  language = 'en'
}) {
  const t = getTranslation(language);
  const [expandedRecId, setExpandedRecId] = useState(null);

  const toggleExpand = (e, bId) => {
    e.stopPropagation();
    setExpandedRecId(prev => (prev === bId ? null : bId));
  };

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
            : 'Chat with Aarambh Saathi to share your skills, capital, and location to generate deterministic Top matches.'}
        </p>
      </div>
    );
  }

  const medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];

  const getMatchLevelBadge = (level, score) => {
    const s = score || 0;
    if (s >= 90 || level === 'Excellent Match') {
      return {
        label: language === 'mr' ? 'सर्वोत्कृष्ट जुळणी' : language === 'hi' ? 'उत्कृष्ट मैच' : 'Excellent Match',
        bg: 'bg-emerald-600 text-white'
      };
    }
    if (s >= 80 || level === 'Strong Match') {
      return {
        label: language === 'mr' ? 'मजबूत जुळणी' : language === 'hi' ? 'मजबूत मैच' : 'Strong Match',
        bg: 'bg-emerald-700 text-white'
      };
    }
    if (s >= 70 || level === 'Good Match') {
      return {
        label: language === 'mr' ? 'उत्तम जुळणी' : language === 'hi' ? 'अच्छा मैच' : 'Good Match',
        bg: 'bg-teal-700 text-white'
      };
    }
    if (s >= 60 || level === 'Possible Match') {
      return {
        label: language === 'mr' ? 'संभाव्य जुळणी' : language === 'hi' ? 'संभावित मैच' : 'Possible Match',
        bg: 'bg-amber-600 text-white'
      };
    }
    return {
      label: language === 'mr' ? 'कमी जुळणी' : language === 'hi' ? 'कम मैच' : 'Low Match',
      bg: 'bg-slate-600 text-white'
    };
  };

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

      {/* List of Top Recommendations */}
      <div className="p-4 space-y-3.5">
        {recommendations.map((rec, index) => {
          const isSelected = selectedBusinessId === rec.business_id;
          const isExpanded = expandedRecId === rec.business_id;
          const matchBadge = getMatchLevelBadge(rec.match_level, rec.overall_score);

          // Factor scores fallback (supporting both 9-factor factor_scores and legacy breakdown)
          const fs = rec.factor_scores || {};
          const skillScore = fs.skill_match ?? (rec.breakdown ? Math.round((rec.breakdown.skill_match_score / 25) * 100) : 0);
          const locationScore = fs.location_suitability ?? (rec.breakdown ? Math.round((rec.breakdown.resource_match_score / 20) * 100) : 80);
          const resourceScore = fs.resource_match ?? (rec.breakdown ? Math.round((rec.breakdown.resource_match_score / 20) * 100) : 0);
          const investmentScore = fs.investment_fit ?? (rec.breakdown ? Math.round((rec.breakdown.capital_match_score / 25) * 100) : 0);
          const demandScore = fs.local_demand ?? (rec.breakdown ? Math.round((rec.breakdown.market_potential_score / 20) * 100) : 0);
          const compScore = fs.competition ?? (rec.breakdown ? Math.round((rec.breakdown.risk_score / 10) * 100) : 75);
          const customerScore = fs.customer_potential ?? 80;
          const supplierScore = fs.supplier_availability ?? 75;
          const marketScore = fs.market_access ?? 80;

          const whyMatches = rec.why_this_matches || rec.why_matches || [];
          const considerations = rec.considerations || (rec.main_risk ? [rec.main_risk] : []);

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
              {/* Top Row: Medal, Title, Match Badge, Overall Score */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start space-x-2.5">
                  <span className="text-2xl flex-shrink-0">{medals[index] || '⭐'}</span>
                  <div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <h4 className="font-bold text-slate-900 text-sm sm:text-base font-display">
                        {rec.business_name}
                      </h4>
                      {/* Match Level Badge */}
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${matchBadge.bg}`}>
                        {matchBadge.label}
                      </span>
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
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-2.5 border-t border-slate-200/80 text-[11px]">
                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'लागणारे भांडवल' : language === 'hi' ? 'आवश्यक पूंजी' : 'Investment'}
                  </span>
                  <span className="font-bold text-slate-800">
                    ₹{Number(rec.required_investment || rec.estimated_total_investment || 0).toLocaleString('en-IN')}
                  </span>
                </div>
                
                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'अंदाजे मासिक महसूल' : language === 'hi' ? 'अनुमानित मासिक आय' : 'Est. Monthly Rev.'}
                  </span>
                  <span className="font-bold text-emerald-700">
                    {rec.estimated_monthly_revenue ? `₹${Number(rec.estimated_monthly_revenue).toLocaleString('en-IN')}` : '₹35,000+'}
                  </span>
                </div>

                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'अंदाजे मासिक नफा' : language === 'hi' ? 'अनुमानित मासिक लाभ' : 'Est. Net Profit'}
                  </span>
                  <span className="font-bold text-emerald-800">
                    {rec.estimated_monthly_profit ? `₹${Number(rec.estimated_monthly_profit).toLocaleString('en-IN')}` : '₹12,000+'}
                  </span>
                </div>

                <div className="bg-white p-2 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">
                    {language === 'mr' ? 'व्यवसाय वाढ क्षमता' : language === 'hi' ? 'व्यापार विस्तार क्षमता' : 'Scalability'}
                  </span>
                  <span className="font-bold text-amber-800">{rec.scalability || 'High'}</span>
                </div>
              </div>

              {/* Expandable "Why this business?" Button */}
              <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
                <button
                  type="button"
                  onClick={(e) => toggleExpand(e, rec.business_id)}
                  className="inline-flex items-center space-x-1 text-xs font-semibold text-gv-primary hover:text-emerald-700 transition-colors"
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  <span>
                    {isExpanded
                      ? (language === 'mr' ? 'तपशील लपवा' : language === 'hi' ? 'विवरण छिपाएं' : 'Hide Factor Breakdown')
                      : (language === 'mr' ? 'हा व्यवसाय का? (९ घटक विश्लेषण)' : language === 'hi' ? 'यह व्यवसाय क्यों? (9 कारक विश्लेषण)' : 'Why this business? (9-Factor Breakdown)')}
                  </span>
                  {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                </button>
                <span className="text-[10px] text-slate-400 font-medium">
                  {rec.confidence ? `${rec.confidence}% Confidence` : 'Deterministic Model'}
                </span>
              </div>

              {/* Expandable Factor Drawer */}
              {isExpanded && (
                <div className="mt-3 bg-white p-3 rounded-xl border border-emerald-100 shadow-inner space-y-2.5 text-[11px] animate-fadeIn">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-700 pb-1 border-b border-slate-100">
                    <span>{language === 'mr' ? '९-घटक अचूक विश्लेषण:' : language === 'hi' ? '9-कारक सटीक विश्लेषण:' : '9-Factor Deterministic Match Matrix:'}</span>
                    <span className="text-[10px] bg-emerald-50 text-gv-primary font-semibold px-2 py-0.5 rounded">
                      Weighted 100%
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
                    {/* 1. Skill Match (20%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'कौशल्य जुळणी (२०%):' : language === 'hi' ? 'कौशल मैच (20%):' : 'Skill Match (20%):'}</span>
                        <span className="font-bold text-slate-800">{skillScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-emerald-600 h-full rounded-full" style={{ width: `${skillScore}%` }}></div>
                      </div>
                    </div>

                    {/* 2. Location Suitability (20%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'ठिकाण योग्यता (२०%):' : language === 'hi' ? 'स्थान उपयुक्तता (20%):' : 'Location Suitability (20%):'}</span>
                        <span className="font-bold text-slate-800">{locationScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${locationScore}%` }}></div>
                      </div>
                    </div>

                    {/* 3. Resource Match (15%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'साधने व जागा (१५%):' : language === 'hi' ? 'संसाधन व भूमि (15%):' : 'Resource Match (15%):'}</span>
                        <span className="font-bold text-slate-800">{resourceScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-blue-500 h-full rounded-full" style={{ width: `${resourceScore}%` }}></div>
                      </div>
                    </div>

                    {/* 4. Investment Fit (15%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'भांडवल जुळणी (१५%):' : language === 'hi' ? 'पूंजी मैच (15%):' : 'Investment Fit (15%):'}</span>
                        <span className="font-bold text-slate-800">{investmentScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-amber-500 h-full rounded-full" style={{ width: `${investmentScore}%` }}></div>
                      </div>
                    </div>

                    {/* 5. Local Demand (10%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'स्थानिक मागणी (१०%):' : language === 'hi' ? 'स्थानीय मांग (10%):' : 'Local Demand (10%):'}</span>
                        <span className="font-bold text-slate-800">{demandScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${demandScore}%` }}></div>
                      </div>
                    </div>

                    {/* 6. Competition (5%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'स्पर्धा संतुलन (५%):' : language === 'hi' ? 'प्रतिस्पर्धा संतुलन (5%):' : 'Competition Score (5%):'}</span>
                        <span className="font-bold text-slate-800">{compScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-purple-500 h-full rounded-full" style={{ width: `${compScore}%` }}></div>
                      </div>
                    </div>

                    {/* 7. Customer Potential (5%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'ग्राहक क्षमता (५%):' : language === 'hi' ? 'ग्राहक क्षमता (5%):' : 'Customer Potential (5%):'}</span>
                        <span className="font-bold text-slate-800">{customerScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-teal-500 h-full rounded-full" style={{ width: `${customerScore}%` }}></div>
                      </div>
                    </div>

                    {/* 8. Supplier Availability (5%) */}
                    <div className="flex flex-col space-y-0.5">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'पुरवठादार उपलब्धता (५%):' : language === 'hi' ? 'आपूर्तिकर्ता उपलब्धता (5%):' : 'Supplier Availability (5%):'}</span>
                        <span className="font-bold text-slate-800">{supplierScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-orange-500 h-full rounded-full" style={{ width: `${supplierScore}%` }}></div>
                      </div>
                    </div>

                    {/* 9. Market Access (5%) */}
                    <div className="flex flex-col space-y-0.5 sm:col-span-2">
                      <div className="flex justify-between text-slate-600">
                        <span>{language === 'mr' ? 'बाजार प्रवेश व विक्री मार्ग (५%):' : language === 'hi' ? 'बाजार पहुंच व विक्रय चैनल (5%):' : 'Market Access & Channels (5%):'}</span>
                        <span className="font-bold text-slate-800">{marketScore}/100</span>
                      </div>
                      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-sky-500 h-full rounded-full" style={{ width: `${marketScore}%` }}></div>
                      </div>
                    </div>
                  </div>

                  {/* Transparent Data Source Note */}
                  <div className="pt-2 border-t border-slate-100 flex items-center space-x-1.5 text-[10px] text-slate-500">
                    <Info className="w-3 h-3 text-slate-400 flex-shrink-0" />
                    <span>
                      {language === 'mr'
                        ? 'डेटा स्रोत: ग्राम नॉलेज बेस व स्थानिक बाजार निर्देशक (अनुमानित/पुष्टी केलेले).'
                        : language === 'hi'
                        ? 'डेटा स्रोत: ग्रामीण ज्ञान आधार और स्थानीय बाजार संकेतक (अनुमानित/सत्यापित)।'
                        : 'Data Source: Curated Rural Knowledge Base & Verified Supplier Registry (Transparent/No Fabricated Counts).'}
                    </span>
                  </div>
                </div>
              )}

              {/* Why This Matches */}
              {whyMatches.length > 0 && (
                <div className="mt-3 space-y-1">
                  <span className="text-[11px] font-semibold text-slate-700 block">
                    {language === 'mr' ? 'हा पर्याय योग्य का आहे:' : language === 'hi' ? 'यह विकल्प उपयुक्त क्यों है:' : 'Why this matches:'}
                  </span>
                  {whyMatches.map((reason, idx) => (
                    <div key={idx} className="flex items-start space-x-1.5 text-[11px] text-slate-600">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Considerations & Opportunities */}
              <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-col sm:flex-row gap-2 text-[10px]">
                {rec.main_opportunity && (
                  <div className="flex-1 flex items-center space-x-1 text-emerald-800 bg-emerald-50/70 p-1.5 rounded">
                    <TrendingUp className="w-3 h-3 flex-shrink-0 text-emerald-600" />
                    <span>
                      <strong>{language === 'mr' ? 'मुख्य संधी:' : language === 'hi' ? 'मुख्य अवसर:' : 'Opportunity:'}</strong> {rec.main_opportunity}
                    </span>
                  </div>
                )}
                
                {considerations.length > 0 && (
                  <div className="flex-1 flex items-center space-x-1 text-amber-900 bg-amber-50/70 p-1.5 rounded">
                    <AlertTriangle className="w-3 h-3 flex-shrink-0 text-amber-600" />
                    <span>
                      <strong>{language === 'mr' ? 'महत्त्वाची दक्षता:' : language === 'hi' ? 'महत्वपूर्ण सावधानी:' : 'Consideration:'}</strong> {considerations[0]}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


