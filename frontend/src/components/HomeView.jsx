import React from 'react';
import {
  ArrowRight,
  Sprout,
  Play,
  Wallet,
  Users,
  Store,
  Package,
  MapPin,
  Tractor,
  Palette,
  Zap,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { getTranslation } from '../services/translations';

import heroVillageImg from '../assets/rural_farmer_robot_1788638084242.jpg';
import sproutLandscapeImg from '../assets/rural_sprout_landscape_1788638113042.jpg';
import agriImg from '../assets/category_agriculture_1788638127709.jpg';
import dairyImg from '../assets/category_dairy_1788638146882.jpg';
import foodProcImg from '../assets/category_food_processing_1788638164240.jpg';

export default function HomeView({
  onStartJourney,
  onOpenCatalogue,
  onSelectCategory,
  language
}) {
  const t = getTranslation(language);

  const opportunities = [
    {
      id: 'agri',
      title: t.catAgri,
      category: 'Agriculture & Allied',
      image: agriImg || 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80',
      icon: Sprout,
      color: 'bg-emerald-50 text-emerald-700'
    },
    {
      id: 'dairy',
      title: t.catDairy,
      category: 'Livestock',
      image: dairyImg || 'https://images.unsplash.com/photo-1527153857715-3908f2bae5e8?auto=format&fit=crop&w=800&q=80',
      icon: Tractor,
      color: 'bg-blue-50 text-blue-700'
    },
    {
      id: 'food',
      title: t.catFood,
      category: 'Food Processing',
      image: foodProcImg || 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80',
      icon: Package,
      color: 'bg-amber-50 text-amber-700'
    },
    {
      id: 'crafts',
      title: t.catCrafts,
      category: 'Handicrafts & Artisans',
      image: 'https://images.unsplash.com/photo-1594736797933-d0c5a3f0b9f2?auto=format&fit=crop&w=800&q=80',
      icon: Palette,
      color: 'bg-orange-50 text-orange-700'
    },
    {
      id: 'energy',
      title: t.catEnergy,
      category: 'Renewable Energy',
      image: 'https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80',
      icon: Zap,
      color: 'bg-teal-50 text-teal-700'
    },
    {
      id: 'tourism',
      title: t.catTourism,
      category: 'Rural Tourism & Services',
      image: 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=800&q=80',
      icon: MapPin,
      color: 'bg-green-50 text-green-700'
    },
  ];

  const features = [
    {
      icon: Sprout,
      title: t.featLocalOpp,
      subtitle: t.featLocalOppSub,
      bgColor: 'bg-[#e5f6d7]',
      iconColor: 'text-[#168650]'
    },
    {
      icon: Wallet,
      title: t.featAiGuide,
      subtitle: t.featAiGuideSub,
      bgColor: 'bg-[#e0f2fe]',
      iconColor: 'text-[#0284c7]'
    },
    {
      icon: Users,
      title: t.featGovtSupport,
      subtitle: t.featGovtSupportSub,
      bgColor: 'bg-[#fef3c7]',
      iconColor: 'text-[#d97706]'
    },
    {
      icon: Store,
      title: t.featBizPlan,
      subtitle: t.featBizPlanSub,
      bgColor: 'bg-[#ffe4e6]',
      iconColor: 'text-[#e11d48]'
    },
  ];

  const stats = [
    {
      icon: Users,
      value: t.statEntrepreneursVal,
      title: t.statEntrepreneursTitle,
      subtitle: t.statEntrepreneursSub,
    },
    {
      icon: Package,
      value: t.statBizVal,
      title: t.statBizTitle,
      subtitle: t.statBizSub,
    },
    {
      icon: MapPin,
      value: t.statCoverageVal,
      title: t.statCoverageTitle,
      subtitle: t.statCoverageSub,
    },
    {
      icon: Sprout,
      value: t.statSustVal,
      title: t.statSustTitle,
      subtitle: t.statSustSub,
    },
  ];

  return (
    <div className="w-full">
      {/* ================= HERO SECTION ================= */}
      <section className="relative min-h-[500px] lg:min-h-[540px] overflow-hidden bg-gradient-to-b from-[#e8f5e9]/60 via-[#f4f9f4]/40 to-[#f5f8f3]">
        {/* Background Image Overlay */}
        <div className="absolute inset-0 pointer-events-none opacity-40 mix-blend-multiply">
          <img
            src={sproutLandscapeImg}
            className="w-full h-full object-cover object-center"
            alt="Rural landscape background"
          />
        </div>

        <div className="relative mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-12 py-10 lg:py-14 flex flex-col lg:flex-row items-center justify-between gap-10">
          {/* Left Hero Text */}
          <div className="z-10 max-w-[680px]">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-100/90 border border-emerald-300/60 mb-4 text-xs font-bold tracking-[3px] text-[#075247] uppercase">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>{t.heroSubtitle}</span>
            </div>

            <h2 className="text-4xl sm:text-5xl lg:text-[68px] font-black leading-[1.02] tracking-tight text-[#072a24] font-display">
              {language === 'en' ? (
                <>Aarambh <span className="text-[#15803d]">Saathi</span></>
              ) : (
                <span>{t.heroTitle} {t.heroTitleHighlight}</span>
              )}
            </h2>

            <h3 className="mt-3 text-2xl sm:text-3xl lg:text-[32px] font-extrabold text-[#0d3f35]">
              {t.heroTagline}
            </h3>

            <p className="mt-4 text-base sm:text-lg lg:text-[19px] leading-relaxed text-[#2d4d46] max-w-[620px]">
              {t.heroDesc}
            </p>

            {/* CTA Buttons */}
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <button
                onClick={onStartJourney}
                className="flex items-center gap-3 rounded-2xl bg-gradient-to-r from-[#075247] to-[#15803d] px-7 py-4 text-base sm:text-lg font-bold text-white shadow-xl hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98] transition-all"
              >
                <Sprout className="w-6 h-6 text-[#a7f3d0]" />
                <span>{t.findOpportunityBtn}</span>
                <ArrowRight className="w-5 h-5 ml-1" />
              </button>

              <button
                onClick={onOpenCatalogue}
                className="flex items-center gap-3 rounded-2xl border-2 border-[#15803d]/30 bg-white/90 backdrop-blur-sm px-6 py-4 text-base sm:text-lg font-bold text-[#075247] hover:bg-emerald-50/80 shadow-md transition-all"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#15803d] text-white">
                  <Play size={13} fill="white" className="ml-0.5" />
                </span>
                <span>{t.exploreCatalogueBtn}</span>
              </button>
            </div>
          </div>

          {/* Right Hero Visual (Farmer + AI Robot + Speech Bubble) */}
          <div className="relative w-full max-w-[540px] lg:max-w-[580px] flex items-center justify-center">
            {/* Main Visual Image */}
            <div className="relative rounded-3xl overflow-hidden shadow-2xl border-4 border-white/80 bg-white group">
              <img
                src={heroVillageImg}
                alt="Aarambh Saathi Farmer and AI Robot Assistant"
                className="w-full h-auto object-cover max-h-[360px] group-hover:scale-105 transition-transform duration-700"
              />

              {/* Gradient Bottom Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-[#063f39]/80 via-transparent to-transparent opacity-60" />

              {/* Badge on Image */}
              <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white">
                <div className="flex items-center gap-2 bg-emerald-950/80 backdrop-blur-md px-3.5 py-1.5 rounded-xl border border-emerald-400/30 text-xs font-bold">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  <span>{t.aiEngineBadge}</span>
                </div>
                <div className="text-right text-[11px] font-semibold text-emerald-200">
                  {t.ruralTogetherBadge}
                </div>
              </div>
            </div>

            {/* Authentic Speech Bubble Overlay */}
            <div className="absolute -top-5 sm:-top-8 right-2 sm:right-6 bg-white/95 backdrop-blur-md rounded-2xl border-2 border-[#15803d] p-3 sm:p-4 shadow-xl text-center max-w-[200px] sm:max-w-[220px] animate-soft-pulse">
              <p className="text-xs sm:text-sm font-bold italic text-[#064e3b] leading-tight font-display whitespace-pre-line">
                {t.speechBubble}
              </p>
              <div className="flex items-center justify-center gap-1 mt-1 text-[11px] font-bold text-[#15803d]">
                <Sprout className="w-3.5 h-3.5 text-[#15803d]" />
                <span>{t.appName}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================= 4 PILL FEATURES ================= */}
      <section className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-12 py-7">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="flex items-center gap-4 p-4 rounded-2xl bg-white border border-[#e2ece5] shadow-xs hover:shadow-md hover:border-emerald-300 transition-all"
              >
                <div className={`flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl ${feature.bgColor}`}>
                  <Icon className={`${feature.iconColor} w-6 h-6`} />
                </div>
                <div>
                  <h4 className="font-extrabold text-sm sm:text-base text-[#0d3f35]">
                    {feature.title}
                  </h4>
                  <p className="text-xs text-[#527068] mt-0.5">
                    {feature.subtitle}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ================= STATS & QUOTE STRIP ================= */}
      <section className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-12 py-4">
        <div className="rounded-3xl border border-[#d6e5da] bg-white p-6 sm:p-8 shadow-card">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={index}
                  className="rounded-2xl border border-[#dcebe1] bg-gradient-to-b from-[#f8fcf9] to-[#edf7ee] p-5 text-center flex flex-col items-center justify-center shadow-2xs hover:border-emerald-400 transition"
                >
                  <div className="w-12 h-12 rounded-xl bg-emerald-100 text-[#075247] flex items-center justify-center mb-3">
                    <Icon size={26} />
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-black text-[#072a24] font-display">
                    {stat.value}
                  </h3>
                  <p className="font-extrabold text-sm sm:text-base text-[#0d3f35] mt-1">
                    {stat.title}
                  </p>
                  <p className="text-xs text-[#527068] mt-0.5">
                    {stat.subtitle}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Inspirational Quote Banner */}
          <div className="mt-6 rounded-2xl bg-gradient-to-r from-[#dcfce7] via-[#ecfccb] to-[#d1fae5] p-5 sm:p-6 text-center border border-emerald-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4 text-left">
              <div className="hidden sm:flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-md">
                <Sprout size={32} />
              </div>
              <div>
                <p className="text-lg sm:text-2xl font-bold italic text-[#064e3b]">
                  {t.quoteMain}
                </p>
                <p className="text-xs sm:text-sm font-semibold text-emerald-800 mt-0.5">
                  {t.quoteAuthor}
                </p>
              </div>
            </div>

            <button
              onClick={onStartJourney}
              className="whitespace-nowrap px-6 py-3 rounded-xl bg-[#075247] text-white font-bold text-sm hover:bg-[#063f39] shadow-md transition"
            >
              {t.startPlanCta}
            </button>
          </div>
        </div>
      </section>

      {/* ================= EXPLORE OPPORTUNITIES (6 CATEGORIES) ================= */}
      <section id="catalogue" className="mx-auto max-w-[1500px] px-6 sm:px-10 lg:px-12 py-10">
        <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-2xl sm:text-3xl lg:text-[34px] font-black text-[#072a24] font-display">
                {t.exploreTitle}
              </h2>
              <span className="bg-emerald-100 text-[#075247] font-bold text-xs px-2.5 py-1 rounded-full border border-emerald-300">
                {t.exploreBadge}
              </span>
            </div>
            <p className="text-sm sm:text-base text-[#527068] mt-1.5">
              {t.exploreSubtitle}
            </p>
          </div>

          <button
            onClick={onOpenCatalogue}
            className="inline-flex items-center gap-2 rounded-xl border border-emerald-600/30 bg-white px-5 py-2.5 font-bold text-sm text-[#075247] hover:bg-emerald-50 shadow-xs transition"
          >
            <span>{t.viewFullCatalogue}</span>
            <ArrowRight size={16} />
          </button>
        </div>

        {/* 6 Category Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {opportunities.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.id}
                onClick={() => onSelectCategory(item.category)}
                className="group cursor-pointer overflow-hidden rounded-2xl bg-white border border-[#dce8e0] shadow-xs transition-all duration-300 hover:-translate-y-1.5 hover:shadow-xl hover:border-emerald-400 flex flex-col"
              >
                {/* Category Cover Image */}
                <div className="h-36 overflow-hidden relative bg-slate-100">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="h-full w-full object-cover transition duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
                </div>

                {/* Category Card Bottom Content */}
                <div className="p-3.5 flex items-center justify-between gap-2.5 flex-1 bg-white">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-[#075247] border border-emerald-100">
                      <Icon size={20} />
                    </div>
                    <p className="whitespace-pre-line text-xs sm:text-sm font-bold leading-tight text-[#072a24] truncate group-hover:text-emerald-700 transition">
                      {item.title}
                    </p>
                  </div>

                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-600 group-hover:bg-[#075247] group-hover:text-white transition">
                    <ArrowRight size={13} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
