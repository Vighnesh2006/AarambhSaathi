import React, { useState, useEffect } from 'react';
import { IndianRupee, Calculator, ShieldAlert, Sparkles, Sliders, Check, TrendingUp, Calendar, Clock } from 'lucide-react';
import { getFinancialPlan } from '../services/api';
import { getTranslation } from '../services/translations';

export default function FinancialSummary({ initialCost, userCapital, onPlanUpdated, language = 'en' }) {
  const t = getTranslation(language);
  const [cost, setCost] = useState(initialCost || 140000);
  const [userContrib, setUserContrib] = useState(userCapital || 15000);
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Sync when initialCost or userCapital change
  useEffect(() => {
    if (initialCost) setCost(initialCost);
    if (userCapital !== undefined && userCapital !== null) setUserContrib(userCapital);
  }, [initialCost, userCapital]);

  // Recalculate financial plan on backend whenever cost or user contribution changes
  useEffect(() => {
    const fetchPlan = async () => {
      setIsLoading(true);
      try {
        const res = await getFinancialPlan({
          project_cost: Number(cost),
          user_contribution: Number(userContrib)
        });
        setPlan(res);
        if (onPlanUpdated) onPlanUpdated(res);
      } catch (err) {
        console.error('Error calculating financial plan:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPlan();
  }, [cost, userContrib]);

  const isMicroFinance = cost <= 140000;

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-dark via-gv-primary to-gv-secondary px-5 py-3.5 text-white flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-400/20 text-amber-300 flex items-center justify-center text-xs font-bold border border-amber-300/40">
            <Calculator className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold font-display flex items-center space-x-2">
              <span>{t.financeTitle}</span>
              <span className="text-[10px] bg-amber-400 text-slate-950 font-extrabold px-2 py-0.5 rounded shadow-xs">
                {t.financeBadge}
              </span>
            </h3>
            <p className="text-[11px] text-emerald-100">
              {t.financeSub}
            </p>
          </div>
        </div>

        {/* Dynamic Scheme Tier Tag */}
        <div className="text-right">
          <span
            className={`inline-block text-[10px] font-bold px-2.5 py-1 rounded-full border shadow-xs ${
              isMicroFinance
                ? 'bg-emerald-400/20 text-emerald-200 border-emerald-400/40'
                : 'bg-amber-400/20 text-amber-200 border-amber-400/40'
            }`}
          >
            {isMicroFinance
              ? (language === 'mr' ? '🌿 सूक्ष्म वित्त (≤ ₹१.४० लाख)' : language === 'hi' ? '🌿 माइक्रो फाइनेंस (≤ ₹1.40 लाख)' : '🌿 Micro Finance (≤ ₹1.40L)')
              : (language === 'mr' ? '🏢 व्यावसायिक मुदत कर्ज (> ₹१.४० लाख)' : language === 'hi' ? '🏢 टर्म लोन (> ₹1.40 लाख)' : '🏢 Term Loan (> ₹1.40L)')}
          </span>
        </div>
      </div>

      <div className="p-4 sm:p-5 space-y-4">
        {/* Tier Specification Notice */}
        <div
          className={`p-3 rounded-xl border text-xs flex items-start space-x-2.5 ${
            isMicroFinance
              ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
              : 'bg-amber-50/80 border-amber-200 text-amber-900'
          }`}
        >
          <Sparkles className="w-4 h-4 flex-shrink-0 text-amber-600 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="block font-bold">
              {isMicroFinance
                ? (language === 'mr' ? 'राष्ट्रीय सूक्ष्म वित्त कर्ज योजना लागू:' : language === 'hi' ? 'राष्ट्रीय माइक्रो फाइनेंस योजना लागू:' : 'National Micro Finance Scheme Tier Applied:')
                : (language === 'mr' ? 'व्यावसायिक मुदत कर्ज योजना लागू:' : language === 'hi' ? 'टर्म लोन योजना लागू:' : 'Commercial Term Loan Tier Applied:')}
            </strong>
            {isMicroFinance ? (
              <span>
                {language === 'mr'
                  ? 'एकूण खर्च ₹१.४० लाखापर्यंत • कमाल कर्ज ९०% पर्यंत • ६.५% वार्षिक व्याज • ३ वर्षे मुदत'
                  : language === 'hi'
                  ? 'कुल लागत ₹1.40 लाख तक • अधिकतम लोन 90% तक • 6.5% वार्षिक ब्याज • 3 वर्ष अवधि'
                  : 'Project cost ≤ ₹1.40 Lakh • Max loan ₹1.25 Lakh (up to 90%) • 6.5% p.a. interest • 3-year repayment'}
              </span>
            ) : (
              <span>
                {language === 'mr'
                  ? 'एकूण खर्च ₹१.४० लाखांपेक्षा जास्त • कमाल कर्ज ९०% पर्यंत • ८.०% वार्षिक व्याज • ७ वर्षे मुदत'
                  : language === 'hi'
                  ? 'कुल लागत ₹1.40 लाख से अधिक • अधिकतम लोन 90% तक • 8.0% वार्षिक ब्याज • 7 वर्ष अवधि'
                  : 'Project cost > ₹1.40 Lakh to ₹50 Lakh • Max loan ₹45 Lakh (up to 90%) • 8.0% p.a. interest • 7-year repayment'}
              </span>
            )}
          </div>
        </div>

        {/* Interactive Sliders / Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs">
          <div>
            <div className="flex justify-between items-center mb-1 font-semibold text-slate-700">
              <label>{t.totalProjCost} (₹)</label>
              <span className="text-gv-primary font-bold">₹{Number(cost).toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="20000"
              max="500000"
              step="5000"
              value={cost}
              onChange={(e) => setCost(Number(e.target.value))}
              className="w-full accent-gv-primary cursor-pointer"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1 font-semibold text-slate-700">
              <label>{t.ownCapitalContrib}</label>
              <span className="text-emerald-700 font-bold">₹{Number(userContrib).toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min="0"
              max={cost}
              step="5000"
              value={userContrib}
              onChange={(e) => setUserContrib(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>
        </div>

        {/* Calculated Financial Metrics */}
        {plan && (
          <div className="space-y-3">
            {/* Top Stat Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-[10px] text-slate-500 font-medium block">{t.ownCapitalContrib}</span>
                <p className="text-sm font-bold text-slate-800 mt-0.5">
                  ₹{Number(plan.own_contribution).toLocaleString('en-IN')}
                </p>
                <span className="text-[10px] text-emerald-600 font-semibold">({plan.own_contribution_percentage}%)</span>
              </div>

              <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-[10px] text-slate-500 font-medium block">{t.bankLoanSubsidy}</span>
                <p className="text-sm font-bold text-gv-primary mt-0.5">
                  ₹{Number(plan.required_loan).toLocaleString('en-IN')}
                </p>
                <span className="text-[10px] text-gv-secondary font-semibold">({plan.loan_percentage}%)</span>
              </div>

              <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
                <span className="text-[10px] text-slate-500 font-medium block">
                  {language === 'mr' ? 'मासिक हप्ता (EMI)' : language === 'hi' ? 'मासिक ईएमआई (EMI)' : 'Monthly EMI'}
                </span>
                <p className="text-sm font-bold text-amber-700 mt-0.5">
                  ₹{Number(plan.monthly_emi).toLocaleString('en-IN')}/mo
                </p>
                <span className="text-[10px] text-slate-500">@ {plan.interest_rate}% p.a.</span>
              </div>

              <div className="bg-emerald-50/70 p-3 rounded-xl border border-emerald-200 shadow-2xs">
                <span className="text-[10px] text-emerald-800 font-medium block">{t.monthlyNetProfit}</span>
                <p className="text-sm font-extrabold text-emerald-900 mt-0.5">
                  ₹{Number(plan.monthly_profit).toLocaleString('en-IN')}
                </p>
                <span className="text-[10px] text-emerald-700 font-semibold">After EMI</span>
              </div>
            </div>

            {/* Detailed Structure Table */}
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 text-xs space-y-1.5">
              <div className="flex justify-between py-1 border-b border-slate-200 text-slate-600">
                <span className="flex items-center"><Calendar className="w-3.5 h-3.5 mr-1 text-slate-400" /> Repayment Tenure:</span>
                <strong className="text-slate-800">{plan.tenure_years} Years ({plan.tenure_months} Months)</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200 text-slate-600">
                <span className="flex items-center"><Clock className="w-3.5 h-3.5 mr-1 text-slate-400" /> Moratorium Period:</span>
                <strong className="text-slate-800">{plan.moratorium_months} Months (No principal repayment)</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200 text-slate-600">
                <span>Estimated Monthly Turnover:</span>
                <strong className="text-slate-800">₹{Number(plan.monthly_revenue).toLocaleString('en-IN')}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200 text-slate-600">
                <span>Estimated Monthly Operating Expenses:</span>
                <strong className="text-slate-800">₹{Number(plan.monthly_operating_expenses).toLocaleString('en-IN')}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-200 text-slate-600">
                <span>Annual Net Profit (Estimated):</span>
                <strong className="text-emerald-700 font-bold">₹{Number(plan.annual_profit).toLocaleString('en-IN')} / year</strong>
              </div>
              <div className="flex justify-between py-1 text-slate-600">
                <span>Capital Break-Even Period:</span>
                <strong className="text-amber-800 font-bold">~ {plan.break_even_months} Months</strong>
              </div>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="flex items-start space-x-2 text-[10px] text-slate-500 bg-amber-50/50 p-2.5 rounded-lg border border-amber-200/60">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Statutory Notice:</strong> Financial calculations follow official micro-enterprise lending guidelines for advisory structuring. Final credit sanction, interest concessions, and disbursement are subject to bank appraisal and official channelizing agency approvals.
          </span>
        </div>
      </div>
    </div>
  );
}
