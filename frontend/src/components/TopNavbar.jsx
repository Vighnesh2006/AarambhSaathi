import React, { useState } from 'react';
import {
  Home,
  User,
  Sparkles,
  ShieldCheck,
  Wrench,
  Landmark,
  Building2,
  FileText,
  MessageCircle,
  Mic,
  ChevronDown,
  Menu,
  X,
  LogOut,
  Sparkle
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function TopNavbar({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  onReset,
  onOpenReport,
  onOpenProfileDrawer,
  onOpenVoiceChat,
  userRole = 'user',
  profile = {},
  hasRecommendations = false,
  onOpenAdminLogin,
  onAdminLogout
}) {
  const [isLangOpen, setIsLangOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const t = getTranslation(language);

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिन्दी' },
    { code: 'mr', label: 'मराठी' }
  ];

  const currentLangObj = languages.find((l) => l.code === language) || languages[0];
  const userInitial = profile.name ? profile.name.charAt(0).toUpperCase() : 'R';

  const navItems = [
    { id: 'home', label: language === 'mr' ? 'मुख्यपृष्ठ' : language === 'hi' ? 'होम' : 'Home', icon: Home },
    { id: 'profile', label: language === 'mr' ? 'प्रोफाइल' : language === 'hi' ? 'प्रोफाइल' : 'Profile', icon: User },
    { id: 'chat', label: language === 'mr' ? 'संवाद' : language === 'hi' ? 'चैट' : 'Chat', icon: MessageCircle }
  ];

  return (
    <header className="bg-white border-b border-[#e3ece5] sticky top-0 z-40 shadow-xs select-none">
      <div className="max-w-[1700px] mx-auto px-4 sm:px-6">
        <div className="h-16 flex items-center justify-between gap-3">
          
          {/* 1. Left Logo & Branding */}
          <div 
            onClick={() => setActiveTab('home')}
            className="flex items-center gap-3 cursor-pointer shrink-0 hover:opacity-95 transition"
          >
            <img src="/logo.png" alt="Aarambh Saathi" className="w-10 h-10 rounded-xl object-cover shadow-md shadow-emerald-900/10" />
            <div className="hidden sm:block">
              <h1 className="text-base font-black text-[#072a24] font-display tracking-tight leading-none">
                Aarambh Saathi
              </h1>
              <p className="text-[11px] font-medium text-[#527068] mt-0.5 leading-none">
                Gaav ka Vikas, Aapke Saath
              </p>
            </div>
          </div>

          {/* 2. Center: All Navigation Links in Header (Horizontal Row) */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-1.5 overflow-x-auto no-scrollbar py-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    if (item.id === 'business_plan') {
                      onOpenReport();
                    } else {
                      setActiveTab(item.id);
                    }
                  }}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'bg-[#e2f0e6] text-[#075247] font-black shadow-2xs'
                      : 'text-[#47635b] hover:bg-[#f3f7f4] hover:text-[#072a24]'
                  }`}
                >
                  <Icon
                    size={15}
                    className={isActive ? 'text-[#075247]' : 'text-[#688a80]'}
                  />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="px-1.5 py-0.2 rounded-full text-[9px] font-black bg-emerald-600 text-white uppercase">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* 3. Right Controls: Voice button, Language dropdown, User Avatar */}
          <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
            
            {/* Voice Assistant Pill Button */}
            <button
              onClick={onOpenVoiceChat}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#0c594d] to-[#15803d] text-white text-xs font-bold shadow-xs hover:brightness-105 transition cursor-pointer"
              title="Voice Assistant"
            >
              <Mic size={14} className="animate-pulse" />
              <span className="hidden md:inline">Voice Assistant</span>
            </button>

            {/* Language Selector Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsLangOpen(!isLangOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#d2e4d7] bg-white hover:bg-[#f2faf4] text-xs font-bold text-[#072a24] transition shadow-2xs cursor-pointer"
              >
                <span>{currentLangObj.label}</span>
                <ChevronDown size={14} className="text-[#527068]" />
              </button>

              {isLangOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setIsLangOpen(false)}
                  />
                  <div className="absolute right-0 mt-1.5 w-32 bg-white rounded-2xl shadow-xl border border-[#d2e4d7] py-1.5 z-50 animate-fadeIn">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setIsLangOpen(false);
                        }}
                        className={`w-full text-left px-3.5 py-2 text-xs font-bold transition-colors cursor-pointer ${
                          language === lang.code
                            ? 'bg-[#edf7f0] text-[#0c594d] font-black'
                            : 'text-[#47635b] hover:bg-[#f7faf8]'
                        }`}
                      >
                        {lang.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* Admin Role indicator / Logout */}
            {userRole === 'admin' ? (
              <div className="flex items-center gap-1.5">
                <span className="bg-amber-400 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded-full uppercase">
                  Admin
                </span>
                <button
                  onClick={onAdminLogout}
                  className="p-1.5 text-rose-600 hover:bg-rose-50 rounded-lg transition"
                  title="Admin Logout"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : null}

            {/* User Profile Avatar */}
            <button
              onClick={onOpenProfileDrawer}
              className="w-9 h-9 rounded-full bg-[#0c594d] hover:bg-[#084239] text-white font-black text-sm flex items-center justify-center shadow-md cursor-pointer transition-transform hover:scale-105"
              title={profile.name || 'User Profile'}
            >
              {userInitial}
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 rounded-xl text-[#47635b] hover:bg-[#f2faf4] transition cursor-pointer"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>

          </div>
        </div>

        {/* Mobile Horizontal Sub-Navbar */}
        <div className="lg:hidden border-t border-[#edf3ee] py-2 flex items-center gap-1 overflow-x-auto no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.id === 'business_plan') {
                    onOpenReport();
                  } else {
                    setActiveTab(item.id);
                  }
                }}
                className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap shrink-0 transition ${
                  isActive
                    ? 'bg-[#e2f0e6] text-[#075247] font-black'
                    : 'text-[#47635b] hover:bg-[#f3f7f4]'
                }`}
              >
                <Icon size={14} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
