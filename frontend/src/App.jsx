import React, { useState, useEffect } from 'react';
import { speakText, stopSpeaking } from './services/voice';
import TopNavbar from './components/TopNavbar';
import HomeView from './components/HomeView';
import AboutView from './components/AboutView';
import RecommendationsView from './components/RecommendationsView';
import VoiceChatMode from './components/VoiceChatMode';
import TextChatMode from './components/TextChatMode';
import ProfileCard from './components/ProfileCard';
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
  Lock,
  MessageCircle,
  RotateCcw
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'profile' | 'recommendations' | 'feasibility' | 'machinery' | 'financial' | 'schemes' | 'business_plan' | 'about' | 'chat' | 'catalogue'
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
    intent: null,
    age: null,
    gender: null,
    village: null,
    district: null,
    state: null,
    location: null,
    education: null,
    occupation: null,
    skills: [],
    experience: null,
    resources: [],
    available_investment: null,
    capital: null,
    business_interest: null,
    existing_business: null,
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
  const [pipelineLoading, setPipelineLoading] = useState(false);

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
    if (activeTab === 'catalogue') {
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
      intent: null,
      age: null,
      gender: null,
      village: null,
      district: null,
      state: null,
      location: null,
      education: null,
      occupation: null,
      skills: [],
      experience: null,
      resources: [],
      available_investment: null,
      capital: null,
      business_interest: null,
      existing_business: null,
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
    setPipelineLoading(true);
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
        setJourneyStep(2);

        // Take user directly to the Recommendations Screen
        setActiveTab('recommendations');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Error in advisory pipeline:', err);
    } finally {
      setPipelineLoading(false);
    }
  };

  // Send message handler
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
      
      if (chatMode === 'voice') {
        speakText(res.reply, language);
      }

      if (res.updated_profile) {
        setProfile(res.updated_profile);
        if (res.is_profile_ready) {
          await runAnalysisPipeline(res.updated_profile);
        }
      }

      if (
        text.includes('उपयुक्त व्यवसाय') ||
        text.includes('योग्य व्यवसाय') ||
        text.includes('सर्वोत्कृष्ट व्यवसाय') ||
        text.includes('Suggest Best') ||
        text.includes('business opportunities')
      ) {
        setActiveTab('recommendations');
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
    if (bizId === selectedBusinessId && feasibility) return;
    
    setSelectedBusinessId(bizId);
    setFeasibility(null);
    setFinancialPlan(null);
    setSchemes([]);
    setGeneratedReportData(null);
    setPipelineLoading(true);

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
    } finally {
      setPipelineLoading(false);
    }
  };

  // Generate 90-Day DPR Report
  const handleOpenReport = async (preferredBizId = null) => {
    const targetBusinessId = preferredBizId || selectedBusinessId || recommendations?.[0]?.business_id || 'milk_testing';
    setIsReportOpen(true);

    try {
      const selectedRec = recommendations?.find((r) => r.business_id === targetBusinessId) || recommendations?.[0] || {
        business_id: targetBusinessId,
        business_name: activeBusiness?.business_name || 'Milk Quality Testing Service',
        required_investment: 100000,
        match_score: 92
      };
      const targetCost = financialPlan?.project_cost || selectedRec?.required_investment || 100000;
      const res = await generateReport(
        profile,
        targetBusinessId,
        targetCost,
        profile.scale || 'starter',
        {
          recommendation: selectedRec,
          feasibility: feasibility,
          financialPlan: financialPlan,
          schemeMatches: schemes,
          language: language
        }
      );
      if (res) {
        setGeneratedReportData(res);
      }
      setJourneyStep(5);
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };

  const handleJourneyStepClick = (step) => {
    setJourneyStep(step);
    if (step === 1) {
      setIsProfileDrawerOpen(true);
    } else if (step === 2) {
      setActiveTab('recommendations');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (step === 3) {
      setActiveTab('financial');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (step === 4) {
      setActiveTab('schemes');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (step === 5) {
      handleOpenReport();
    }
  };

  const activeBusiness = recommendations.find((r) => r.business_id === selectedBusinessId) || recommendations[0];

  return (
    <div className="min-h-screen flex flex-col bg-[#f5f8f3] text-[#123c3a] font-sans antialiased">
      
      {/* ================= TOP HEADER NAVIGATION ONLY (NO SIDEBAR) ================= */}
      <TopNavbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={handleLanguageChange}
        onReset={handleReset}
        onOpenReport={handleOpenReport}
        onOpenProfileDrawer={() => setIsProfileDrawerOpen(true)}
        onOpenVoiceChat={() => {
          setActiveTab('chat');
          setChatMode('voice');
        }}
        userRole={userRole}
        profile={profile}
        hasRecommendations={recommendations && recommendations.length > 0}
        onOpenAdminLogin={() => setIsAdminLoginOpen(true)}
        onAdminLogout={handleAdminLogout}
      />

      {/* ================= FULL-WIDTH MAIN CONTENT AREA ================= */}
      <main className="flex-1 w-full pb-16">
        
        {/* VIEW 1: HOME */}
        {activeTab === 'home' && (
          <HomeView
            onStartJourney={() => setActiveTab('chat')}
            onOpenCatalogue={() => {
              if (userRole === 'admin') {
                setIsCatalogueModalOpen(true);
              } else {
                setActiveTab('recommendations');
              }
            }}
            onSelectCategory={(cat) => {
              const updatedProfile = {
                ...profile,
                business_interest: cat,
                skills: [cat],
                capital: profile.capital || 100000
              };
              setProfile(updatedProfile);
              setActiveTab('chat');
              handleSendMessage(`I am interested in opportunities under ${cat}.`);
              runAnalysisPipeline(updatedProfile);
            }}
            language={language}
          />
        )}

        {/* VIEW 2: RECOMMENDATIONS & OPPORTUNITIES (HORIZONTAL ONE-LINE CAROUSEL) */}
        {activeTab === 'recommendations' && (
          <RecommendationsView
            recommendations={recommendations}
            selectedBusinessId={selectedBusinessId}
            onSelectBusiness={handleSelectBusiness}
            profile={profile}
            feasibility={feasibility}
            schemes={schemes}
            financialPlan={financialPlan}
            onUpdateFinancialPlan={setFinancialPlan}
            onOpenReport={handleOpenReport}
            onUpdateProfile={() => setActiveTab('chat')}
            onBackToChat={() => setActiveTab('chat')}
            language={language}
          />
        )}

        {/* VIEW 3: PROFILE MANAGEMENT */}
        {activeTab === 'profile' && (
          <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fadeIn">
            <ProfileCard
              profile={profile}
              onUpdateProfile={(updated) => {
                setProfile(updated);
                if (isProfileReady) {
                  runAnalysisPipeline(updated);
                }
              }}
              isDrawer={false}
              journeyStep={journeyStep}
              onJourneyStepClick={handleJourneyStepClick}
              language={language}
            />
          </div>
        )}

        {/* VIEW 4: FEASIBILITY CHECK */}
        {activeTab === 'feasibility' && (
          <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fadeIn">
            <FeasibilityCard
              feasibility={feasibility}
              selectedBusinessName={activeBusiness?.business_name || 'Selected Opportunity'}
              language={language}
            />
          </div>
        )}

        {/* VIEW 5: MACHINERY & SUPPLIERS */}
        {activeTab === 'machinery' && (
          <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fadeIn">
            <BusinessSetupCard
              businessId={activeBusiness?.id || activeBusiness?.business_id || 'general'}
              businessName={activeBusiness?.business_name || 'Milk Quality Testing Service'}
              businessScale={profile.scale || 'small'}
              userLocation={`${profile.district || profile.location || 'Pune'} ${profile.state || 'Maharashtra'}`.trim()}
              userBudget={profile.capital || profile.available_investment || undefined}
              userProfile={profile}
              feasibilityResult={feasibility}
              language={language}
            />
          </div>
        )}

        {/* VIEW 6: FINANCIAL PLANNING */}
        {activeTab === 'financial' && (
          <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fadeIn">
            <FinancialSummary
              initialCost={activeBusiness?.required_investment || 120000}
              userCapital={profile.capital || profile.available_investment || 15000}
              businessId={activeBusiness?.id || activeBusiness?.business_id || 'general'}
              businessName={activeBusiness?.business_name || 'Milk Quality Testing Service'}
              userProfile={profile}
              onPlanUpdated={setFinancialPlan}
              language={language}
            />
          </div>
        )}

        {/* VIEW 7: GOVERNMENT SCHEMES */}
        {activeTab === 'schemes' && (
          <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 animate-fadeIn">
            <SchemesCard schemes={schemes} language={language} />
          </div>
        )}

        {/* VIEW 8: ABOUT */}
        {activeTab === 'about' && (
          <AboutView
            onStartJourney={() => setActiveTab('chat')}
            language={language}
          />
        )}

        {/* VIEW 9: CHAT / ADVISORY */}
        {activeTab === 'chat' && (
          <div className="max-w-[1280px] mx-auto p-4 sm:p-6 lg:p-8 space-y-5 animate-fadeIn">
            
            {/* Interaction Mode Switcher */}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-extrabold uppercase tracking-wider text-[#527068]">
                  Advisory Mode:
                </span>
                <div className="flex rounded-xl bg-white p-1 border border-[#d6e5da] shadow-2xs">
                  <button
                    onClick={() => setChatMode('voice')}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      chatMode === 'voice'
                        ? 'bg-[#0c594d] text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    🎙️ Voice Mode
                  </button>
                  <button
                    onClick={() => setChatMode('text')}
                    className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                      chatMode === 'text'
                        ? 'bg-[#0c594d] text-white shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    💬 Text Chat
                  </button>
                </div>
              </div>

              {recommendations.length > 0 && (
                <button
                  onClick={() => setActiveTab('recommendations')}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#0c594d] text-white font-extrabold text-xs shadow-md hover:bg-[#084239] transition cursor-pointer"
                >
                  <Sparkles size={15} />
                  <span>View Recommendations Screen ➜</span>
                </button>
              )}
            </div>

            {/* Chat View */}
            {chatMode === 'voice' ? (
              <VoiceChatMode
                messages={messages}
                onSendMessage={handleSendMessage}
                onSwitchToText={() => {
                  stopSpeaking();
                  setChatMode('text');
                }}
                language={language}
                onLanguageChange={handleLanguageChange}
                isLoading={isLoading}
              />
            ) : (
              <TextChatMode
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                suggestedReplies={suggestedReplies}
                onClearChat={handleReset}
                language={language}
                onLanguageChange={handleLanguageChange}
                onSwitchToVoice={() => {
                  stopSpeaking();
                  setChatMode('voice');
                }}
                journeyStep={journeyStep}
                onJourneyStepClick={handleJourneyStepClick}
                isProfileReady={isProfileReady || recommendations.length > 0}
                onOpenReport={handleOpenReport}
              />
            )}
          </div>
        )}

        {/* VIEW 10: CATALOGUE (Admin Only) */}
        {activeTab === 'catalogue' && (
          <div className="max-w-[1280px] mx-auto p-4 sm:p-8 space-y-6 animate-fadeIn">
            {userRole === 'admin' ? (
              <CatalogueModal
                isOpen={true}
                onClose={() => setActiveTab('home')}
                onSelectBusinessForAnalysis={(biz) => {
                  const updatedProfile = {
                    ...profile,
                    business_interest: biz.business_name
                  };
                  setProfile(updatedProfile);
                  runAnalysisPipeline(updatedProfile, biz.id);
                  setActiveTab('recommendations');
                }}
              />
            ) : (
              <div className="max-w-md mx-auto my-16 p-8 bg-white rounded-3xl border border-slate-200 shadow-xl text-center space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mx-auto">
                  <Lock size={28} />
                </div>
                <h3 className="text-xl font-bold text-slate-900">Admin Authentication Required</h3>
                <button
                  onClick={() => setIsAdminLoginOpen(true)}
                  className="w-full py-3 rounded-xl bg-[#0c594d] text-white font-bold text-sm shadow-md"
                >
                  Login as Administrator
                </button>
              </div>
            )}
          </div>
        )}

      </main>

      {/* ================= MODALS & DRAWERS ================= */}
      {/* 90-Day DPR Bank Report Modal */}
      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        report={generatedReportData}
        reportData={generatedReportData}
        profile={profile}
        selectedBusiness={activeBusiness}
        feasibility={feasibility}
        financialPlan={financialPlan}
        schemes={schemes}
        language={language}
        onStartChat={() => {
          setIsReportOpen(false);
          setActiveTab('chat');
        }}
      />

      {/* Admin Login Modal */}
      <AdminLoginModal
        isOpen={isAdminLoginOpen}
        onClose={() => setIsAdminLoginOpen(false)}
        onLoginSuccess={handleAdminLoginSuccess}
      />

      {/* User Profile Drawer */}
      {isProfileDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-2xs transition-opacity"
            onClick={() => setIsProfileDrawerOpen(false)}
          />
          <div className="relative w-full max-w-md bg-white h-full z-10 shadow-2xl overflow-y-auto p-6 flex flex-col justify-between">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-full bg-[#0c594d] text-white font-bold flex items-center justify-center text-sm">
                    {profile.name ? profile.name.charAt(0).toUpperCase() : 'R'}
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-[#072a24]">
                      {profile.name || 'Entrepreneur Profile'}
                    </h3>
                    <p className="text-xs text-[#527068]">
                      {profile.district || profile.location || 'Pune'}, {profile.state || 'Maharashtra'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsProfileDrawerOpen(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition"
                >
                  <X size={18} />
                </button>
              </div>

              <ProfileCard
                profile={profile}
                onUpdateProfile={(updated) => {
                  setProfile(updated);
                  if (isProfileReady) {
                    runAnalysisPipeline(updated);
                  }
                }}
                isDrawer={true}
                journeyStep={journeyStep}
                onJourneyStepClick={handleJourneyStepClick}
                language={language}
              />
            </div>

            <div className="pt-6 border-t border-slate-100">
              <button
                onClick={() => {
                  setIsProfileDrawerOpen(false);
                  setActiveTab('chat');
                }}
                className="w-full py-3 rounded-2xl bg-[#0c594d] hover:bg-[#084239] text-white font-bold text-xs shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <MessageCircle size={15} />
                <span>Edit via Advisory Chat</span>
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
