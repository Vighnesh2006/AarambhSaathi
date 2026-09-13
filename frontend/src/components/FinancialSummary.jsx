import React, { useState, useEffect } from 'react';
import { 
  IndianRupee, 
  Calculator, 
  ShieldAlert, 
  Sparkles, 
  Sliders, 
  Check, 
  TrendingUp, 
  Calendar, 
  Clock, 
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Building2,
  PieChart,
  Layers,
  HelpCircle,
  Coins
} from 'lucide-react';
import { getFinancialPlan } from '../services/api';
import { getTranslation } from '../services/translations';

export default function FinancialSummary({ 
  initialCost, 
  userCapital, 
  businessId,
  businessName,
  userProfile,
  onPlanUpdated, 
  language = 'en' 
}) {
  const t = getTranslation(language);
  const [cost, setCost] = useState(initialCost || 140000);
  const [userContrib, setUserContrib] = useState(userCapital !== undefined ? userCapital : 15000);
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSection, setExpandedSection] = useState(null); // 'breakdown', 'scenarios', 'risks'

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
          user_contribution: Number(userContrib),
          business_id: businessId,
          business_name: businessName,
          user_profile: userProfile
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
  }, [cost, userContrib, businessId, businessName]);

  const toggleSection = (sec) => {
    setExpandedSection(expandedSection === sec ? null : sec);
  };

  const isMicroFinance = (cost <= 140000);
  const health = plan?.financial_health || 'HEALTHY';
  const coverage = plan?.repayment_capacity;
  const financials = plan?.monthly_financials;
  const breakEven = plan?.break_even;
  const costDecomp = plan?.cost_breakdown;
  const scenarios = plan?.scenarios || [];
  const risks = plan?.risks || [];

  const getHealthBadge = (h) => {
    switch (h) {
      case 'HEALTHY':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'CAUTION':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'HIGH RISK':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  const getCoverageBadgeClass = (status) => {
    if (status?.includes('Strong')) return 'bg-emerald-100 text-emerald-900 border-emerald-300';
    if (status?.includes('Reasonable')) return 'bg-teal-100 text-teal-900 border-teal-300';
    if (status?.includes('Tight')) return 'bg-amber-100 text-amber-900 border-amber-300';
    return 'bg-rose-100 text-rose-900 border-rose-300';
  };

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-dark via-gv-primary to-gv-secondary px-5 py-3.5 text-white flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-400/20 text-amber-300 flex items-center justify-center text-xs font-bold border border-amber-300/40">
            <Calculator className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold font-display flex items-center space-x-2">
                <span>{language === 'mr' ? 'आर्थिक व कर्ज योजना रचना' : language === 'hi' ? 'वित्तीय एवं ऋण योजना संरचना' : 'Financial & Funding Plan'}</span>
              </h3>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getHealthBadge(health)}`}>
                {health}
              </span>
            </div>
            <p className="text-[11px] text-emerald-100">
              {plan?.business_name ? `Financial model for ${plan.business_name}` : t.financeSub}
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
                ? (language === 'mr' ? 'राष्ट्रीय सूक्ष्म वित्त कर्ज योजना निकष लागू:' : language === 'hi' ? 'राष्ट्रीय माइक्रो फाइनेंस योजना लागू:' : 'National Micro Finance Tier Structure:')
                : (language === 'mr' ? 'व्यावसायिक मुदत कर्ज योजना लागू:' : language === 'hi' ? 'टर्म लोन योजना लागू:' : 'Commercial Term Loan Tier Structure:')}
            </strong>
            <span className="text-[11px] text-slate-700">
              {plan?.tier_description || 'Project cost eligible for up to 90% micro-enterprise debt financing.'}
            </span>
          </div>
        </div>

        {/* Low-Capital Guidance Banner */}
        {plan?.low_capital_path?.is_low_capital && (
          <div className="bg-amber-50 p-3.5 rounded-xl border border-amber-200 text-xs text-amber-950 space-y-1.5">
            <div className="flex items-center space-x-1.5 font-bold text-amber-900">
              <Coins className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>Low-Capital Startup Path Available</span>
            </div>
            <p className="text-[11px]">{plan.low_capital_path.message}</p>
            <p className="text-[11px] font-semibold text-emerald-900">
              💡 {plan.low_capital_path.starter_recommendation}
            </p>
          </div>
        )}

        {/* Core 3 Figures: Project Cost, Your Contribution, Funding Required */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
              Total Project Cost
            </span>
            <p className="text-base font-extrabold text-slate-900 mt-0.5">
              ₹{Number(plan?.project_cost || cost).toLocaleString('en-IN')}
            </p>
            <span className="text-[10px] text-slate-500">100% Required Investment</span>
          </div>

          <div className="bg-white p-3 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
              Your Own Contribution
            </span>
            <p className="text-base font-extrabold text-emerald-800 mt-0.5">
              ₹{Number(plan?.own_contribution || userContrib).toLocaleString('en-IN')}
            </p>
            <span className="text-[10px] text-emerald-600 font-semibold">
              ({plan?.own_contribution_percentage || 0}% Equity Margin)
            </span>
          </div>

          <div className="bg-white p-3 rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
              Funding Gap / Loan
            </span>
            <p className="text-base font-extrabold text-gv-primary mt-0.5">
              ₹{Number(plan?.funding_requirement !== undefined ? plan.funding_requirement : plan?.required_loan || 0).toLocaleString('en-IN')}
            </p>
            <span className="text-[10px] text-gv-secondary font-semibold">
              ({plan?.loan_percentage || 0}% Debt Financing)
            </span>
          </div>
        </div>

        {/* Monthly Estimate Panel */}
        {financials && (
          <div className="bg-gradient-to-br from-slate-50 to-teal-50/40 p-3.5 rounded-xl border border-slate-200 space-y-3">
            <div className="flex justify-between items-center text-xs">
              <h4 className="font-bold text-slate-900 flex items-center space-x-1.5">
                <TrendingUp className="w-4 h-4 text-teal-700" />
                <span>Monthly Business Performance Model</span>
              </h4>
              <span className="text-[10px] text-slate-500">Source: {financials.revenue_source}</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-center sm:text-left">
              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Monthly Revenue</span>
                <p className="text-sm font-bold text-slate-800 mt-0.5">
                  ₹{Number(financials.revenue).toLocaleString('en-IN')}
                </p>
              </div>

              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Operating Expenses</span>
                <p className="text-sm font-bold text-slate-800 mt-0.5">
                  ₹{Number(financials.operating_expense).toLocaleString('en-IN')}
                </p>
              </div>

              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Monthly Surplus (Pre-EMI)</span>
                <p className="text-sm font-bold text-teal-800 mt-0.5">
                  ₹{Number(financials.surplus).toLocaleString('en-IN')}
                </p>
              </div>

              <div className="bg-emerald-50 p-2.5 rounded-lg border border-emerald-200">
                <span className="text-[10px] text-emerald-800 font-bold block">Profit Margin</span>
                <p className="text-sm font-extrabold text-emerald-900 mt-0.5">
                  {financials.profit_margin}%
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Illustrative Financing & Loan Calculator */}
        {plan && (
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-3 text-xs">
            <div className="flex justify-between items-center">
              <h4 className="font-bold text-slate-900 flex items-center space-x-1.5">
                <Building2 className="w-4 h-4 text-slate-700" />
                <span>Illustrative Loan & Repayment Structure</span>
              </h4>
              <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-semibold">
                Reducing Balance
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Loan Amount</span>
                <strong className="text-xs text-slate-800">
                  ₹{Number(plan.required_loan).toLocaleString('en-IN')}
                </strong>
              </div>

              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Interest Rate</span>
                <strong className="text-xs text-slate-800">{plan.interest_rate}% p.a.</strong>
              </div>

              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block">Tenure</span>
                <strong className="text-xs text-slate-800">{plan.tenure_years} Yrs ({plan.tenure_months} Mos)</strong>
              </div>

              <div className="bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                <span className="text-[10px] text-amber-800 font-bold block">Monthly EMI</span>
                <strong className="text-xs text-amber-950">₹{Number(plan.monthly_emi).toLocaleString('en-IN')}/mo</strong>
              </div>
            </div>

            {/* Repayment Buffer / EMI Coverage Ratio */}
            {coverage && (
              <div className={`p-3 rounded-lg border flex items-start justify-between gap-3 ${getCoverageBadgeClass(coverage.status)}`}>
                <div>
                  <div className="flex items-center space-x-2 font-bold text-xs">
                    <span>Repayment Buffer (EMI Coverage): {coverage.emi_coverage_ratio}x</span>
                    <span className="text-[10px] px-2 py-0.2 rounded-full font-extrabold bg-white border">
                      {coverage.status}
                    </span>
                  </div>
                  <p className="text-[11px] mt-0.5 leading-tight">{coverage.interpretation}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-[10px] text-slate-500 block">Break-Even</span>
                  <strong className="text-xs">{breakEven?.label || `~ ${plan.break_even_months} Mos`}</strong>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Interactive Sliders */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs">
          <div>
            <div className="flex justify-between items-center mb-1 font-semibold text-slate-700">
              <label>Adjust Project Cost (₹)</label>
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
              <label>Your Capital Contribution (₹)</label>
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

        {/* Interactive Expandable Drawers */}
        <div className="space-y-2 pt-1">
          {/* Drawer 1: Cost Breakdown */}
          {costDecomp && (
            <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
              <button
                onClick={() => toggleSection('breakdown')}
                className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800"
              >
                <span className="flex items-center space-x-2">
                  <PieChart className="w-3.5 h-3.5 text-teal-700" />
                  <span>Cost Decomposition (Equipment vs Infrastructure vs Working Capital)</span>
                </span>
                {expandedSection === 'breakdown' ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
              </button>
              {expandedSection === 'breakdown' && (
                <div className="p-3 bg-white border-t border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="text-[10px] text-slate-500 block">Equipment</span>
                    <strong className="text-slate-800">₹{costDecomp.equipment?.toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="text-[10px] text-slate-500 block">Infrastructure</span>
                    <strong className="text-slate-800">₹{costDecomp.infrastructure?.toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg">
                    <span className="text-[10px] text-slate-500 block">Working Capital</span>
                    <strong className="text-slate-800">₹{costDecomp.working_capital?.toLocaleString('en-IN')}</strong>
                  </div>
                  <div className="p-2 bg-teal-50 rounded-lg">
                    <span className="text-[10px] text-teal-800 block">Total</span>
                    <strong className="text-teal-950">₹{costDecomp.total?.toLocaleString('en-IN')}</strong>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Drawer 2: Financing Scenarios */}
          {scenarios.length > 0 && (
            <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
              <button
                onClick={() => toggleSection('scenarios')}
                className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800"
              >
                <span className="flex items-center space-x-2">
                  <Layers className="w-3.5 h-3.5 text-blue-700" />
                  <span>Compare 3 Funding Scenarios (Minimal vs Balanced vs Growth)</span>
                </span>
                {expandedSection === 'scenarios' ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
              </button>
              {expandedSection === 'scenarios' && (
                <div className="p-3 bg-white border-t border-slate-200 space-y-2.5">
                  {scenarios.map((scen, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                      <div className="flex justify-between font-bold text-slate-900 text-xs">
                        <span>{scen.scenario_name}</span>
                        <span className="text-teal-800">EMI: ₹{scen.monthly_emi?.toLocaleString('en-IN')}/mo</span>
                      </div>
                      <div className="flex flex-wrap gap-x-3 text-[11px] text-slate-600">
                        <span>Own: <strong>₹{scen.own_contribution?.toLocaleString('en-IN')}</strong></span>
                        <span>•</span>
                        <span>Loan: <strong>₹{scen.loan_amount?.toLocaleString('en-IN')}</strong></span>
                        <span>•</span>
                        <span>Coverage: <strong>{scen.emi_coverage}x</strong></span>
                      </div>
                      <p className="text-[10px] text-slate-500">{scen.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Drawer 3: Financial Risks */}
          {risks.length > 0 && (
            <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
              <button
                onClick={() => toggleSection('risks')}
                className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left font-bold text-slate-800"
              >
                <span className="flex items-center space-x-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Financial & Operating Risks ({risks.length})</span>
                </span>
                {expandedSection === 'risks' ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
              </button>
              {expandedSection === 'risks' && (
                <div className="p-3 bg-white border-t border-slate-200 space-y-1.5">
                  {risks.map((r, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-[11px] text-slate-700">
                      <span className="text-amber-600 font-bold">⚠</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Disclaimer */}
        <div className="flex items-start space-x-2 text-[10px] text-slate-500 bg-amber-50/50 p-2.5 rounded-lg border border-amber-200/60">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Illustrative Disclaimer: </strong>{plan?.disclaimer || 'Financial calculations follow micro-enterprise credit benchmarks. Final loan sanction, interest concessions, and disbursement are subject to bank credit verification.'}
          </span>
        </div>
      </div>
    </div>
  );
}
