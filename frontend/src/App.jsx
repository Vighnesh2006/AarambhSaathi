import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HomeView from './components/HomeView';
import AboutView from './components/AboutView';
import VoiceChatMode from './components/VoiceChatMode';
import TextChatMode from './components/TextChatMode';
import ProfileCard from './components/ProfileCard';
import RecommendationCard from './components/RecommendationCard';
import FeasibilityCard from './components/FeasibilityCard';
import FinancialSummary from './components/FinancialSummary';
import SchemesCard from './components/SchemesCard';
import BusinessSetupCard from './components/BusinessSetupCard';
import ReportModal from './components/ReportModal';
import CatalogueModal from './components/CatalogueModal';
import AdminLoginModal from './components/AdminLoginModal';
import { getTranslation } from './services/translations';

import {
  sendChatMessage,
  getRecommendations,
  getFeasibility,
  matchSchemes,
  generateReport,
  fetchTrainStatus,
  fetchBusinesses
} from './services/api';

import {
  Sprout,
  Users,
  TrendingUp,
  Landmark,
  FileText,
  X,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Lock
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'about' | 'chat' | 'catalogue' | 'schemes'
  const [chatMode, setChatMode] = useState('text'); // 'text' | 'voice'
  const [language, setLanguage] = useState('en');
  const t = getTranslation(language);

  // Authentication & RBAC State: 'user' | 'admin'
  const [userRole, setUserRole] = useState(() => {
    return localStorage.getItem('aarambh_user_role') || 'user';
  });
  const [isAdminLoginOpen, setIsAdminLoginOpen] = useState(false);

  // Journey step in advisory flow (1: Understand, 2: Opportunities, 3: Finance, 4: Schemes, 5: DPR Plan)
  const [journeyStep, setJourneyStep] = useState(1);
  const [isProfileDrawerOpen, setIsProfileDrawerOpen] = useState(false);

  // Profile State
  const [profile, setProfile] = useState({
    name: null,
    location: null,
    district: null,
    state: null,
    occupation: null,
    skills: [],
    experience: null,
    capital: null,
    resources: [],
    business_interest: null,
    goal: null,
    scale: null,
    constraints: [],
    language: 'en'
  });

  // Session ID for Stateful Multi-Turn Conversation
  const [sessionId, setSessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36));

  // Multilingual Initial Greeting for Aarambh Saathi
  const getInitialGreeting = (lang) => {
    if (lang === 'mr') {
      return `नमस्कार! 👋 आपले नाव काय आहे?`;
    }
    if (lang === 'hi') {
      return `नमस्कार! 👋 आपका नाम क्या है?`;
    }
    return `Namaskar! 👋 What is your name?`;
  };

  // Chat Messages State
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: getInitialGreeting('en'),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [suggestedReplies, setSuggestedReplies] = useState([]);
  const [isProfileReady, setIsProfileReady] = useState(false);

  // Analysis Intelligence Results
  const [recommendations, setRecommendations] = useState([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState(null);
  const [feasibility, setFeasibility] = useState(null);
  const [schemes, setSchemes] = useState([]);
  const [financialPlan, setFinancialPlan] = useState(null);

  // Modals & Metadata
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [generatedReportData, setGeneratedReportData] = useState(null);
  const [isCatalogueModalOpen, setIsCatalogueModalOpen] = useState(false);
  const [totalCatalogueItems, setTotalCatalogueItems] = useState(90);

  // On initial mount, fetch catalogue metadata
  useEffect(() => {
    fetchTrainStatus()
      .then((data) => {
        if (data.total_businesses) {
          setTotalCatalogueItems(data.total_businesses);
        }
      })
      .catch((err) => console.log('Status error:', err));
  }, []);

  // Admin Login handler
  const handleAdminLoginSuccess = (adminData) => {
    setUserRole('admin');
    localStorage.setItem('aarambh_user_role', 'admin');
    setIsAdminLoginOpen(false);
  };

  // Admin Logout handler
  const handleAdminLogout = () => {
    setUserRole('user');
    localStorage.removeItem('aarambh_user_role');
    if (activeTab === 'catalogue' || activeTab === 'schemes') {
      setActiveTab('home');
    }
  };

  // Language switch
  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    setProfile((prev) => ({ ...prev, language: newLang }));
    if (messages.length <= 1) {
      setMessages([
        {
          role: 'assistant',
          content: getInitialGreeting(newLang),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  };

  // Reset conversation & profile
  const handleReset = () => {
    const emptyProfile = {
      name: null,
      location: null,
      district: null,
      state: null,
      occupation: null,
      skills: [],
      experience: null,
      capital: null,
      resources: [],
      business_interest: null,
      goal: null,
      scale: null,
      constraints: [],
      language
    };
    setProfile(emptyProfile);
    setRecommendations([]);
    setSelectedBusinessId(null);
    setFeasibility(null);
    setSchemes([]);
    setFinancialPlan(null);
    setGeneratedReportData(null);
    setIsProfileReady(false);
    setJourneyStep(1);
    const newSessionId = 'sess_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
    setSessionId(newSessionId);
    setMessages([
      {
        role: 'assistant',
        content: getInitialGreeting(language),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  // Advisory pipeline trigger
  const runAnalysisPipeline = async (currentProfile, preferredBusinessId = null) => {
    try {
      // 1. Recommendations
      const recRes = await getRecommendations(currentProfile);
      if (recRes && recRes.recommendations.length > 0) {
        setRecommendations(recRes.recommendations);
        const activeId = preferredBusinessId || selectedBusinessId || recRes.recommendations[0].business_id;
        setSelectedBusinessId(activeId);

        // 2. Feasibility
        const feasRes = await getFeasibility(activeId, currentProfile);
        setFeasibility(feasRes);

        // 3. Schemes
        const selectedRec = recRes.recommendations.find((r) => r.business_id === activeId) || recRes.recommendations[0];
        const schemeRes = await matchSchemes(
          currentProfile,
          activeId,
          selectedRec.category,
          selectedRec.required_investment
        );
        setSchemes(schemeRes);
        setJourneyStep(3);
      }
    } catch (err) {
      console.error('Error in advisory pipeline:', err);
    }
  };

  // Send message handler (works for both text and voice input)
  const handleSendMessage = async (text) => {
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = { role: 'user', content: text, timestamp: now };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    setIsLoading(true);

    try {
      const res = await sendChatMessage(
        text,
        updatedHistory.map((m) => ({ role: m.role, content: m.content })),
        profile,
        language,
        sessionId
      );

      const aiMsg = {
        role: 'assistant',
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages([...updatedHistory, aiMsg]);
      setSuggestedReplies(res.suggested_quick_replies || []);
      setIsProfileReady(res.is_profile_ready);

      if (res.updated_profile) {
        setProfile(res.updated_profile);
        await runAnalysisPipeline(res.updated_profile);
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages([
        ...updatedHistory,
        {
          role: 'assistant',
          content: 'I encountered an issue processing your request. Please check the backend server.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Switch selected business
  const handleSelectBusiness = async (bizId) => {
    setSelectedBusinessId(bizId);
    try {
      const feasRes = await getFeasibility(bizId, profile);
      setFeasibility(feasRes);

      const selectedRec = recommendations.find((r) => r.business_id === bizId);
      if (selectedRec) {
        const schemeRes = await matchSchemes(
          profile,
          bizId,
          selectedRec.category,
          selectedRec.required_investment
        );
        setSchemes(schemeRes);
      }
    } catch (err) {
      console.error('Error updating business:', err);
    }
  };

  // Generate 90-Day DPR Report
  const handleOpenReport = async () => {
    const targetBusinessId = selectedBusinessId || recommendations?.[0]?.business_id;
    if (!targetBusinessId) {
      // Profile not ready yet: open ReportModal in helper/guidance mode
      setGeneratedReportData(null);
      setIsReportOpen(true);
      return;
    }

    try {
      const targetCost = financialPlan?.project_cost || recommendations?.find((r) => r.business_id === targetBusinessId)?.required_investment;
      const res = await generateReport(
        profile,
        targetBusinessId,
        targetCost
      );
      setGeneratedReportData(res);
      setIsReportOpen(true);
      setJourneyStep(5);
    } catch (err) {
      console.error('Error generating report:', err);
      // Fallback: open helper state inside ReportModal
      setGeneratedReportData(null);
      setIsReportOpen(true);
    }
  };

  // Journey step click routing
  const handleJourneyStepClick = (step) => {
    setJourneyStep(step);
    if (step === 1) {
      setIsProfileDrawerOpen(true);
    } else if (step === 2) {
      const el = document.getElementById('opportunities-section');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        handleSendMessage(
          language === 'mr'
            ? 'माझ्या कौशल्यानुसार व्यवसाय संधी सांगा.'
            : language === 'hi'
            ? 'मेरे हुनर और क्षेत्र के अनुसार व्यवसाय के अवसर बताएं।'
            : 'Show me recommended business opportunities.'
        );
      }
    } else if (step === 3) {
      const el = document.getElementById('finance-section');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        handleSendMessage(
          language === 'mr'
            ? 'माझे कर्ज, अनुदान आणि मासिक हप्ता (EMI) मोजा.'
            : language === 'hi'
            ? 'मेरा लोन, सब्सिडी और मासिक EMI की गणना करें।'
            : 'Calculate my loan, EMI and financial model.'
        );
      }
    } else if (step === 4) {
      const el = document.getElementById('schemes-section');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        handleSendMessage(
          language === 'mr'
            ? 'माझ्या व्यवसायासाठी शासकीय अनुदान योजनांची माहिती द्या.'
            : language === 'hi'
            ? 'मेरे व्यवसाय के लिए सरकारी सब्सिडी योजनाओं की जानकारी दें।'
            : 'Show me relevant government subsidy schemes.'
        );
      }
    } else if (step === 5) {
      handleOpenReport();
    }
  };

  // Direct selection from catalogue
  const handleSelectFromCatalogue = (biz) => {
    const updatedProfile = {
      ...profile,
      business_interest: biz.business_name,
      skills: Array.from(new Set([...(profile.skills || []), ...(biz.required_skills || [])]))
    };
    setProfile(updatedProfile);
    runAnalysisPipeline(updatedProfile, biz.id);
    setActiveTab('chat');
  };

  // Active recommended business
  const activeBusiness = recommendations.find((r) => r.business_id === selectedBusinessId) || recommendations[0];

  return (
    <div className="min-h-screen flex flex-col bg-[#f5f8f3] text-[#123c3a]">
      
      {/* ================= TOP NAVBAR ================= */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={handleLanguageChange}
        onReset={handleReset}
        onOpenReport={handleOpenReport}
        onOpenProfileDrawer={() => setIsProfileDrawerOpen(true)}
        totalBusinesses={totalCatalogueItems}
        userRole={userRole}
        onOpenAdminLogin={() => setIsAdminLoginOpen(true)}
        onAdminLogout={handleAdminLogout}
      />

      {/* ================= MAIN VIEW ROUTER ================= */}
      <main className="flex-1 w-full">
        
        {/* VIEW 1: HOME (Accessible to all users & admin) */}
        {activeTab === 'home' && (
          <HomeView
            onStartJourney={() => setActiveTab('chat')}
            onOpenCatalogue={() => {
              if (userRole === 'admin') {
                setIsCatalogueModalOpen(true);
              } else {
                setActiveTab('chat');
              }
            }}
            onSelectCategory={(cat) => {
              setProfile((prev) => ({ ...prev, business_interest: cat }));
              setActiveTab('chat');
              handleSendMessage(`I am interested in opportunities under ${cat}.`);
            }}
            language={language}
          />
        )}

        {/* VIEW 2: ABOUT (Accessible to all users & admin) */}
        {activeTab === 'about' && (
          <AboutView
            onStartJourney={() => setActiveTab('chat')}
            language={language}
          />
        )}

        {/* VIEW 3: CHAT / ADVISORY (Accessible to all users & admin) */}
        {activeTab === 'chat' && (
          <div className="max-w-[1500px] mx-auto p-4 sm:p-6 lg:p-8">
            
            {/* Mode Toggle Header */}
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#527068]">
                  Interaction Mode:
                </span>
                <div className="flex rounded-xl bg-white p-1 border border-[#d6e5da] shadow-2xs">
                  <button
                    onClick={() => setChatMode('voice')}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      chatMode === 'voice'
                        ? 'bg-[#075247] text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    🎙️ {t.voiceTitle.split(' ')[0]} (Voice)
                  </button>
                  <button
                    onClick={() => setChatMode('text')}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      chatMode === 'text'
                        ? 'bg-[#075247] text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    💬 {t.navChat} (Text)
                  </button>
                </div>
              </div>

              {/* Quick Jump to Generated Plan */}
              {recommendations.length > 0 && (
                <button
                  onClick={handleOpenReport}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-[#15803d] text-slate-950 font-extrabold text-xs shadow-md animate-soft-pulse hover:brightness-105 transition"
                >
                  <FileText size={15} />
                  <span>{t.journeyGenReportBtn} Ready</span>
                </button>
              )}
            </div>

            {/* Voice Mode */}
            {chatMode === 'voice' && (
              <VoiceChatMode
                onSendMessage={handleSendMessage}
                onSwitchToText={() => setChatMode('text')}
                language={language}
                isLoading={isLoading}
              />
            )}

            {/* Text Chat Mode */}
            {chatMode === 'text' && (
              <TextChatMode
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                suggestedReplies={suggestedReplies}
                onClearChat={handleReset}
                language={language}
                onSwitchToVoice={() => setChatMode('voice')}
                journeyStep={journeyStep}
                onJourneyStepClick={handleJourneyStepClick}
                isProfileReady={isProfileReady || recommendations.length > 0}
                onOpenReport={handleOpenReport}
              />
            )}

            {/* Live Intelligence Cards Container */}
            {recommendations.length > 0 && (
              <div id="decision-support-container" className="mt-8 space-y-6 pt-6 border-t border-slate-200 scroll-mt-10">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  <h3 className="text-xl font-black text-[#072a24] font-display">
                    {t.journeyTitle} — Decision Support
                  </h3>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Top 3 Recommendations */}
                  <div className="lg:col-span-6 scroll-mt-20" id="opportunities-section">
                    <RecommendationCard
                      recommendations={recommendations}
                      selectedBusinessId={selectedBusinessId}
                      onSelectBusiness={handleSelectBusiness}
                    />
                  </div>

                  {/* Business Setup & Machinery Planner */}
                  <div className="lg:col-span-6 scroll-mt-20" id="machinery-section">
                    {activeBusiness && (
                      <BusinessSetupCard
                        businessName={activeBusiness.business_name}
                        businessScale={profile.scale || 'small'}
                        userLocation={`${profile.district || profile.location || ''} ${profile.state || ''}`.trim()}
                        userBudget={profile.capital || undefined}
                      />
                    )}
                  </div>

                  {/* Feasibility */}
                  {feasibility && (
                    <div className="lg:col-span-6 scroll-mt-20" id="feasibility-section">
                      <FeasibilityCard
                        feasibility={feasibility}
                        selectedBusinessName={activeBusiness?.business_name}
                      />
                    </div>
                  )}

                  {/* Financial Structuring */}
                  <div className="lg:col-span-6 scroll-mt-20" id="finance-section">
                    <FinancialSummary
                      initialCost={activeBusiness?.required_investment || 140000}
                      userCapital={profile.capital || 15000}
                      onPlanUpdated={setFinancialPlan}
                    />
                  </div>

                  {/* Matched Schemes */}
                  <div className="lg:col-span-12 scroll-mt-20" id="schemes-section">
                    <SchemesCard schemes={schemes} />
                  </div>
                </div>
              </div>
            )}

          </div>
        )}

        {/* VIEW 4: CATALOGUE (Admin Only Access) */}
        {activeTab === 'catalogue' && (
          userRole === 'admin' ? (
            <div className="max-w-[1500px] mx-auto p-4 sm:p-8">
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl sm:text-3xl font-black text-[#072a24] font-display">
                      {t.exploreTitle} ({totalCatalogueItems} {t.exploreBadge})
                    </h2>
                    <span className="bg-amber-400 text-slate-950 text-xs font-black px-2.5 py-0.5 rounded-full uppercase">
                      Admin Control
                    </span>
                  </div>
                  <p className="text-sm text-[#527068] mt-1">
                    Manage catalogue records, upload Excel datasets, and trigger automated ML model retraining.
                  </p>
                </div>
              </div>

              {/* Embed Catalogue modal interface directly in view */}
              <div className="bg-white rounded-3xl p-6 border border-[#d6e5da] shadow-card">
                <CatalogueModal
                  isOpen={true}
                  onClose={() => setActiveTab('home')}
                  onSelectBusinessForAnalysis={handleSelectFromCatalogue}
                />
              </div>
            </div>
          ) : (
            <div className="max-w-md mx-auto my-16 p-8 bg-white rounded-3xl border border-slate-200 shadow-xl text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mx-auto">
                <Lock size={28} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Admin Authentication Required</h3>
              <p className="text-xs text-slate-500">
                The Catalogue Manager & Dataset Retraining Suite is restricted to administrative staff.
              </p>
              <button
                onClick={() => setIsAdminLoginOpen(true)}
                className="w-full py-3 rounded-xl bg-[#075247] text-white font-bold text-sm shadow-md"
              >
                Login as Administrator
              </button>
            </div>
          )
        )}

        {/* VIEW 5: SCHEMES (Admin Only Access) */}
        {activeTab === 'schemes' && (
          userRole === 'admin' ? (
            <div className="max-w-[1500px] mx-auto p-4 sm:p-8 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl sm:text-3xl font-black text-[#072a24] font-display">
                      {t.aboutFeatGovtSchemes} & Subsidies
                    </h2>
                    <span className="bg-amber-400 text-slate-950 text-xs font-black px-2.5 py-0.5 rounded-full uppercase">
                      Admin Sync
                    </span>
                  </div>
                  <p className="text-sm text-[#527068] mt-1">
                    60+ verified central & state subsidy schemes cross-referenced with myScheme.gov.in.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-8">
                  <SchemesCard schemes={schemes} />
                </div>
                <div className="lg:col-span-4 space-y-4">
                  <div className="p-6 bg-white rounded-3xl border border-[#d6e5da] shadow-card">
                    <h4 className="font-extrabold text-base text-[#072a24] mb-2">
                      Official Verification Portal
                    </h4>
                    <p className="text-xs text-[#527068] leading-relaxed mb-4">
                      All scheme data is verified directly from official Ministry guidelines and myScheme.gov.in.
                    </p>
                    <a
                      href="https://www.myscheme.gov.in"
                      target="_blank"
                      rel="noreferrer"
                      className="block w-full py-2.5 rounded-xl bg-emerald-50 border border-emerald-300 text-center text-xs font-bold text-[#075247] hover:bg-emerald-100 transition"
                    >
                      Open myScheme.gov.in ↗
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-md mx-auto my-16 p-8 bg-white rounded-3xl border border-slate-200 shadow-xl text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mx-auto">
                <Lock size={28} />
              </div>
              <h3 className="text-xl font-bold text-slate-900">Admin Authentication Required</h3>
              <p className="text-xs text-slate-500">
                Official Scheme Synchronization & Analytics is restricted to administrative staff.
              </p>
              <button
                onClick={() => setIsAdminLoginOpen(true)}
                className="w-full py-3 rounded-xl bg-[#075247] text-white font-bold text-sm shadow-md"
              >
                Login as Administrator
              </button>
            </div>
          )
        )}

      </main>

      {/* ================= ADMIN LOGIN MODAL ================= */}
      <AdminLoginModal
        isOpen={isAdminLoginOpen}
        onClose={() => setIsAdminLoginOpen(false)}
        onLoginSuccess={handleAdminLoginSuccess}
      />

      {/* ================= USER PROFILE DRAWER / MODAL ================= */}
      {isProfileDrawerOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 border border-slate-200 shadow-2xl relative">
            <button
              onClick={() => setIsProfileDrawerOpen(false)}
              className="absolute top-5 right-5 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700"
            >
              <X size={18} />
            </button>
            <ProfileCard
              profile={profile}
              onUpdateProfile={(updated) => {
                setProfile(updated);
                runAnalysisPipeline(updated);
              }}
            />
          </div>
        </div>
      )}

      {/* ================= REPORT MODAL (90-DAY DPR) ================= */}
      <ReportModal
        report={generatedReportData}
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        isProfileReady={isProfileReady || recommendations.length > 0}
        onStartChat={() => setActiveTab('chat')}
      />

      {/* ================= CATALOGUE MODAL ================= */}
      {isCatalogueModalOpen && (
        <CatalogueModal
          isOpen={isCatalogueModalOpen}
          onClose={() => setIsCatalogueModalOpen(false)}
          onSelectBusinessForAnalysis={handleSelectFromCatalogue}
        />
      )}

    </div>
  );
}
