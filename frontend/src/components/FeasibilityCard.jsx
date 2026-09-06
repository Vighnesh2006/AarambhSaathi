import React from 'react';
import { MapPin, CheckCircle2, AlertTriangle, Info, Compass, Users, PackageCheck, AlertCircle } from 'lucide-react';

export default function FeasibilityCard({ feasibility, selectedBusinessName }) {
  if (!feasibility) {
    return null;
  }

  const score = Math.round(feasibility.feasibility_score);

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-surface via-emerald-50 to-teal-50 px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-800 text-white flex items-center justify-center text-xs font-bold shadow-2xs">
            <Compass className="w-4 h-4 text-teal-200" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 font-display flex items-center space-x-1.5">
              <span>Hyper-Local Feasibility Analysis</span>
              <span className="text-[10px] bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full font-semibold">
                Local Baseline
              </span>
            </h3>
            <p className="text-[11px] text-slate-500">
              Evaluating: <strong className="text-slate-700">{selectedBusinessName || feasibility.business_name}</strong>
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
            Feasibility Score
          </span>
        </div>
      </div>

      {/* 4 Core Pillars Grid */}
      <div className="p-4 sm:p-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4">
          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium block flex items-center">
              <Compass className="w-3 h-3 mr-1 text-emerald-600" /> Market Demand
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.market_opportunity}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium block flex items-center">
              <Users className="w-3 h-3 mr-1 text-blue-600" /> Local Competition
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.competition_level}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium block flex items-center">
              <PackageCheck className="w-3 h-3 mr-1 text-teal-600" /> Raw Resources
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.resource_availability}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
            <span className="text-[10px] text-slate-500 font-medium block flex items-center">
              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" /> Risk Exposure
            </span>
            <p className="text-xs font-bold text-slate-800 mt-1">{feasibility.risk_level}</p>
          </div>
        </div>

        {/* Positive & Caution Indicators */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          {/* Positives */}
          <div className="bg-emerald-50/50 rounded-xl p-3 border border-emerald-200/70 space-y-1.5">
            <span className="font-bold text-emerald-900 text-xs flex items-center space-x-1 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Key Feasibility Strengths</span>
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
              <span>Local Risks & Cautions</span>
            </span>
            {feasibility.caution_factors?.map((caut, i) => (
              <div key={i} className="flex items-start space-x-1.5 text-[11px] text-amber-950">
                <span className="text-amber-600 font-bold">⚠</span>
                <span>{caut}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Transparent Demo Data Disclaimer */}
        <div className="mt-3.5 flex items-start space-x-2 bg-slate-100/80 p-2 rounded-lg border border-slate-200 text-[10px] text-slate-500">
          <Info className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Transparency Notice:</strong> Local feasibility utilizes baseline rural demographic and trade benchmarks for demonstration. Architecture supports connecting live district APMC & GIS APIs for sanctioning.
          </span>
        </div>
      </div>
    </div>
  );
}
