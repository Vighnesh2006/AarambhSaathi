import React from 'react';
import {
  Sprout,
  Users,
  Target,
  Eye,
  ShieldCheck,
  TrendingUp,
  Landmark,
  Layers,
  ArrowRight,
  Heart,
  Globe,
  Sparkles,
  HelpCircle,
  Lightbulb,
  CheckCircle2
} from 'lucide-react';
import { getTranslation } from '../services/translations';

import heroVillageImg from '../assets/rural_farmer_robot_1788638084242.jpg';
import sproutLandscapeImg from '../assets/rural_sprout_landscape_1788638113042.jpg';

export default function AboutView({ onStartJourney, language = 'en' }) {
  const t = getTranslation(language);

  const opportunityFeatures = [
    {
      icon: Lightbulb,
      title: t.aboutFeatRealOpp,
      subtitle: t.aboutFeatRealOppSub,
      color: 'text-amber-500 bg-amber-50'
    },
    {
      icon: TrendingUp,
      title: t.aboutFeatFinGuide,
      subtitle: t.aboutFeatFinGuideSub,
      color: 'text-emerald-600 bg-emerald-50'
    },
    {
      icon: Landmark,
      title: t.aboutFeatGovtSchemes,
      subtitle: t.aboutFeatGovtSchemesSub,
      color: 'text-blue-600 bg-blue-50'
    },
    {
      icon: Users,
      title: t.aboutFeatStepSupport,
      subtitle: t.aboutFeatStepSupportSub,
      color: 'text-green-600 bg-green-50'
    },
  ];

  const whyReasons = [
    {
      icon: Users,
      title: t.whyNoForms,
      desc: t.whyNoFormsSub,
      color: 'bg-emerald-50 text-emerald-700'
    },
    {
      icon: Globe,
      title: t.whyMultiLang,
      desc: t.whyMultiLangSub,
      color: 'bg-blue-50 text-blue-700'
    },
    {
      icon: ShieldCheck,
      title: t.whyTrusted,
      desc: t.whyTrustedSub,
      color: 'bg-teal-50 text-teal-700'
    },
    {
      icon: Heart,
      title: t.whyRealPeople,
      desc: t.whyRealPeopleSub,
      color: 'bg-rose-50 text-rose-600'
    },
  ];

  return (
    <div className="w-full bg-[#f5f8f3] text-[#123c3a] py-6 sm:py-10">
      <div className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-12 space-y-10">
        
        {/* ================= ABOUT HERO ================= */}
        <section className="relative rounded-3xl bg-white border border-[#dce8e0] p-6 sm:p-10 lg:p-12 shadow-card overflow-hidden">
          {/* Background glow */}
          <div className="absolute -right-20 -top-20 w-96 h-96 rounded-full bg-emerald-100/50 blur-3xl pointer-events-none" />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            
            {/* Left Column: About Info */}
            <div className="lg:col-span-5 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100/80 text-xs font-bold tracking-wider text-[#075247] uppercase border border-emerald-300/60">
                <span>{t.aboutBadge}</span>
              </div>

              <h2 className="text-3xl sm:text-4xl lg:text-[46px] font-black leading-tight text-[#072a24] font-display">
                {language === 'en' ? (
                  <>Aarambh <span className="text-[#15803d]">Saathi</span></>
                ) : (
                  <span>{t.aboutTitle} {t.aboutTitleHighlight}</span>
                )}
              </h2>

              <h3 className="text-xl sm:text-2xl font-extrabold text-[#0d3f35]">
                {t.aboutSubtitle}
              </h3>

              <p className="text-sm sm:text-base leading-relaxed text-[#2d4d46]">
                {t.aboutDesc}
              </p>

              {/* 3 Value Pills */}
              <div className="grid grid-cols-3 gap-2.5 pt-2">
                <div className="flex flex-col items-center text-center p-3 rounded-xl bg-emerald-50 border border-emerald-100">
                  <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center mb-1.5 shadow-xs">
                    <Sprout size={16} />
                  </div>
                  <h5 className="font-extrabold text-xs text-[#072a24]">{t.pillPeopleFirst}</h5>
                  <p className="text-[10px] text-[#527068] mt-0.5">{t.pillPeopleFirstSub}</p>
                </div>

                <div className="flex flex-col items-center text-center p-3 rounded-xl bg-blue-50 border border-blue-100">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center mb-1.5 shadow-xs">
                    <Sparkles size={16} />
                  </div>
                  <h5 className="font-extrabold text-xs text-[#072a24]">{t.pillAiPowered}</h5>
                  <p className="text-[10px] text-[#527068] mt-0.5">{t.pillAiPoweredSub}</p>
                </div>

                <div className="flex flex-col items-center text-center p-3 rounded-xl bg-amber-50 border border-amber-100">
                  <div className="w-8 h-8 rounded-full bg-amber-600 text-white flex items-center justify-center mb-1.5 shadow-xs">
                    <Users size={16} />
                  </div>
                  <h5 className="font-extrabold text-xs text-[#072a24]">{t.pillInclusive}</h5>
                  <p className="text-[10px] text-[#527068] mt-0.5">{t.pillInclusiveSub}</p>
                </div>
              </div>

              {/* Quote */}
              <div className="pt-2">
                <p className="text-lg font-bold italic text-emerald-800 font-display">
                  {t.smallIdeasQuote}
                </p>
              </div>
            </div>

            {/* Center Column: Farmer + Mascot Visual */}
            <div className="lg:col-span-4 relative flex items-center justify-center">
              <div className="relative rounded-2xl overflow-hidden border-2 border-emerald-200 shadow-xl bg-slate-50">
                <img
                  src={heroVillageImg}
                  alt="Farmer with Aarambh Saathi Bot"
                  className="w-full h-auto object-cover max-h-[380px]"
                />
                
                {/* Speech Bubble */}
                <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl border border-emerald-400 p-2.5 shadow-md text-center max-w-[150px]">
                  <p className="text-[11px] font-bold italic text-[#064e3b] leading-tight whitespace-pre-line">
                    {t.speechBubble}
                  </p>
                </div>

                <div className="absolute bottom-3 left-3 right-3 bg-emerald-950/80 backdrop-blur-sm px-3 py-1.5 rounded-lg text-center text-xs font-bold text-emerald-200">
                  {t.ruralTogetherBadge}
                </div>
              </div>
            </div>

            {/* Right Column: 4 Feature Highlights */}
            <div className="lg:col-span-3 space-y-3">
              {opportunityFeatures.map((feat, idx) => {
                const Icon = feat.icon;
                return (
                  <div
                    key={idx}
                    className="flex items-center gap-3.5 p-3.5 rounded-xl bg-gradient-to-r from-slate-50 to-emerald-50/50 border border-slate-200/80 hover:border-emerald-300 transition shadow-2xs"
                  >
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${feat.color}`}>
                      <Icon size={20} />
                    </div>
                    <div>
                      <h4 className="font-extrabold text-xs sm:text-sm text-[#072a24]">
                        {feat.title}
                      </h4>
                      <p className="text-[11px] text-[#527068]">
                        {feat.subtitle}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        </section>

        {/* ================= MISSION & VISION / IMPACT ================= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left: Our Mission & Vision */}
          <div className="lg:col-span-5 rounded-3xl bg-white border border-[#dce8e0] p-6 sm:p-8 shadow-card flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <Target className="w-5 h-5 text-emerald-700" />
                <h3 className="text-xl font-extrabold text-[#072a24] font-display">
                  {t.missionVisionTitle}
                </h3>
              </div>

              <div className="space-y-6">
                {/* Mission */}
                <div className="flex gap-4 items-start">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-[#075247]">
                    <Target size={22} />
                  </div>
                  <div>
                    <h4 className="font-black text-base text-[#072a24]">{t.missionTitle}</h4>
                    <p className="text-xs sm:text-sm text-[#3b5952] mt-1 leading-relaxed">
                      {t.missionDesc}
                    </p>
                  </div>
                </div>

                {/* Vision */}
                <div className="flex gap-4 items-start">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-800">
                    <Eye size={22} />
                  </div>
                  <div>
                    <h4 className="font-black text-base text-[#072a24]">{t.visionTitle}</h4>
                    <p className="text-xs sm:text-sm text-[#3b5952] mt-1 leading-relaxed">
                      {t.visionDesc}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-5 border-t border-slate-100">
              <button
                onClick={onStartJourney}
                className="w-full py-3 rounded-xl bg-[#075247] text-white font-bold text-sm hover:bg-[#063f39] shadow-md transition flex items-center justify-center gap-2"
              >
                <span>{t.talkToBotBtn}</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>

          {/* Right: Our Impact (Target) */}
          <div className="lg:col-span-7 rounded-3xl bg-white border border-[#dce8e0] p-6 sm:p-8 shadow-card flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-6">
                <TrendingUp className="w-5 h-5 text-emerald-700" />
                <h3 className="text-xl font-extrabold text-[#072a24] font-display">
                  {t.impactTitle}
                </h3>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-gradient-to-b from-[#f8fcf9] to-[#edf7ee] border border-emerald-100 text-center">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-[#075247] flex items-center justify-center mx-auto mb-2">
                    <Users size={20} />
                  </div>
                  <h4 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
                    {t.statEntrepreneursVal}
                  </h4>
                  <p className="text-xs font-bold text-[#0d3f35] mt-0.5">{t.statEntrepreneursTitle}</p>
                  <p className="text-[10px] text-[#527068]">{t.statEntrepreneursSub}</p>
                </div>

                <div className="p-4 rounded-2xl bg-gradient-to-b from-[#f8fcf9] to-[#edf7ee] border border-emerald-100 text-center">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-[#075247] flex items-center justify-center mx-auto mb-2">
                    <Layers size={20} />
                  </div>
                  <h4 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
                    {t.statBizVal}
                  </h4>
                  <p className="text-xs font-bold text-[#0d3f35] mt-0.5">{t.statBizTitle}</p>
                  <p className="text-[10px] text-[#527068]">{t.statBizSub}</p>
                </div>

                <div className="p-4 rounded-2xl bg-gradient-to-b from-[#f8fcf9] to-[#edf7ee] border border-emerald-100 text-center">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-[#075247] flex items-center justify-center mx-auto mb-2">
                    <Globe size={20} />
                  </div>
                  <h4 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
                    {t.statCoverageVal}
                  </h4>
                  <p className="text-xs font-bold text-[#0d3f35] mt-0.5">{t.statCoverageTitle}</p>
                  <p className="text-[10px] text-[#527068]">{t.statCoverageSub}</p>
                </div>

                <div className="p-4 rounded-2xl bg-gradient-to-b from-[#f8fcf9] to-[#edf7ee] border border-emerald-100 text-center">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 text-[#075247] flex items-center justify-center mx-auto mb-2">
                    <Sprout size={20} />
                  </div>
                  <h4 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
                    {t.statSustVal}
                  </h4>
                  <p className="text-xs font-bold text-[#0d3f35] mt-0.5">{t.statSustTitle}</p>
                  <p className="text-[10px] text-[#527068]">{t.statSustSub}</p>
                </div>
              </div>
            </div>

            {/* Bottom Sprout Quote Banner */}
            <div className="mt-6 rounded-2xl bg-gradient-to-r from-emerald-100 via-amber-50 to-teal-100 p-4 sm:p-5 flex items-center gap-4 border border-emerald-200">
              <div className="w-12 h-12 rounded-xl bg-emerald-700 text-white flex items-center justify-center shrink-0 shadow-md">
                <Sprout size={26} />
              </div>
              <div>
                <p className="text-base sm:text-lg font-bold italic text-[#064e3b]">
                  {t.quoteMain}
                </p>
                <p className="text-xs font-semibold text-emerald-800">
                  {t.quoteAuthor}
                </p>
              </div>
            </div>
          </div>

        </div>

        {/* ================= WHY AARAMBH SAATHI ================= */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            <h3 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
              {t.whyTitle}
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {whyReasons.map((reason, idx) => {
              const Icon = reason.icon;
              return (
                <div
                  key={idx}
                  className="p-5 rounded-2xl bg-white border border-[#dce8e0] shadow-xs hover:shadow-md hover:border-emerald-300 transition"
                >
                  <div className={`w-11 h-11 rounded-xl ${reason.color} flex items-center justify-center mb-3`}>
                    <Icon size={22} />
                  </div>
                  <h4 className="font-extrabold text-sm sm:text-base text-[#072a24]">
                    {reason.title}
                  </h4>
                  <p className="text-xs text-[#527068] mt-1 leading-relaxed">
                    {reason.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

      </div>
    </div>
  );
}
