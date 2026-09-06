import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  Mic,
  Trash2,
  ArrowRight,
  Bot,
  User,
  CheckCircle2,
  TrendingUp,
  Landmark,
  FileText,
  Sprout,
  HelpCircle,
  Clock,
  RotateCcw,
  SlidersHorizontal
} from 'lucide-react';
import { getTranslation } from '../services/translations';
import robotAvatarImg from '../assets/robot_avatar_1788638099080.jpg';
import landscapeImg from '../assets/rural_sprout_landscape_1788638113042.jpg';

export default function TextChatMode({
  messages,
  onSendMessage,
  isLoading,
  suggestedReplies,
  onClearChat,
  language = 'en',
  onSwitchToVoice,
  journeyStep = 1,
  onJourneyStepClick,
  isProfileReady,
  onOpenReport
}) {
  const t = getTranslation(language);
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickOptionClick = (text) => {
    if (isLoading) return;
    onSendMessage(text);
  };

  // Starter Occupation Tiles shown when conversation starts
  const starterOptions = [
    {
      label: t.optFarming,
      emoji: '👨‍🌾',
      query: language === 'mr' ? 'मी शेती आणि शेतीपूरक कामे करतो.' : language === 'hi' ? 'मैं खेती और कृषि कार्य करता हूँ।' : 'I do farming and agricultural work.'
    },
    {
      label: t.optAnimals,
      emoji: '🐄',
      query: language === 'mr' ? 'माझ्याकडे गायी/म्हशी व पशुपालनाचा अनुभव आहे.' : language === 'hi' ? 'मुझे डेयरी पशुओं और पशुपालन का अनुभव है।' : 'I have experience working with dairy animals and livestock.'
    },
    {
      label: t.optShop,
      emoji: '🏪',
      query: language === 'mr' ? 'माझे गावात किराणा/छोटे दुकान आहे.' : language === 'hi' ? 'मेरी गाँव में किराने/खुदरा की छोटी दुकान है।' : 'I run a small rural grocery shop/retail counter.'
    },
    {
      label: t.optSkilled,
      emoji: '🔨',
      query: language === 'mr' ? 'मी सुतारकाम/वेल्डिंग/टेलरिंग सारखे कुशल काम करतो.' : language === 'hi' ? 'मैं सिलाई/कारीगरी/वेल्डिंग जैसा हुनरमंद काम करता हूँ।' : 'I do skilled vocational work like mechanics/carpentry/tailoring.'
    },
    {
      label: t.optLabour,
      emoji: '🧱',
      query: language === 'mr' ? 'मी रोजंदारी मजुरी करतो, मला स्वतःचा उद्योग सुरू करायचा आहे.' : language === 'hi' ? 'मैं मजदूरी करता हूँ और खुद का छोटा उद्यम शुरू करना चाहता हूँ।' : 'I work as daily agricultural/construction labourer and want my own enterprise.'
    },
    {
      label: t.optNotSure,
      emoji: '❓',
      query: language === 'mr' ? 'मला सुरुवातीपासून योग्य व्यवसाय मार्गदर्शन हवे आहे.' : language === 'hi' ? 'मुझे शुरुआत से सही व्यवसाय चुनने में मदद चाहिए।' : 'I am not sure which business is best for my location. Please guide me from scratch.'
    },
  ];

  const journeySteps = [
    {
      step: 1,
      id: 'understand',
      label: t.journey1,
      sub: isProfileReady ? t.completed : t.inProgress,
      isDone: isProfileReady
    },
    {
      step: 2,
      id: 'opportunities',
      label: t.journey2,
      sub: isProfileReady ? 'Top 3 Matches Ready' : t.journey2Sub,
      isDone: isProfileReady
    },
    {
      step: 3,
      id: 'finance',
      label: t.journey3,
      sub: isProfileReady ? 'Loan & EMI Structured' : t.journey3Sub,
      isDone: isProfileReady
    },
    {
      step: 4,
      id: 'schemes',
      label: t.journey4,
      sub: isProfileReady ? 'Verified Schemes Synced' : t.journey4Sub,
      isDone: isProfileReady
    },
    {
      step: 5,
      id: 'report',
      label: t.journey5,
      sub: isProfileReady ? '90-Day DPR Ready' : t.journey5Sub,
      isDone: isProfileReady && journeyStep === 5
    },
  ];

  return (
    <div className="w-full max-w-[1500px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* ================= LEFT / MAIN CHAT CONTAINER (8 Cols) ================= */}
      <div className="lg:col-span-8 flex flex-col h-[calc(100vh-140px)] min-h-[580px] bg-white rounded-3xl border border-[#d6e5da] shadow-card overflow-hidden">
        
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-[#075247] to-[#15803d] px-5 py-3.5 text-white flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-white/10 p-0.5 border border-amber-300/60 overflow-hidden shadow-inner">
                <img
                  src={robotAvatarImg}
                  alt="Aarambh Saathi Mascot"
                  className="w-full h-full object-cover rounded-full"
                />
              </div>
              <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-400 ring-2 ring-[#075247]" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold font-display leading-tight">
                  {t.appName}
                </h3>
                <span className="text-[10px] bg-amber-400 text-slate-950 font-black px-2 py-0.5 rounded-full shadow-2xs">
                  {t.chatAiAdvisorBadge}
                </span>
              </div>
              <p className="text-xs text-emerald-100">
                {t.chatSubtitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onSwitchToVoice}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/15 hover:bg-white/25 text-xs font-bold text-white border border-white/20 transition shadow-2xs"
              title={t.chatSwitchToVoice}
            >
              <Mic size={14} className="text-amber-300" />
              <span className="hidden sm:inline">{t.chatSwitchToVoice}</span>
            </button>

            <button
              onClick={onClearChat}
              className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-emerald-100 hover:text-white transition"
              title={t.chatResetBtn}
            >
              <Trash2 size={15} />
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-[#f9fbf9]">
          {messages.map((msg, index) => {
            const isBot = msg.role === 'assistant';
            return (
              <div
                key={index}
                className={`flex gap-3 ${isBot ? 'justify-start' : 'justify-end'}`}
              >
                {/* Bot Avatar */}
                {isBot && (
                  <div className="w-9 h-9 rounded-full shrink-0 overflow-hidden bg-emerald-700 border-2 border-white shadow-md">
                    <img
                      src={robotAvatarImg}
                      alt="Aarambh Saathi"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <div className="max-w-[85%] sm:max-w-[78%] space-y-2">
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs ${
                      isBot
                        ? 'bg-white text-[#072a24] border border-[#e1ece4] rounded-tl-sm'
                        : 'bg-[#075247] text-white font-medium rounded-tr-sm shadow-md'
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.content}</p>
                    <span
                      className={`block text-[10px] mt-1.5 text-right font-medium ${
                        isBot ? 'text-slate-400' : 'text-emerald-200'
                      }`}
                    >
                      {msg.timestamp || 'Just now'}
                    </span>
                  </div>

                  {/* Starter Occupation Tile Grid in First Message */}
                  {isBot && index === 0 && messages.length <= 2 && (
                    <div className="pt-2 space-y-2">
                      <p className="text-xs font-bold text-[#0d3f35]">
                        {t.chatStarterTitle}
                      </p>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {starterOptions.map((opt, oIdx) => (
                          <button
                            key={oIdx}
                            onClick={() => handleQuickOptionClick(opt.query)}
                            disabled={isLoading}
                            className="flex flex-col items-center justify-center p-3 rounded-xl bg-white border border-[#dce8e0] hover:border-emerald-400 hover:bg-emerald-50/50 hover:shadow-md transition text-center group"
                          >
                            <span className="text-2xl mb-1 group-hover:scale-110 transition-transform">
                              {opt.emoji}
                            </span>
                            <span className="text-xs font-bold text-[#072a24] leading-tight">
                              {opt.label}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* User Avatar */}
                {!isBot && (
                  <div className="w-9 h-9 rounded-full shrink-0 bg-[#063f39] text-amber-300 font-bold flex items-center justify-center border-2 border-white shadow-md text-xs">
                    <User size={18} />
                  </div>
                )}
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex gap-3 justify-start items-center">
              <div className="w-8 h-8 rounded-full bg-emerald-700 flex items-center justify-center text-white text-xs">
                <Bot size={16} />
              </div>
              <div className="bg-white border border-emerald-100 rounded-2xl px-4 py-3 shadow-xs flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce [animation-delay:0.4s]" />
                <span className="text-xs text-[#527068] font-semibold ml-2">{t.chatThinking}</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Suggested Quick Replies */}
        {suggestedReplies && suggestedReplies.length > 0 && (
          <div className="px-4 py-2 bg-white border-t border-[#e8efe9] flex items-center gap-2 overflow-x-auto">
            <span className="text-[11px] font-bold text-[#527068] shrink-0">{t.chatSuggestions}</span>
            {suggestedReplies.map((reply, rIdx) => (
              <button
                key={rIdx}
                onClick={() => handleQuickOptionClick(reply)}
                className="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-bold bg-emerald-50 hover:bg-emerald-100 text-[#075247] border border-emerald-200 transition"
              >
                {reply}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <div className="p-3 sm:p-4 bg-white border-t border-[#dce8e0]">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t.chatPlaceholder}
                className="w-full px-4 py-3 rounded-2xl bg-[#f4f8f5] border border-[#d6e5da] text-sm text-[#072a24] focus:outline-hidden focus:ring-2 focus:ring-[#075247] focus:bg-white placeholder-slate-400 font-medium transition"
              />
            </div>

            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={`p-3.5 rounded-2xl flex items-center justify-center transition-all ${
                input.trim() && !isLoading
                  ? 'bg-[#075247] hover:bg-[#063f39] text-white shadow-md active:scale-95'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Send size={18} />
            </button>
          </form>

          {/* 3 Starter Fast Actions */}
          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            <button
              onClick={() => onJourneyStepClick(2)}
              className="px-3 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 cursor-pointer shadow-2xs"
            >
              <span>🌾</span>
              <span>{t.actFindBiz}</span>
            </button>
            <button
              onClick={() => onJourneyStepClick(3)}
              className="px-3 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 cursor-pointer shadow-2xs"
            >
              <span>💰</span>
              <span>{t.actCalcFinance}</span>
            </button>
            <button
              onClick={() => onJourneyStepClick(4)}
              className="px-3 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 cursor-pointer shadow-2xs"
            >
              <span>🏛️</span>
              <span>{t.actCheckSchemes}</span>
            </button>
          </div>
        </div>

      </div>

      {/* ================= RIGHT / YOUR JOURNEY PANEL (4 Cols) ================= */}
      <div className="lg:col-span-4 space-y-5">
        
        {/* Journey Progress Card */}
        <div className="bg-white rounded-3xl border border-[#d6e5da] p-5 sm:p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-100 text-[#075247] flex items-center justify-center font-bold">
                <Sprout size={16} />
              </div>
              <h4 className="font-extrabold text-base text-[#072a24] font-display">
                {t.journeyTitle}
              </h4>
            </div>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
              {t.journeyStepsCount}
            </span>
          </div>

          <div className="space-y-3">
            {journeySteps.map((item, idx) => {
              const Icon = item.icon;
              const isCurrent = journeyStep === item.step;
              const isPassed = item.isDone || journeyStep > item.step || (item.step === 1 && isProfileReady);
              const isUnlocked = isProfileReady || journeyStep >= item.step;

              return (
                <button
                  key={idx}
                  onClick={() => onJourneyStepClick(item.step)}
                  className={`w-full flex items-center justify-between p-3 rounded-2xl border text-left transition-all cursor-pointer ${
                    isCurrent
                      ? 'bg-emerald-50 border-emerald-500 shadow-sm ring-2 ring-emerald-300'
                      : isPassed
                      ? 'bg-[#f4f9f5] border-[#d0e5d5] hover:bg-emerald-50/80 hover:border-emerald-300'
                      : isUnlocked
                      ? 'bg-white border-[#dce8e0] hover:bg-emerald-50/40 hover:border-emerald-300'
                      : 'bg-white border-slate-100 opacity-80 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center font-black text-xs transition-colors ${
                        isPassed
                          ? 'bg-emerald-600 text-white'
                          : isCurrent
                          ? 'bg-[#075247] text-white animate-pulse'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {isPassed ? <CheckCircle2 size={16} /> : item.step}
                    </div>

                    <div>
                      <h5 className="text-xs sm:text-sm font-extrabold text-[#072a24] flex items-center gap-1.5">
                        <span>{item.label}</span>
                        {isPassed && (
                          <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded">
                            Active
                          </span>
                        )}
                      </h5>
                      <p className="text-[11px] text-[#527068]">
                        {item.sub}
                      </p>
                    </div>
                  </div>

                  <ArrowRight size={14} className={isCurrent ? 'text-emerald-700' : 'text-slate-400'} />
                </button>
              );
            })}
          </div>

          {/* Generate DPR Plan Button */}
          <div className="mt-5 pt-4 border-t border-slate-100">
            <button
              onClick={onOpenReport}
              className={`w-full py-3 rounded-xl font-extrabold text-xs sm:text-sm shadow-md flex items-center justify-center gap-2 transition cursor-pointer ${
                isProfileReady
                  ? 'bg-gradient-to-r from-amber-500 to-[#15803d] text-slate-950 hover:brightness-105 animate-soft-pulse'
                  : 'bg-gradient-to-r from-emerald-700 to-[#075247] text-white hover:brightness-110'
              }`}
            >
              <FileText size={16} className={isProfileReady ? 'text-slate-950' : 'text-emerald-200'} />
              <span>{t.journeyGenReportBtn}</span>
            </button>
          </div>
        </div>

        {/* Motivational Landscape Banner */}
        <div className="relative rounded-3xl overflow-hidden shadow-card border border-[#d6e5da] bg-white group">
          <div className="h-48 relative overflow-hidden bg-emerald-950">
            <img
              src={landscapeImg}
              alt="Rural Sprout"
              className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700 opacity-90"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
            
            <div className="absolute top-4 left-4 right-4 bg-white/90 backdrop-blur-xs p-3 rounded-xl border border-white/60">
              <p className="text-xs font-bold italic text-[#064e3b] leading-tight">
                {t.journeyCardQuote}
              </p>
            </div>

            <div className="absolute bottom-4 left-4 right-4 text-white">
              <h4 className="text-lg font-black font-display text-amber-300 drop-shadow-sm">
                {t.journeyCardBanner}
              </h4>
              <p className="text-xs text-emerald-100">
                {t.appName} • {t.tagline}
              </p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
