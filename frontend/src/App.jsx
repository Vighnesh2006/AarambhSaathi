import React, { useState, useEffect } from 'react';
import { speakText, stopSpeaking } from './services/voice';
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

  const [isDemoMode, setIsDemoMode] = useState(false);

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
    setIsDemoMode(false);
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
        setJourneyStep(3);
      }
    } catch (err) {
      console.error('Error in advisory pipeline:', err);
    } finally {
      setPipelineLoading(false);
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
      
      // Only speak aloud if user is in voice mode
      if (chatMode === 'voice') {
        speakText(res.reply, language);
      }

      if (res.updated_profile) {
        setProfile(res.updated_profile);
        if (res.is_profile_ready && (!recommendations || recommendations.length === 0)) {
          await runAnalysisPipeline(res.updated_profile);
        }
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

  // Switch selected business (Preserves profile, resets downstream dependent intelligence)
  const handleSelectBusiness = async (bizId) => {
    if (bizId === selectedBusinessId && feasibility) return;
    
    setSelectedBusinessId(bizId);
    // Reset downstream dependent results to avoid stale DPR / calculations
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
      const selectedRec = recommendations?.find((r) => r.business_id === targetBusinessId) || recommendations?.[0];
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
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

  // 1-Click Sample Profile Handler for Rapid Verification & Testing (Demo Mode)
  const handleSelectSampleProfile = async (sampleType) => {
    let sampleProfile;
    let introMsg;

    if (sampleType === 'dairy') {
      sampleProfile = {
        name: 'Ramesh Patil',
        intent: 'Start a new business',
        age: 28,
        gender: 'Male',
        village: 'Shirol',
        district: 'Kolhapur',
        state: 'Maharashtra',
        location: 'Shirol, Kolhapur, Maharashtra',
        education: '12th Pass',
        occupation: 'Farming',
        skills: ['Dairy farming', 'Cattle care', 'Animal husbandry'],
        experience: '4 years of animal handling & milk production',
        resources: ['Agricultural land', 'Water source', 'Cattle shed space'],
        available_investment: 100000,
        capital: 100000,
        business_interest: 'Dairy Farming',
        existing_business: null,
        goal: 'Start sustainable modern dairy farm with cold chain access',
        scale: 'starter',
        constraints: [],
        language
      };
      introMsg = language === 'mr'
        ? 'मी **रमेश पाटील** (कोल्हापूर, ₹१ लाख भांडवल, दुग्धव्यवसाय कौशल्य) यांचे डेमो प्रोफाइल लोड केले आहे. खालील ९-घटक जुळणी विश्लेषण तपासा!'
        : language === 'hi'
        ? 'मैंने **रमेश पाटिल** (कोल्हापुर, ₹1 लाख पूंजी, डेयरी कौशल) की डेमो प्रोफ़ाइल लोड कर दी है। नीचे 9-कारक मैच विश्लेषण देखें!'
        : 'Loaded demo profile for **Ramesh Patil** (Kolhapur, ₹1,00,000 capital, Dairy skills, Land + Water). Deterministic multi-factor recommendations computed below!';
    } else if (sampleType === 'retail') {
      sampleProfile = {
        name: 'Rahul Verma',
        intent: 'Start a new business',
        age: 22,
        gender: 'Male',
        village: 'Khed Town',
        district: 'Pune',
        state: 'Maharashtra',
        location: 'Khed Town, Pune, Maharashtra',
        education: 'Graduate (B.Com)',
        occupation: 'Store Assistant',
        skills: ['Retail sales', 'Customer management', 'Accounting & Billing'],
        experience: '2 years retail shop counter experience',
        resources: ['Commercial shop space', 'Electricity connection', 'Main road access'],
        available_investment: 200000,
        capital: 200000,
        business_interest: 'Commercial Retail / FMCG Store',
        existing_business: null,
        goal: 'Start profitable retail business with existing shop',
        scale: 'micro',
        constraints: [],
        language
      };
      introMsg = language === 'mr'
        ? 'मी **राहुल वर्मा** (पुणे, ₹२ लाख भांडवल, दुकान जागा व किरकोळ विक्री कौशल्य) यांचे डेमो प्रोफाइल लोड केले आहे. खालील ९-घटक विश्लेषण तपासा!'
        : language === 'hi'
        ? 'मैंने **राहुल वर्मा** (पुणे, ₹2 लाख पूंजी, दुकान व रिटेल कौशल) की डेमो प्रोफ़ाइल लोड कर दी है। नीचे 9-कारक मैच देखें!'
        : 'Loaded demo profile for **Rahul Verma** (Pune, ₹2,00,000 capital, Commercial Shop space, Retail sales skills). Top matches computed below!';
    } else {
      sampleProfile = {
        name: 'Sunita Kulkarni',
        intent: 'Start a new business',
        age: 35,
        gender: 'Female',
        village: 'Miraj',
        district: 'Sangli',
        state: 'Maharashtra',
        location: 'Miraj, Sangli, Maharashtra',
        education: '10th Pass',
        occupation: 'Home maker / SHG member',
        skills: ['Food processing', 'Pickle making', 'Spice grinding', 'Packaging'],
        experience: 'SHG group food packaging experience',
        resources: ['Processing shed', '3-phase electricity', 'Continuous water supply'],
        available_investment: 500000,
        capital: 500000,
        business_interest: 'Food Processing Unit',
        existing_business: null,
        goal: 'Set up automated food processing micro unit',
        scale: 'small',
        constraints: [],
        language
      };
      introMsg = language === 'mr'
        ? 'मी **सुनिता कुलकर्णी** (सांगली, ₹५ लाख भांडवल, अन्न प्रक्रिया कौशल्य) यांचे डेमो प्रोफाइल लोड केले आहे. खालील विश्लेषण तपासा!'
        : language === 'hi'
        ? 'मैंने **सुनीता कुलकर्णी** (सांगली, ₹5 लाख पूंजी, खाद्य प्रसंस्करण कौशल) की डेमो प्रोफ़ाइल लोड कर दी है। नीचे 9-कारक मैच देखें!'
        : 'Loaded demo profile for **Sunita Kulkarni** (Sangli, ₹5,00,000 capital, Food Processing skills, 3-Phase power). Top matches computed below!';
    }

    setIsDemoMode(true);
    setProfile(sampleProfile);
    setIsProfileReady(true);
    setActiveTab('chat');
    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: introMsg,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);

    await runAnalysisPipeline(sampleProfile);
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
            onSelectSampleProfile={handleSelectSampleProfile}
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
            
            {/* Demo Mode Notice Banner */}
            {isDemoMode && (
              <div className="mb-5 p-3.5 rounded-2xl bg-gradient-to-r from-amber-50 to-emerald-50 border border-amber-300 text-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs shadow-xs">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-400 text-slate-950 text-[10px] font-black uppercase tracking-wider">
                    Demo Mode
                  </span>
                  <span>
                    Simulating Journey with Sample Persona: <strong>{profile.name}</strong> ({profile.district || 'Rural'}, {profile.state} • ₹{Number(profile.capital || 100000).toLocaleString('en-IN')})
                  </span>
                </div>
                <button
                  onClick={handleReset}
                  className="px-3 py-1 rounded-xl bg-white border border-amber-300 hover:bg-amber-100 text-slate-800 font-bold transition text-xs shadow-2xs"
                >
                  Start New Real Journey
                </button>
              </div>
            )}

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
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleOpenReport}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-[#15803d] text-slate-950 font-extrabold text-xs shadow-md animate-soft-pulse hover:brightness-105 transition"
                  >
                    <FileText size={15} />
                    <span>{t.journeyGenReportBtn} Ready</span>
                  </button>
                </div>
              )}
            </div>

            {/* Voice Mode */}
            {chatMode === 'voice' && (
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
                onLanguageChange={handleLanguageChange}
                onSwitchToVoice={() => {
                  stopSpeaking();
                  setChatMode('voice');
                }}
                journeyStep={journeyStep}
                onJourneyStepClick={handleJourneyStepClick}
                isProfileReady={isProfileReady || recommendations.length > 0}
                onOpenReport={handleOpenReport}
                onSelectSampleProfile={handleSelectSampleProfile}
              />
            )}

            {/* Live Intelligence Cards Container */}
            {recommendations.length > 0 && (
              <div id="decision-support-container" className="mt-8 space-y-6 pt-6 border-t border-slate-200 scroll-mt-10">
                <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-[#d6e5da] shadow-xs">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-base sm:text-lg font-black text-[#072a24] font-display">
                        {t.journeyTitle} — Decision Support
                      </h3>
                      <p className="text-xs text-[#527068]">
                        Selected Opportunity: <strong>{activeBusiness?.business_name}</strong>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        const el = document.getElementById('opportunities-section');
                        if (el) el.scrollIntoView({ behavior: 'smooth' });
                      }}
                      className="px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-[#075247] border border-emerald-200 font-bold text-xs transition"
                    >
                      🔄 Change Business
                    </button>
                    <button
                      onClick={handleReset}
                      className="px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200 font-semibold text-xs transition"
                    >
                      Start New Journey
                    </button>
                  </div>
                </div>

                {pipelineLoading && (
                  <div className="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 flex items-center gap-3 text-xs text-[#075247] animate-pulse">
                    <div className="w-4 h-4 border-2 border-[#075247] border-t-transparent rounded-full animate-spin"></div>
                    <span>Evaluating local feasibility, setup requirements & financial structuring for {activeBusiness?.business_name}...</span>
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

                  {/* Top 3 Recommendations */}
                  <div className="lg:col-span-6 scroll-mt-20" id="opportunities-section">
                    <RecommendationCard
                      recommendations={recommendations}
                      selectedBusinessId={selectedBusinessId}
                      onSelectBusiness={handleSelectBusiness}
                      language={language}
                    />
                  </div>

                  {/* Business Setup & Machinery Planner */}
                  <div className="lg:col-span-6 scroll-mt-20" id="machinery-section">
                    {activeBusiness && (
                      <BusinessSetupCard
                        businessId={activeBusiness.id || activeBusiness.business_id}
                        businessName={activeBusiness.business_name}
                        businessScale={profile.scale || 'small'}
                        userLocation={`${profile.district || profile.location || ''} ${profile.state || ''}`.trim()}
                        userBudget={profile.capital || profile.available_investment || undefined}
                        userProfile={profile}
                        feasibilityResult={feasibility}
                        language={language}
                      />
                    )}
                  </div>

                  {/* Feasibility */}
                  {feasibility && (
                    <div className="lg:col-span-6 scroll-mt-20" id="feasibility-section">
                      <FeasibilityCard
                        feasibility={feasibility}
                        selectedBusinessName={activeBusiness?.business_name}
                        language={language}
                      />
                    </div>
                  )}

                  {/* Financial Structuring */}
                  <div className="lg:col-span-6 scroll-mt-20" id="finance-section">
                    <FinancialSummary
                      initialCost={activeBusiness?.required_investment || 140000}
                      userCapital={profile.capital || profile.available_investment || 15000}
                      businessId={activeBusiness?.id || activeBusiness?.business_id}
                      businessName={activeBusiness?.business_name}
                      userProfile={profile}
                      onPlanUpdated={setFinancialPlan}
                      language={language}
                    />
                  </div>

                  {/* Matched Schemes */}
                  <div className="lg:col-span-12 scroll-mt-20" id="schemes-section">
                    <SchemesCard schemes={schemes} language={language} />
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
                  <SchemesCard schemes={schemes} language={language} />
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
              language={language}
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
        language={language}
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
