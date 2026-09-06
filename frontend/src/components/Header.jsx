import React, { useState } from 'react';
import {
  Home,
  BookOpen,
  Package,
  Info,
  MessageCircle,
  Globe,
  Users,
  ChevronDown,
  Sprout,
  Menu,
  X,
  RotateCcw,
  FileText,
  Lock,
  LogOut,
  ShieldCheck
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function Header({
  activeTab,
  setActiveTab,
  language,
  setLanguage,
  onReset,
  onOpenReport,
  onOpenProfileDrawer,
  totalBusinesses = 90,
  userRole = 'user', // 'user' | 'admin'
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

  // Role-Based Navigation Items:
  // Customers/Users only have access to: Home, About, Chat
  // Admin has access to: Home, About, Chat, Catalogue, Schemes
  const navItems = userRole === 'admin'
    ? [
        { id: 'home', label: t.navHome, icon: Home },
        { id: 'catalogue', label: t.navCatalogue, icon: BookOpen, badge: 'Admin' },
        { id: 'schemes', label: t.navSchemes, icon: Package, badge: 'Admin' },
        { id: 'about', label: t.navAbout, icon: Info },
        { id: 'chat', label: t.navChat, icon: MessageCircle },
      ]
    : [
        { id: 'home', label: t.navHome, icon: Home },
        { id: 'about', label: t.navAbout, icon: Info },
        { id: 'chat', label: t.navChat, icon: MessageCircle },
      ];

  const handleNavClick = (tabId) => {
    setActiveTab(tabId);
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-[#063f39] text-white shadow-lg border-b border-[#0f5349]">
      <div className="mx-auto flex h-16 sm:h-[78px] max-w-[1500px] items-center justify-between px-3 sm:px-8">
        
        {/* ================= LOGO & BRANDING ================= */}
        <div
          onClick={() => handleNavClick('home')}
          className="flex items-center gap-2.5 sm:gap-3.5 cursor-pointer select-none group shrink-0"
        >
          <div className="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-xl sm:rounded-2xl bg-[#f7c928] shadow-md group-hover:scale-105 transition-transform shrink-0">
            <Sprout className="h-6 w-6 sm:h-8 sm:w-8 text-[#075044]" />
          </div>

          <div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <h1 className="text-xl sm:text-[26px] font-extrabold leading-none tracking-tight font-display">
                {language === 'en' ? (
                  <>Aarambh <span className="text-[#b9db4a]">Saathi</span></>
                ) : (
                  <span className="text-white">{t.appName}</span>
                )}
              </h1>
              {userRole === 'admin' && (
                <span className="text-[9px] sm:text-[10px] bg-amber-400 text-slate-950 font-black px-1.5 py-0.5 rounded-md uppercase tracking-wider">
                  Admin
                </span>
              )}
            </div>
            <p className="mt-0.5 text-xs sm:text-[14px] text-emerald-100 font-normal hidden sm:block">
              {t.tagline}
            </p>
          </div>
        </div>

        {/* ================= DESKTOP NAVIGATION TABS ================= */}
        <nav className="hidden lg:flex items-center gap-8">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`flex items-center gap-2 py-1.5 text-sm font-bold transition-all relative ${
                  isActive
                    ? 'text-white border-b-2 border-[#f7c928] pb-1'
                    : 'text-emerald-100/80 hover:text-[#b9db4a]'
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="text-[9px] bg-emerald-500/30 text-emerald-200 px-1.5 py-0.2 rounded border border-emerald-400/40">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* ================= RIGHT CONTROLS ================= */}
        <div className="hidden lg:flex items-center gap-3.5">
          
          {/* Language Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsLangOpen(!isLangOpen)}
              className="flex items-center gap-2 rounded-full border border-[#27776d] px-3.5 py-2 text-xs sm:text-sm font-semibold text-emerald-100 hover:text-white hover:border-[#b9db4a] transition bg-[#094d45]/60"
            >
              <Globe size={16} />
              <span>{currentLangObj.label}</span>
              <ChevronDown size={14} className={`transition-transform ${isLangOpen ? 'rotate-180' : ''}`} />
            </button>

            {isLangOpen && (
              <div className="absolute right-0 mt-2 w-36 rounded-2xl bg-white p-1.5 shadow-xl border border-slate-200 z-50 text-slate-800 animate-in fade-in zoom-in-95 duration-150">
                {languages.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => {
                      setLanguage(l.code);
                      setIsLangOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold transition ${
                      language === l.code
                        ? 'bg-emerald-100 text-[#075247]'
                        : 'hover:bg-slate-100 text-slate-700'
                    }`}
                  >
                    <span>{l.label}</span>
                    {language === l.code && <span className="text-emerald-700">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* User Profile Avatar Drawer Trigger */}
          <button
            onClick={onOpenProfileDrawer}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-[#08745e] shadow-md hover:bg-emerald-100 transition"
            title={t.userProfile}
          >
            <Users size={18} />
          </button>

          {/* Admin Login / Logout Button */}
          {userRole === 'admin' ? (
            <button
              onClick={onAdminLogout}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-bold transition shadow-xs border border-rose-400/40"
              title="Logout from Admin Account"
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          ) : (
            <button
              onClick={onOpenAdminLogin}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-full border border-amber-300/40 bg-amber-400/10 hover:bg-amber-400/20 text-amber-200 text-xs font-bold transition"
              title="Admin Login Portal"
            >
              <Lock size={14} className="text-amber-300" />
              <span>Admin Login</span>
            </button>
          )}

          {/* Gaav ka Vikas Badge / Plan Trigger */}
          <button
            onClick={onOpenReport}
            className="rounded-full bg-[#d4ef83] px-4 py-2.5 text-xs sm:text-sm font-extrabold italic text-[#143b36] hover:bg-[#c7e96b] shadow-md transition flex items-center gap-1.5"
            title="Open Complete Business Plan"
          >
            <Sprout size={16} className="text-[#075044]" />
            <span>{t.navPlanBadge}</span>
          </button>
        </div>

        {/* ================= MOBILE HAMBURGER BUTTON ================= */}
        <div className="lg:hidden flex items-center gap-1.5 sm:gap-2">
          {userRole !== 'admin' ? (
            <button
              onClick={onOpenAdminLogin}
              className="p-1.5 sm:p-2 rounded-xl bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-bold"
            >
              <Lock size={15} />
            </button>
          ) : (
            <button
              onClick={onAdminLogout}
              className="p-1.5 sm:p-2 rounded-xl bg-rose-600 text-white text-xs font-bold"
            >
              <LogOut size={15} />
            </button>
          )}

          <button
            onClick={onOpenProfileDrawer}
            className="p-1.5 sm:p-2 rounded-xl bg-white text-[#08745e]"
          >
            <Users size={16} />
          </button>

          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-1.5 sm:p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white"
          >
            {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

      </div>

      {/* ================= MOBILE DRAWER MENU ================= */}
      {isMobileMenuOpen && (
        <div className="lg:hidden bg-[#063f39] border-t border-[#12584e] px-4 py-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center gap-2 p-2.5 rounded-xl text-xs font-bold transition ${
                    isActive ? 'bg-[#f7c928] text-[#075044]' : 'bg-[#094d45] text-white hover:bg-[#0c5d53]'
                  }`}
                >
                  <Icon size={16} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-[#12584e]">
            <div className="flex gap-1.5">
              {languages.map((l) => (
                <button
                  key={l.code}
                  onClick={() => setLanguage(l.code)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                    language === l.code ? 'bg-[#b9db4a] text-[#063f39]' : 'bg-white/10 text-white'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>

            <button
              onClick={onOpenReport}
              className="px-3 py-1.5 rounded-xl bg-[#d4ef83] text-[#143b36] font-extrabold text-xs"
            >
              Business Plan 📄
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
