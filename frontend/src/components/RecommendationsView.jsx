import React, { useState, useRef } from 'react';
import {
  ArrowLeft,
  Edit3,
  Heart,
  Share2,
  ChevronRight,
  ChevronLeft,
  Sparkles,
  DollarSign,
  Clock,
  TrendingUp,
  CheckCircle2,
  Users,
  Award,
  Mic,
  FileText,
  ShieldCheck,
  Wrench,
  Landmark,
  Building2,
  ArrowRight,
  RotateCcw,
  BarChart3,
  Bookmark
} from 'lucide-react';
import { getBusinessAsset } from '../services/businessAssets';
import FeasibilityCard from './FeasibilityCard';
import BusinessSetupCard from './BusinessSetupCard';
import FinancialSummary from './FinancialSummary';
import SchemesCard from './SchemesCard';

export default function RecommendationsView({
  recommendations = [],
  selectedBusinessId,
  onSelectBusiness,
  profile = {},
  feasibility,
  schemes = [],
  financialPlan,
  onUpdateFinancialPlan,
  onOpenReport,
  onUpdateProfile,
  onBackToChat,
  language = 'en'
}) {
  const [activeFilter, setActiveFilter] = useState('All');
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'detail'
  const [activeDetailTab, setActiveDetailTab] = useState('overview');
  const [isSaved, setIsSaved] = useState(false);
  const scrollContainerRef = useRef(null);

  // Fallback / standard list
  const defaultBusinesses = [
    { business_id: 'milk_testing', business_name: 'Milk Quality Testing Service', match_score: 95, match_level: 'Top Match' },
    { business_id: 'dairy_farming', business_name: 'Dairy Farming', match_score: 91, match_level: 'Strong Match' },
    { business_id: 'mushroom_cultivation', business_name: 'Mushroom Cultivation', match_score: 87, match_level: 'Strong Match' },
    { business_id: 'solar_installation', business_name: 'Solar Installation Service', match_score: 85, match_level: 'Good Match' },
    { business_id: 'spice_processing', business_name: 'Spice Processing Unit', match_score: 82, match_level: 'Good Match' },
    { business_id: 'tailoring_unit', business_name: 'Tailoring & Garment Unit', match_score: 80, match_level: 'Good Match' },
    { business_id: 'retail_general_store', business_name: 'Retail & General Store', match_score: 78, match_level: 'Good Match' },
    { business_id: 'vermicompost_production', business_name: 'Vermicompost Production', match_score: 76, match_level: 'Good Match' }
  ];

  const currentList = (recommendations && recommendations.length > 0)
    ? recommendations
    : defaultBusinesses;

  // Selected business
  const currentBusiness = currentList.find(
    (b) => b.business_id === selectedBusinessId || b.id === selectedBusinessId
  ) || currentList[0];

  const currentAsset = getBusinessAsset(currentBusiness?.business_name);

  // Filter list
  const filteredList = currentList.filter((b) => {
    if (activeFilter === 'All') return true;
    const asset = getBusinessAsset(b.business_name);
    if (activeFilter === 'Low Investment') return asset.maxInvestment <= 150000 || asset.badge === 'Low Investment';
    if (activeFilter === 'High Returns') return asset.badge === 'High Returns' || asset.profitPotential.includes('High');
    if (activeFilter === 'Quick Setup') return asset.setupTime.includes('1') || asset.badge === 'Quick Setup';
    if (activeFilter === 'Service Based') return asset.filterCategory === 'Service Based' || b.business_name.includes('Service') || b.business_name.includes('Store');
    return true;
  });

  const handleOpenDetail = (bizId) => {
    onSelectBusiness(bizId);
    setViewMode('detail');
    setActiveDetailTab('overview');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToList = () => {
    setViewMode('list');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Horizontal Scroll Handler
  const scrollHorizontally = (direction) => {
    if (scrollContainerRef.current) {
      const scrollAmount = direction === 'left' ? -380 : 380;
      scrollContainerRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const userLocationText = profile.district || profile.location || 'Maharashtra';
  const userCapitalNum = Number(profile.capital || profile.available_investment || 100000);
  const userCapitalFormatted = `₹${(userCapitalNum * 0.5).toLocaleString('en-IN')} – ₹${(userCapitalNum * 2).toLocaleString('en-IN')}`;

  return (
    <div className="max-w-[1700px] mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
      
      {/* ========================================================================= */}
      {/* VIEW 1: RECOMMENDATIONS LIST VIEW (ONE HORIZONTAL LINE CAROUSEL)         */}
      {/* ========================================================================= */}
      {viewMode === 'list' && (
        <div className="space-y-6 animate-fadeIn">
          
          {/* Top Navigation Row: Back and Update Profile */}
          <div className="flex items-center justify-between">
            <button
              onClick={onBackToChat}
              className="flex items-center gap-1.5 text-xs font-bold text-[#426159] hover:text-[#072a24] transition cursor-pointer"
            >
              <ArrowLeft size={16} />
              <span>{language === 'mr' ? 'मागे जा' : language === 'hi' ? 'पीछे' : 'Back'}</span>
            </button>

            <button
              onClick={onUpdateProfile}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-[#cbe0d2] text-[#075247] hover:bg-[#f2faf4] text-xs font-extrabold shadow-2xs transition cursor-pointer"
            >
              <Edit3 size={14} />
              <span>{language === 'mr' ? 'प्रोफाइल बदला' : language === 'hi' ? 'प्रोफाइल अपडेट करें' : 'Update Profile'}</span>
            </button>
          </div>

          {/* Banner Title & Farmland Illustration */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#e0ece3] shadow-card flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
            <div className="max-w-3xl space-y-2 z-10">
              <h2 className="text-2xl sm:text-3xl font-black text-[#072a24] font-display tracking-tight">
                Recommended <span className="text-[#0c594d]">Business</span> Opportunities
              </h2>
              <p className="text-xs sm:text-sm text-[#527068] leading-relaxed">
                Based on your profile, location ({userLocationText}) and investment range ({userCapitalFormatted}), here are the best opportunities for you.
              </p>

              {/* Filter Chips Row */}
              <div className="pt-3 flex flex-wrap gap-2">
                {['All', 'Low Investment', 'High Returns', 'Quick Setup', 'Service Based'].map((filter) => {
                  const isActive = activeFilter === filter;
                  return (
                    <button
                      key={filter}
                      onClick={() => setActiveFilter(filter)}
                      className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                        isActive
                          ? 'bg-[#0c594d] text-white shadow-xs'
                          : 'bg-[#f0f6f2] text-[#47635b] hover:bg-[#e4ede7]'
                      }`}
                    >
                      {filter}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Village / Farmland Art on Right */}
            <div className="shrink-0 flex items-center justify-center">
              <div className="w-36 h-28 sm:w-44 sm:h-32 rounded-2xl bg-gradient-to-br from-[#eaf6ee] to-[#d8ede0] border border-[#c8e2d1] flex flex-col items-center justify-center p-3 relative shadow-inner">
                <div className="text-4xl sm:text-5xl animate-bounce-subtle">🏡🌾</div>
                <div className="absolute top-2 right-2 text-xl">☀️</div>
                <span className="text-[10px] font-black text-[#0c594d] uppercase tracking-wider mt-1">
                  GramVantage
                </span>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* HORIZONTAL ONE-LINE CAROUSEL HEADER & CONTROLS                            */}
          {/* ========================================================================= */}
          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-black uppercase tracking-wider text-[#075247]">
                Top Ranked Opportunities ({filteredList.length})
              </h3>
              <span className="text-xs text-[#527068] hidden sm:inline">
                • Scroll horizontally to explore all matches
              </span>
            </div>

            {/* Left / Right Scroll Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => scrollHorizontally('left')}
                className="w-8 h-8 rounded-full bg-white border border-[#d2e4d7] hover:bg-[#eaf4ed] text-[#075247] flex items-center justify-center shadow-xs transition cursor-pointer"
                title="Scroll Left"
              >
                <ChevronLeft size={18} />
              </button>
              <button
                onClick={() => scrollHorizontally('right')}
                className="w-8 h-8 rounded-full bg-white border border-[#d2e4d7] hover:bg-[#eaf4ed] text-[#075247] flex items-center justify-center shadow-xs transition cursor-pointer"
                title="Scroll Right"
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* HORIZONTAL ONE-LINE BUSINESS RECOMMENDATION CARDS                         */}
          {/* ========================================================================= */}
          <div
            ref={scrollContainerRef}
            className="flex gap-5 sm:gap-6 overflow-x-auto pb-4 pt-1 px-1 scroll-smooth snap-x snap-mandatory no-scrollbar"
          >
            {filteredList.map((biz, idx) => {
              const asset = getBusinessAsset(biz.business_name);
              const score = Math.round(biz.match_score || (95 - idx * 4));
              const isTop = idx === 0 || biz.match_level === 'Top Match';

              return (
                <div
                  key={biz.business_id || idx}
                  onClick={() => handleOpenDetail(biz.business_id || biz.id)}
                  className="w-[310px] sm:w-[360px] md:w-[390px] shrink-0 snap-start bg-white rounded-3xl border border-[#e2ede5] shadow-card hover:shadow-xl hover:border-emerald-300 transition-all duration-300 overflow-hidden cursor-pointer group flex flex-col justify-between"
                >
                  <div>
                    {/* Card Image with Badges & Fallback Handlers */}
                    <div className="relative h-44 sm:h-48 w-full overflow-hidden bg-slate-100">
                      <img
                        src={asset.image}
                        alt={biz.business_name}
                        onError={(e) => {
                          e.target.src = 'https://images.unsplash.com/photo-1595855759920-86582396756a?auto=format&fit=crop&w=800&q=80';
                        }}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />
                      
                      {/* Top Badges */}
                      <div className="absolute top-3 left-3 right-3 flex items-center justify-between gap-2">
                        {isTop ? (
                          <span className="px-2.5 py-1 rounded-full bg-emerald-600 text-white text-[11px] font-black flex items-center gap-1 shadow-md">
                            ⭐ Top Match
                          </span>
                        ) : (
                          <span />
                        )}

                        <span className="px-2.5 py-1 rounded-full bg-white/95 backdrop-blur-sm text-emerald-900 text-[11px] font-black flex items-center gap-1 shadow-md">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                          {score}% match
                        </span>
                      </div>
                    </div>

                    {/* Card Content & Title */}
                    <div className="p-4 sm:p-5">
                      <h3 className="text-base sm:text-lg font-black text-[#072a24] font-display group-hover:text-[#0c594d] transition-colors truncate">
                        {biz.business_name}
                      </h3>

                      {/* 3 Metric Pills */}
                      <div className="mt-3 grid grid-cols-3 gap-2 text-left">
                        <div className="flex items-center gap-1.5 text-xs text-[#527068] font-bold">
                          <span className="text-[#0c594d]">💵</span>
                          <span className="truncate">{asset.investmentRange}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-[#527068] font-bold">
                          <span className="text-[#0c594d]">⏱️</span>
                          <span className="truncate">{asset.setupTime}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-[#527068] font-bold">
                          <span className="text-[#0c594d]">📈</span>
                          <span className="truncate">{asset.demand}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card Bottom Action Bar */}
                  <div className="px-4 pb-4 sm:px-5 sm:pb-5 pt-2 flex items-center justify-between border-t border-[#f0f5f1]">
                    <span className="text-xs font-bold text-[#0c594d] group-hover:underline">
                      View Detailed Plan
                    </span>
                    <div className="w-8 h-8 rounded-full bg-[#edf7f0] group-hover:bg-[#0c594d] group-hover:text-white text-[#0c594d] flex items-center justify-center transition-colors shadow-2xs">
                      <ChevronRight size={16} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Refine CTA Banner */}
          <div className="bg-white rounded-3xl p-5 sm:p-6 border border-[#e0ece3] shadow-card flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <img src="/logo.png" alt="Aarambh Saathi" className="w-10 h-10 rounded-2xl object-cover shrink-0" />
              <div>
                <h4 className="text-xs sm:text-sm font-black text-[#072a24]">
                  Don't see what you're looking for?
                </h4>
                <p className="text-[11px] sm:text-xs text-[#527068]">
                  Tell us more about your interests or try speaking to Aarambh Saathi.
                </p>
              </div>
            </div>

            <button
              onClick={onBackToChat}
              className="px-5 py-2.5 rounded-xl bg-[#0c594d] hover:bg-[#084239] text-white font-black text-xs shadow-md transition cursor-pointer shrink-0"
            >
              Refine Recommendations
            </button>
          </div>

          {/* Voice Prompt Helper Card */}
          <div className="bg-white rounded-3xl p-5 sm:p-6 border border-[#e0ece3] shadow-card flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3.5 w-full md:w-auto">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#0c594d] to-[#15803d] text-white flex items-center justify-center shadow-md shrink-0">
                <Mic size={18} />
              </div>
              <div>
                <h4 className="text-xs font-black text-[#072a24]">
                  Ask Aarambh Saathi
                </h4>
                <p className="text-[11px] text-[#527068]">
                  You can ask questions like:
                </p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  <span className="px-2 py-0.5 rounded-md bg-[#f0f6f2] text-[10px] font-bold text-[#47635b]">
                    "Which business is best for me?"
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-[#f0f6f2] text-[10px] font-bold text-[#47635b]">
                    "Show low investment options"
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-[#f0f6f2] text-[10px] font-bold text-[#47635b]">
                    "Explain mushroom business"
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <span className="text-[11px] font-bold text-[#527068]">
                Speak in English, हिंदी or मराठी
              </span>
              <div className="flex items-center gap-1 text-[#0c594d]">
                <span className="w-1 h-3 bg-emerald-500 rounded-full animate-pulse" />
                <span className="w-1 h-5 bg-emerald-600 rounded-full animate-pulse" />
                <span className="w-1 h-2 bg-emerald-400 rounded-full animate-pulse" />
                <span className="w-1 h-6 bg-emerald-700 rounded-full animate-pulse" />
                <span className="w-1 h-3 bg-emerald-500 rounded-full animate-pulse" />
              </div>
            </div>
          </div>

        </div>
      )}

      {/* ========================================================================= */}
      {/* VIEW 2: BUSINESS DETAIL VIEW (DEEP-DIVE EXECUTION INTELLIGENCE)          */}
      {/* ========================================================================= */}
      {viewMode === 'detail' && (
        <div className="space-y-6 animate-fadeIn">
          
          {/* Top Bar: Back to Recommendations, Save, Share */}
          <div className="flex items-center justify-between">
            <button
              onClick={handleBackToList}
              className="flex items-center gap-1.5 text-xs font-bold text-[#426159] hover:text-[#072a24] transition cursor-pointer"
            >
              <ArrowLeft size={16} />
              <span>Back to Recommendations</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSaved(!isSaved)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition cursor-pointer ${
                  isSaved
                    ? 'bg-rose-50 border-rose-200 text-rose-600'
                    : 'bg-white border-[#cbe0d2] text-[#47635b] hover:bg-[#f2faf4]'
                }`}
              >
                <Heart size={14} className={isSaved ? 'fill-current' : ''} />
                <span>{isSaved ? 'Saved' : 'Save'}</span>
              </button>

              <button
                onClick={() => {
                  if (navigator.share) {
                    navigator.share({
                      title: currentBusiness?.business_name,
                      text: `Check out ${currentBusiness?.business_name} on Aarambh Saathi`,
                      url: window.location.href
                    }).catch(() => {});
                  } else {
                    navigator.clipboard.writeText(window.location.href);
                    alert('Link copied to clipboard!');
                  }
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white border border-[#cbe0d2] text-[#47635b] hover:bg-[#f2faf4] text-xs font-bold shadow-2xs transition cursor-pointer"
              >
                <Share2 size={14} />
                <span>Share</span>
              </button>
            </div>
          </div>

          {/* Hero Business Image: Only the single mentioned image */}
          <div className="rounded-3xl overflow-hidden shadow-card border border-[#e0ece3] bg-white p-2 sm:p-3">
            <div className="w-full h-64 sm:h-80 lg:h-96 rounded-2xl overflow-hidden relative">
              <img
                src={currentAsset.image}
                alt={currentBusiness?.business_name}
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1595855759920-86582396756a?auto=format&fit=crop&w=800&q=80';
                }}
                className="w-full h-full object-cover hover:scale-102 transition-transform duration-700"
              />
            </div>
          </div>

          {/* Title, Badges & Subtitle */}
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-black text-[#072a24] font-display">
                {currentBusiness?.business_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-black border border-emerald-300">
                {currentBusiness?.match_score || 92}% match
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-[#f0f6f2] text-[#47635b] text-xs font-bold border border-[#d2e5d8]">
                {currentAsset.badge}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#527068]">
              {currentAsset.tagline}
            </p>
          </div>

          {/* Internal Tab Navigation Bar */}
          <div className="border-b border-[#dbe8df] flex gap-6 overflow-x-auto no-scrollbar pt-1">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'feasibility', label: 'Feasibility' },
              { id: 'machinery', label: 'Machinery' },
              { id: 'financials', label: 'Financials' },
              { id: 'schemes', label: 'Schemes' },
              { id: 'market', label: 'Market' },
              { id: 'steps', label: 'Steps' }
            ].map((tab) => {
              const isActive = activeDetailTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveDetailTab(tab.id)}
                  className={`pb-3 text-xs sm:text-sm font-bold transition-all relative whitespace-nowrap cursor-pointer ${
                    isActive
                      ? 'text-[#0c594d] font-black'
                      : 'text-[#628076] hover:text-[#072a24]'
                  }`}
                >
                  <span>{tab.label}</span>
                  {isActive && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#0c594d] rounded-full" />
                  )}
                </button>
              );
            })}
          </div>

          {/* ================= TAB 1: OVERVIEW ================= */}
          {activeDetailTab === 'overview' && (
            <div className="space-y-6">
              
              {/* Quick Summary Grid */}
              <div className="bg-[#eef8f2] rounded-3xl p-5 border border-[#d2e8db] space-y-3">
                <div className="flex items-center gap-2 text-xs font-extrabold text-[#0c594d]">
                  <CheckCircle2 size={16} />
                  <span>Quick Summary</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
                  <div className="bg-white rounded-2xl p-3.5 border border-[#e0ece3] shadow-2xs">
                    <div className="flex items-center gap-2 text-[#0c594d]">
                      <DollarSign size={16} />
                      <span className="text-[10px] text-[#527068] font-bold">Estimated Investment</span>
                    </div>
                    <div className="mt-1 text-xs sm:text-sm font-black text-[#072a24]">
                      {currentAsset.totalInvestmentText ? `₹${currentAsset.totalInvestmentText}` : currentAsset.investmentRange}
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl p-3.5 border border-[#e0ece3] shadow-2xs">
                    <div className="flex items-center gap-2 text-[#0c594d]">
                      <Clock size={16} />
                      <span className="text-[10px] text-[#527068] font-bold">Setup Time</span>
                    </div>
                    <div className="mt-1 text-xs sm:text-sm font-black text-[#072a24]">
                      {currentAsset.setupTime}
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl p-3.5 border border-[#e0ece3] shadow-2xs">
                    <div className="flex items-center gap-2 text-[#0c594d]">
                      <TrendingUp size={16} />
                      <span className="text-[10px] text-[#527068] font-bold">Demand</span>
                    </div>
                    <div className="mt-1 text-xs sm:text-sm font-black text-[#072a24]">
                      {currentAsset.demandLevel}
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl p-3.5 border border-[#e0ece3] shadow-2xs">
                    <div className="flex items-center gap-2 text-[#0c594d]">
                      <Award size={16} />
                      <span className="text-[10px] text-[#527068] font-bold">Profit Potential</span>
                    </div>
                    <div className="mt-1 text-xs sm:text-sm font-black text-[#072a24]">
                      {currentAsset.profitPotential}
                    </div>
                  </div>
                </div>
              </div>

              {/* 2-Column: About the Business & Key Highlights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-3">
                  <h3 className="text-sm font-black text-[#072a24]">
                    About the Business
                  </h3>
                  <p className="text-xs text-[#527068] leading-relaxed">
                    {currentAsset.about}
                  </p>
                </div>

                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-3">
                  <h3 className="text-sm font-black text-[#072a24]">
                    Key Highlights
                  </h3>
                  <div className="space-y-2">
                    {currentAsset.highlights.map((h, idx) => (
                      <div key={idx} className="flex items-start gap-2.5 text-xs text-[#527068]">
                        <CheckCircle2 size={15} className="text-emerald-600 shrink-0 mt-0.5" />
                        <span>{h}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 2-Column: Investment Breakdown & Potential Returns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Investment Table */}
                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-3">
                  <h3 className="text-sm font-black text-[#072a24]">
                    Investment Breakdown (Estimated)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-[#eaf0eb] text-[#527068]">
                          <th className="pb-2 font-bold">Component</th>
                          <th className="pb-2 font-bold text-right">Estimated Cost (₹)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#f2f7f3]">
                        {currentAsset.breakdown.map((row, idx) => (
                          <tr key={idx} className="hover:bg-[#f9fbf9]">
                            <td className="py-2 text-[#47635b]">{row.item}</td>
                            <td className="py-2 text-right font-medium text-[#072a24]">{row.cost}</td>
                          </tr>
                        ))}
                        <tr className="font-black bg-[#edf7f0]">
                          <td className="py-2.5 px-2 rounded-l-lg text-[#075247]">Total</td>
                          <td className="py-2.5 px-2 rounded-r-lg text-right text-[#075247]">
                            ₹{currentAsset.totalInvestmentText}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Potential Returns */}
                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-3">
                  <h3 className="text-sm font-black text-[#072a24]">
                    Potential Returns
                  </h3>
                  <div className="space-y-3">
                    <div className="p-3 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] flex items-center justify-between">
                      <span className="text-xs text-[#527068] font-bold">Monthly Production</span>
                      <span className="text-xs font-black text-[#072a24]">{currentAsset.returns.production}</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] flex items-center justify-between">
                      <span className="text-xs text-[#527068] font-bold">Estimated Monthly Revenue</span>
                      <span className="text-xs font-black text-emerald-700">{currentAsset.returns.revenue}</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] flex items-center justify-between">
                      <span className="text-xs text-[#527068] font-bold">Estimated Monthly Profit</span>
                      <span className="text-xs font-black text-[#0c594d]">{currentAsset.returns.profit}</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] flex items-center justify-between">
                      <span className="text-xs text-[#527068] font-bold">ROI Period</span>
                      <span className="text-xs font-black text-amber-700">{currentAsset.returns.roi}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 2-Column: Market Demand Chart & Suitable For */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Market Demand Growth Chart */}
                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-black text-[#072a24]">
                      Market Demand
                    </h3>
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                      5-Year Growth Trend
                    </span>
                  </div>

                  <div className="pt-4 flex items-end justify-between gap-3 h-40 border-b border-l border-[#dbe6df] px-3 pb-2">
                    {currentAsset.marketTrend.map((bar) => {
                      const heightPercent = Math.round((bar.val / 250) * 100);
                      return (
                        <div key={bar.year} className="flex flex-col items-center gap-1.5 flex-1 group">
                          <div className="text-[9px] font-bold text-[#527068] opacity-0 group-hover:opacity-100 transition">
                            {bar.val}
                          </div>
                          <div
                            style={{ height: `${heightPercent}%` }}
                            className="w-full rounded-t-lg bg-gradient-to-t from-[#0c594d] to-[#22c55e] group-hover:brightness-110 transition-all shadow-xs"
                          />
                          <span className="text-[10px] font-bold text-[#527068]">
                            {bar.year}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Suitable For */}
                <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-3">
                  <h3 className="text-sm font-black text-[#072a24]">
                    Suitable For
                  </h3>
                  <div className="space-y-2.5">
                    {currentAsset.suitableFor.map((target, idx) => (
                      <div key={idx} className="flex items-center gap-2.5 text-xs text-[#47635b] font-medium">
                        <span className="w-6 h-6 rounded-full bg-emerald-50 text-[#0c594d] flex items-center justify-center text-xs">
                          👥
                        </span>
                        <span>{target}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Next Steps Stepper & CTA */}
              <div className="bg-white rounded-3xl p-6 border border-[#e0ece3] shadow-card space-y-4">
                <h3 className="text-sm font-black text-[#072a24]">
                  Next Steps
                </h3>

                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-2 sm:gap-4 overflow-x-auto w-full sm:w-auto">
                    {[
                      { step: 1, label: 'Check Feasibility', tab: 'feasibility' },
                      { step: 2, label: 'View Machinery', tab: 'machinery' },
                      { step: 3, label: 'Explore Schemes', tab: 'schemes' },
                      { step: 4, label: 'Create Business Plan', tab: 'steps' }
                    ].map((s, i) => (
                      <button
                        key={s.step}
                        onClick={() => setActiveDetailTab(s.tab)}
                        className="flex items-center gap-2 group cursor-pointer text-left shrink-0"
                      >
                        <div className="w-7 h-7 rounded-full bg-[#0c594d] text-white font-black text-xs flex items-center justify-center shadow-xs">
                          {s.step}
                        </div>
                        <span className="text-xs font-bold text-[#072a24] group-hover:text-[#0c594d]">
                          {s.label}
                        </span>
                        {i < 3 && <span className="text-slate-300 font-bold ml-1">→</span>}
                      </button>
                    ))}
                  </div>

                  <button
                    onClick={() => setActiveDetailTab('feasibility')}
                    className="px-6 py-3 rounded-2xl bg-[#0c594d] hover:bg-[#084239] text-white font-black text-xs shadow-md transition flex items-center gap-2 cursor-pointer shrink-0"
                  >
                    <span>Check Feasibility</span>
                    <ArrowRight size={15} />
                  </button>
                </div>
              </div>

            </div>
          )}

          {/* ================= TAB 2: FEASIBILITY ================= */}
          {activeDetailTab === 'feasibility' && (
            <div className="space-y-6">
              {feasibility ? (
                <FeasibilityCard
                  feasibility={feasibility}
                  selectedBusinessName={currentBusiness?.business_name}
                  language={language}
                />
              ) : (
                <div className="bg-white rounded-3xl p-8 border border-[#e0ece3] text-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-emerald-50 text-[#0c594d] flex items-center justify-center mx-auto">
                    <ShieldCheck size={24} />
                  </div>
                  <h3 className="text-base font-bold text-[#072a24]">Evaluating Local Feasibility</h3>
                  <p className="text-xs text-[#527068] max-w-md mx-auto">
                    Computing resource availability, raw material access, power, water & mandi logistics in {userLocationText}.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* ================= TAB 3: MACHINERY ================= */}
          {activeDetailTab === 'machinery' && (
            <div className="space-y-6">
              <BusinessSetupCard
                businessId={currentBusiness?.id || currentBusiness?.business_id}
                businessName={currentBusiness?.business_name}
                businessScale={profile.scale || 'small'}
                userLocation={`${profile.district || profile.location || ''} ${profile.state || ''}`.trim()}
                userBudget={profile.capital || profile.available_investment || undefined}
                userProfile={profile}
                feasibilityResult={feasibility}
                language={language}
              />
            </div>
          )}

          {/* ================= TAB 4: FINANCIALS ================= */}
          {activeDetailTab === 'financials' && (
            <div className="space-y-6">
              <FinancialSummary
                initialCost={currentBusiness?.required_investment || currentAsset.minInvestment || 120000}
                userCapital={profile.capital || profile.available_investment || 15000}
                businessId={currentBusiness?.id || currentBusiness?.business_id}
                businessName={currentBusiness?.business_name}
                userProfile={profile}
                onPlanUpdated={onUpdateFinancialPlan}
                language={language}
              />
            </div>
          )}

          {/* ================= TAB 5: SCHEMES ================= */}
          {activeDetailTab === 'schemes' && (
            <div className="space-y-6">
              <SchemesCard schemes={schemes} language={language} />
            </div>
          )}

          {/* ================= TAB 6: MARKET ================= */}
          {activeDetailTab === 'market' && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#e0ece3] shadow-card space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-black text-[#072a24]">
                    Market Analysis & Buyer Linkage
                  </h3>
                  <p className="text-xs text-[#527068] mt-0.5">
                    Local wholesale buyers, institutional procurement, and retail demand in {userLocationText}.
                  </p>
                </div>
                <span className="px-3 py-1 rounded-full bg-emerald-100 text-[#0c594d] text-xs font-bold">
                  High Demand Sector
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] space-y-2">
                  <h4 className="text-xs font-black text-[#072a24]">Target Consumer Base</h4>
                  <ul className="text-xs text-[#527068] space-y-1.5 list-disc list-inside">
                    <li>Local neighborhood grocery stores and weekly village haats</li>
                    <li>Hotels, dhabas, caterers, and roadside highway food joints</li>
                    <li>Direct-to-consumer farmgate sales at 20% higher realization</li>
                    <li>Taluka APMC Mandi wholesale commission agents</li>
                  </ul>
                </div>

                <div className="p-4 rounded-2xl bg-[#f5f9f6] border border-[#e4ede7] space-y-2">
                  <h4 className="text-xs font-black text-[#072a24]">Competitive Advantage</h4>
                  <ul className="text-xs text-[#527068] space-y-1.5 list-disc list-inside">
                    <li>Fresh harvest delivers better shelf-life than transported urban supplies</li>
                    <li>Zero middleman transportation costs within 15 km radius</li>
                    <li>Personal relationship and credit trust with local buyers</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* ================= TAB 7: STEPS / DPR REPORT ================= */}
          {activeDetailTab === 'steps' && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#e0ece3] shadow-card text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-[#0c594d] flex items-center justify-center mx-auto text-2xl">
                📄
              </div>
              <h3 className="text-lg font-black text-[#072a24]">
                90-Day Execution Roadmap & Bank DPR
              </h3>
              <p className="text-xs text-[#527068] max-w-lg mx-auto">
                Download your complete Detailed Project Report (DPR) with week-by-week implementation milestones, machinery quotes, Mudra loan documentation, and scheme application forms.
              </p>
              <button
                onClick={() => onOpenReport(currentBusiness?.business_id || currentBusiness?.id)}
                className="px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-500 to-[#0c594d] text-slate-950 font-black text-xs shadow-md hover:shadow-lg transition cursor-pointer inline-flex items-center gap-2"
              >
                <FileText size={16} />
                <span>Generate Official Bank DPR Report</span>
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
