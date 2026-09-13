import React, { useState } from 'react';
import { 
  MapPin, CheckCircle2, AlertTriangle, Info, Compass, Users, 
  PackageCheck, AlertCircle, ChevronDown, ChevronUp, Store, 
  ShoppingCart, Truck, Wrench, ShieldCheck, Sparkles, Building2, Factory
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function FeasibilityCard({ feasibility, selectedBusinessName, language = 'en' }) {
  const t = getTranslation(language);
  const [expandedSection, setExpandedSection] = useState(null); // 'breakdown', 'competitors', 'markets', 'suppliers'

  if (!feasibility) {
    return null;
  }

  const score = Math.round(feasibility.overall_score || feasibility.feasibility_score || 0);
  const level = feasibility.feasibility_level || 'Feasible';
  const factors = feasibility.factors;
  const infraGaps = feasibility.infrastructure_gaps || [];
  const competitors = feasibility.nearby_competitors || [];
  const markets = feasibility.nearby_markets || [];
  const suppliers = feasibility.suppliers || [];
  const dataQuality = feasibility.data_quality;

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const getLevelBadgeClass = (lvl) => {
    switch (lvl) {
      case 'Highly Feasible':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'Feasible':
        return 'bg-teal-100 text-teal-800 border-teal-300';
      case 'Moderately Feasible':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'Needs Validation':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      default:
        return 'bg-rose-100 text-rose-800 border-rose-300';
    }
  };

  const factorList = factors ? [
    { key: 'location', label: 'Location Suitability', weight: '20%', icon: MapPin, data: factors.location },
    { key: 'infrastructure', label: 'Infrastructure Fit', weight: '20%', icon: Building2, data: factors.infrastructure },
    { key: 'market_access', label: 'Market Access', weight: '15%', icon: Store, data: factors.market_access },
    { key: 'local_demand', label: 'Local Demand', weight: '15%', icon: ShoppingCart, data: factors.local_demand },
    { key: 'competition', label: 'Competition Landscape', weight: '10%', icon: Users, data: factors.competition },
    { key: 'supplier_availability', label: 'Supplier Availability', weight: '10%', icon: Wrench, data: factors.supplier_availability },
    { key: 'raw_material_access', label: 'Raw Material Access', weight: '5%', icon: PackageCheck, data: factors.raw_material_access },
    { key: 'transport', label: 'Transport & Connectivity', weight: '5%', icon: Truck, data: factors.transport },
  ] : [];

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-surface via-emerald-50 to-teal-50 px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-teal-800 text-white flex items-center justify-center text-xs font-bold shadow-xs">
            <Compass className="w-5 h-5 text-teal-200" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-900 font-display">
                {t.feasibilityTitle || 'Hyper-Local Feasibility'}
              </h3>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${getLevelBadgeClass(level)}`}>
                {level}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              {language === 'mr' ? 'विश्लेषण व्यवसाय: ' : language === 'hi' ? 'विश्लेषण व्यवसाय: ' : 'Evaluating: '}
              <strong className="text-slate-700">{selectedBusinessName || feasibility.business_name}</strong>
            </p>
          </div>
        </div>

        {/* Score Gauge */}
        <div className="text-right">
          <div className="inline-flex items-baseline space-x-0.5 bg-gradient-to-br from-teal-800 to-gv-primary text-white px-3 py-1 rounded-xl shadow-xs">
            <span className="text-lg font-extrabold text-amber-300">{score}</span>
            <span className="text-xs text-slate-200 font-normal">/100</span>
          </div>
          <span className="block text-[9px] text-teal-900 font-bold uppercase tracking-wider mt-0.5">
            {t.feasibilityScoreLabel || 'Feasibility Score'}
          </span>
        </div>
      </div>

      <div className="p-4 sm:p-5 space-y-4">
        {/* Infrastructure Gap Alert (if any) */}
        {infraGaps.length > 0 && (
          <div className="bg-amber-50 rounded-xl p-3 border border-amber-200 text-xs">
            <div className="flex items-center space-x-1.5 font-bold text-amber-900 mb-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>Infrastructure Prerequisites to Address</span>
            </div>
            <ul className="space-y-1 pl-5 list-disc text-amber-950 text-[11px]">
              {infraGaps.map((gap, idx) => (
                <li key={idx}>{gap}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 4 Core Summary Pillars */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium flex items-center">
              <Compass className="w-3 h-3 mr-1 text-emerald-600" /> {t.marketDemand || 'Market Demand'}
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.market_opportunity}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium flex items-center">
              <Users className="w-3 h-3 mr-1 text-blue-600" /> {t.localComp || 'Competition'}
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.competition_level}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium flex items-center">
              <PackageCheck className="w-3 h-3 mr-1 text-teal-600" /> {t.rawMat || 'Resources & Setup'}
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.resource_availability}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> {t.riskFactor || 'Risk Profile'}
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.risk_level}</p>
          </div>
        </div>

        {/* Interactive Expandable Drawers */}
        <div className="space-y-2 pt-1">
          {/* Drawer 1: 8-Factor Feasibility Breakdown */}
          {factorList.length > 0 && (
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <button
                onClick={() => toggleSection('breakdown')}
                className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left transition-colors text-xs font-bold text-slate-800"
              >
                <span className="flex items-center space-x-2">
                  <Sparkles className="w-3.5 h-3.5 text-teal-600" />
                  <span>Why this score? (8-Factor Transparent Breakdown)</span>
                </span>
                {expandedSection === 'breakdown' ? (
                  <ChevronUp className="w-4 h-4 text-slate-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                )}
              </button>
              {expandedSection === 'breakdown' && (
                <div className="p-3.5 bg-white border-t border-slate-200 space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {factorList.map((f) => {
                      const Icon = f.icon;
                      const fScore = Math.round(f.data?.score || 0);
                      return (
                        <div key={f.key} className="bg-slate-50 p-2.5 rounded-lg border border-slate-200/70 text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold text-slate-800 flex items-center space-x-1.5 text-[11px]">
                              <Icon className="w-3.5 h-3.5 text-teal-700" />
                              <span>{f.label}</span>
                              <span className="text-[9px] text-slate-500 font-normal">({f.weight})</span>
                            </span>
                            <span className="font-bold text-teal-800 bg-teal-50 px-1.5 py-0.5 rounded text-[11px]">
                              {fScore}/100
                            </span>
                          </div>
                          {/* Score Bar */}
                          <div className="w-full bg-slate-200 rounded-full h-1.5 mb-1.5">
                            <div
                              className={`h-1.5 rounded-full ${
                                fScore >= 85 ? 'bg-emerald-600' : fScore >= 70 ? 'bg-teal-600' : 'bg-amber-500'
                              }`}
                              style={{ width: `${fScore}%` }}
                            />
                          </div>
                          <p className="text-[10px] text-slate-600 leading-tight">{f.data?.reason}</p>
                          <div className="mt-1 flex items-center justify-between text-[9px] text-slate-400">
                            <span>Source: {f.data?.source}</span>
                            <span>Conf: {Math.round(f.data?.confidence || 85)}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Drawer 2: Nearby Competitors */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <button
              onClick={() => toggleSection('competitors')}
              className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left transition-colors text-xs font-bold text-slate-800"
            >
              <span className="flex items-center space-x-2">
                <Users className="w-3.5 h-3.5 text-blue-600" />
                <span>Nearby Local Competitors & Peers ({competitors.length})</span>
              </span>
              {expandedSection === 'competitors' ? (
                <ChevronUp className="w-4 h-4 text-slate-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-500" />
              )}
            </button>
            {expandedSection === 'competitors' && (
              <div className="p-3 bg-white border-t border-slate-200 space-y-2">
                {competitors.length === 0 ? (
                  <p className="text-xs text-slate-500 italic p-2">No direct competitors found nearby. High pioneer advantage.</p>
                ) : (
                  competitors.map((comp, idx) => (
                    <div key={idx} className="flex items-start justify-between p-2 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                      <div>
                        <div className="flex items-center space-x-1.5 font-bold text-slate-800">
                          <span>{comp.business_name}</span>
                          {comp.is_live_api && (
                            <span className="text-[9px] bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded font-medium">Live Google Places</span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500">{comp.relevance || comp.category}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <span className="inline-block bg-white px-2 py-0.5 rounded border border-slate-200 font-bold text-slate-700 text-[11px]">
                          ~{comp.distance_km} km
                        </span>
                        {comp.rating && (
                          <span className="block text-[10px] text-amber-600 font-semibold">★ {comp.rating}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Drawer 3: Nearby Markets & APMC Mandis */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <button
              onClick={() => toggleSection('markets')}
              className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left transition-colors text-xs font-bold text-slate-800"
            >
              <span className="flex items-center space-x-2">
                <Store className="w-3.5 h-3.5 text-emerald-600" />
                <span>Nearby Markets, APMC Mandis & Haats ({markets.length})</span>
              </span>
              {expandedSection === 'markets' ? (
                <ChevronUp className="w-4 h-4 text-slate-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-500" />
              )}
            </button>
            {expandedSection === 'markets' && (
              <div className="p-3 bg-white border-t border-slate-200 space-y-2">
                {markets.map((m, idx) => (
                  <div key={idx} className="flex items-start justify-between p-2 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                    <div>
                      <div className="flex items-center space-x-1.5 font-bold text-slate-800">
                        <span>{m.market_name}</span>
                        {m.is_live_api && (
                          <span className="text-[9px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded font-medium">Live Geolocation</span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500">{m.relevance}</p>
                      <span className="text-[10px] text-teal-700 font-medium">{m.operating_days || 'Regular trading days'}</span>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className="inline-block bg-white px-2 py-0.5 rounded border border-slate-200 font-bold text-slate-700 text-[11px]">
                        ~{m.distance_km} km
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Drawer 4: Verified Equipment Suppliers */}
          {suppliers.length > 0 && (
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <button
                onClick={() => toggleSection('suppliers')}
                className="w-full px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 flex items-center justify-between text-left transition-colors text-xs font-bold text-slate-800"
              >
                <span className="flex items-center space-x-2">
                  <Factory className="w-3.5 h-3.5 text-purple-600" />
                  <span>Verified Machinery & Equipment Suppliers ({suppliers.length})</span>
                </span>
                {expandedSection === 'suppliers' ? (
                  <ChevronUp className="w-4 h-4 text-slate-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                )}
              </button>
              {expandedSection === 'suppliers' && (
                <div className="p-3 bg-white border-t border-slate-200 space-y-2">
                  {suppliers.map((sup, idx) => (
                    <div key={idx} className="flex items-start justify-between p-2.5 rounded-lg bg-purple-50/50 border border-purple-200/70 text-xs">
                      <div>
                        <div className="flex items-center space-x-1.5 font-bold text-slate-800">
                          <span>{sup.supplier_name}</span>
                          {sup.verified && (
                            <span className="text-[9px] bg-purple-100 text-purple-800 px-1.5 py-0.2 rounded font-semibold flex items-center">
                              <ShieldCheck className="w-2.5 h-2.5 mr-0.5 text-purple-700" /> Verified
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-600 font-medium mt-0.5">{sup.machine_name}</p>
                        <p className="text-[10px] text-slate-500">📍 {sup.location}, {sup.state}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <span className="inline-block bg-white px-2 py-0.5 rounded border border-purple-200 font-bold text-purple-900 text-[11px]">
                          {sup.price_range}
                        </span>
                        <span className="block text-[9px] text-slate-400 mt-0.5">Indicative</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Positive & Caution Indicators */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {/* Positives */}
          <div className="bg-emerald-50/50 rounded-xl p-3 border border-emerald-200/70 space-y-1.5">
            <span className="font-bold text-emerald-900 text-xs flex items-center space-x-1 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>{language === 'mr' ? 'मुख्य सुसंगतता बलस्थाने' : language === 'hi' ? 'मुख्य व्यवहार्यता की ताकत' : 'Key Feasibility Strengths'}</span>
            </span>
            {feasibility.positive_factors?.map((pos, i) => (
              <div key={i} className="flex items-start space-x-1.5 text-[11px] text-emerald-950">
                <span className="text-emerald-600 font-bold">✓</span>
                <span>{pos}</span>
              </div>
            ))}
          </div>

          {/* Cautions */}
          <div className="bg-amber-50/50 rounded-xl p-3 border border-amber-200/70 space-y-1.5">
            <span className="font-bold text-amber-900 text-xs flex items-center space-x-1 mb-1">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
              <span>{language === 'mr' ? 'स्थानिक जोखीम व काळजी' : language === 'hi' ? 'स्थानीय जोखिम और सावधानियां' : 'Local Risks & Cautions'}</span>
            </span>
            {feasibility.caution_factors?.map((caut, i) => (
              <div key={i} className="flex items-start space-x-1.5 text-[11px] text-amber-950">
                <span className="text-amber-600 font-bold">⚠</span>
                <span>{caut}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Next Steps */}
        {feasibility.recommendations && feasibility.recommendations.length > 0 && (
          <div className="bg-teal-50/60 rounded-xl p-3 border border-teal-200/70 text-xs space-y-1.5">
            <span className="font-bold text-teal-950 text-xs flex items-center space-x-1.5 mb-1">
              <Sparkles className="w-3.5 h-3.5 text-teal-700" />
              <span>Actionable Next Steps for this Location</span>
            </span>
            <ul className="space-y-1 pl-4 list-disc text-teal-950 text-[11px]">
              {feasibility.recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Data Quality & Transparency Notice */}
        <div className="flex items-start space-x-2 bg-slate-100/80 p-2.5 rounded-lg border border-slate-200 text-[10px] text-slate-500">
          <Info className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Transparency & Data Quality: </strong>
            {dataQuality?.verified_factors?.length > 0 ? (
              <span>Verified via {dataQuality.verified_factors.join(', ')}. </span>
            ) : null}
            <span>Local feasibility utilizes verified supplier databases and geographic indicators without fabricating synthetic headcount metrics.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
