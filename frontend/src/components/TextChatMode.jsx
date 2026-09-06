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
  SlidersHorizontal,
  Globe
} from 'lucide-react';
import { getTranslation } from '../services/translations';
import robotAvatarImg from '../assets/robot_avatar_1788638099080.jpg';
import landscapeImg from '../assets/rural_sprout_landscape_1788638113042.jpg';

// Helper to parse markdown bold (**text**) and code (`text`) into clean JSX elements, eliminating raw ** asterisks
const renderFormattedMessage = (content, isBot) => {
  if (!content) return null;

  const lines = content.split('\n');

  return lines.map((line, lineIdx) => {
    const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);

    const formattedParts = parts.map((part, partIdx) => {
      if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
        const text = part.slice(2, -2);
        return (
          <strong
            key={partIdx}
            className={isBot ? "font-extrabold text-[#063f39]" : "font-extrabold text-amber-300"}
          >
            {text}
          </strong>
        );
      } else if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
        const codeText = part.slice(1, -1);
        return (
          <code
            key={partIdx}
            className={`mx-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-bold ${
              isBot
                ? "bg-emerald-100/70 text-[#075247] border border-emerald-200"
                : "bg-emerald-900/60 text-amber-300 border border-emerald-700"
            }`}
          >
            {codeText}
          </code>
        );
      }
      // Strip any stray unmatched ** asterisks
      return part.replace(/\*\*/g, '');
    });

    return (
      <React.Fragment key={lineIdx}>
        {formattedParts}
        {lineIdx < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
};

export default function TextChatMode({
  messages,
  onSendMessage,
  isLoading,
  suggestedReplies,
  onClearChat,
  language = 'en',
  onLanguageChange,
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
    <div className="w-full max-w-5xl mx-auto flex flex-col gap-8">
      
      {/* ================= MAIN CHAT CONTAINER (Full Width) ================= */}
      <div className="w-full flex flex-col h-[calc(100vh-140px)] min-h-[440px] sm:min-h-[580px] bg-white rounded-3xl border border-[#d6e5da] shadow-card overflow-hidden">
        
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-[#075247] to-[#15803d] px-3 py-2.5 sm:px-5 sm:py-3.5 text-white flex items-center justify-between shadow-xs gap-2">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            <div className="relative shrink-0">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-white/10 p-0.5 border border-amber-300/60 overflow-hidden shadow-inner">
                <img
                  src={robotAvatarImg}
                  alt="Aarambh Saathi Mascot"
                  className="w-full h-full object-cover rounded-full"
                />
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-emerald-400 ring-2 ring-[#075247]" />
            </div>

            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <h3 className="text-sm sm:text-base font-extrabold font-display leading-tight truncate">
                  {t.appName}
                </h3>
                <span className="text-[9px] sm:text-[10px] bg-amber-400 text-slate-950 font-black px-1.5 sm:px-2 py-0.5 rounded-full shadow-2xs shrink-0">
                  {t.chatAiAdvisorBadge}
                </span>
              </div>
              <p className="text-[11px] sm:text-xs text-emerald-100 hidden md:block truncate">
                {t.chatSubtitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 sm:gap-2 shrink-0">
            {/* Multilingual Choice Option Selector */}
            <div className="flex items-center gap-0.5 sm:gap-1 bg-black/25 p-0.5 sm:p-1 rounded-xl border border-white/20 shadow-inner">
              <Globe size={12} className="text-amber-300 ml-0.5 shrink-0 hidden xs:inline" />
              <button
                type="button"
                onClick={() => onLanguageChange && onLanguageChange('en')}
                className={`px-1.5 sm:px-2 py-0.5 rounded-lg text-[10px] sm:text-[11px] font-black transition ${
                  language === 'en'
                    ? 'bg-amber-400 text-slate-950 shadow-2xs'
                    : 'text-emerald-100 hover:text-white'
                }`}
                title="Switch to English"
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => onLanguageChange && onLanguageChange('hi')}
                className={`px-1.5 sm:px-2 py-0.5 rounded-lg text-[10px] sm:text-[11px] font-black transition ${
                  language === 'hi'
                    ? 'bg-amber-400 text-slate-950 shadow-2xs'
                    : 'text-emerald-100 hover:text-white'
                }`}
                title="हिन्दी में बदलें"
              >
                हिंदी
              </button>
              <button
                type="button"
                onClick={() => onLanguageChange && onLanguageChange('mr')}
                className={`px-1.5 sm:px-2 py-0.5 rounded-lg text-[10px] sm:text-[11px] font-black transition ${
                  language === 'mr'
                    ? 'bg-amber-400 text-slate-950 shadow-2xs'
                    : 'text-emerald-100 hover:text-white'
                }`}
                title="मराठीत बदला"
              >
                मराठी
              </button>
            </div>

            <button
              onClick={onSwitchToVoice}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-white/15 hover:bg-white/25 text-xs font-bold text-white border border-white/20 transition shadow-2xs"
              title={t.chatSwitchToVoice}
            >
              <Mic size={14} className="text-amber-300" />
              <span className="hidden sm:inline">{t.chatSwitchToVoice}</span>
            </button>

            <button
              onClick={onClearChat}
              className="p-1.5 sm:p-2 rounded-xl bg-white/10 hover:bg-white/20 text-emerald-100 hover:text-white transition"
              title={t.chatResetBtn}
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3.5 bg-[#f9fbf9]">
          {messages.map((msg, index) => {
            const isBot = msg.role === 'assistant';
            return (
              <div
                key={index}
                className={`flex gap-2 sm:gap-3 ${isBot ? 'justify-start' : 'justify-end'}`}
              >
                {/* Bot Avatar */}
                {isBot && (
                  <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full shrink-0 overflow-hidden bg-emerald-700 border-2 border-white shadow-md">
                    <img
                      src={robotAvatarImg}
                      alt="Aarambh Saathi"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <div className="max-w-[88%] sm:max-w-[78%] space-y-2">
                  <div
                    className={`rounded-2xl px-3.5 py-2.5 sm:px-4 sm:py-3 text-xs sm:text-sm leading-relaxed shadow-xs ${
                      isBot
                        ? 'bg-white text-[#072a24] border border-[#e1ece4] rounded-tl-sm'
                        : 'bg-[#075247] text-white font-medium rounded-tr-sm shadow-md'
                    }`}
                  >
                    <div className="leading-relaxed font-normal">{renderFormattedMessage(msg.content, isBot)}</div>
                    <span
                      className={`block text-[9px] sm:text-[10px] mt-1 text-right font-medium ${
                        isBot ? 'text-slate-400' : 'text-emerald-200'
                      }`}
                    >
                      {msg.timestamp || 'Just now'}
                    </span>
                  </div>
                </div>

                {/* User Avatar */}
                {!isBot && (
                  <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full shrink-0 bg-[#063f39] text-amber-300 font-bold flex items-center justify-center border-2 border-white shadow-md text-xs">
                    <User size={16} />
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
          <div className="px-3 py-2 bg-white border-t border-[#e8efe9] flex items-center gap-2 overflow-x-auto">
            <span className="text-[11px] font-bold text-[#527068] shrink-0">{t.chatSuggestions}</span>
            {suggestedReplies.map((reply, rIdx) => (
              <button
                key={rIdx}
                onClick={() => handleQuickOptionClick(reply)}
                className="whitespace-nowrap px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 hover:bg-emerald-100 text-[#075247] border border-emerald-200 transition shrink-0"
              >
                {reply}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <div className="p-2.5 sm:p-4 bg-white border-t border-[#dce8e0]">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t.chatPlaceholder}
                className="w-full px-3.5 py-2.5 sm:px-4 sm:py-3 rounded-2xl bg-[#f4f8f5] border border-[#d6e5da] text-xs sm:text-sm text-[#072a24] focus:outline-hidden focus:ring-2 focus:ring-[#075247] focus:bg-white placeholder-slate-400 font-medium transition"
              />
            </div>

            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={`p-3 sm:p-3.5 rounded-2xl flex items-center justify-center transition-all shrink-0 ${
                input.trim() && !isLoading
                  ? 'bg-[#075247] hover:bg-[#063f39] text-white shadow-md active:scale-95'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              <Send size={16} />
            </button>
          </form>

          {/* 4 Starter Fast Actions */}
          <div className="mt-2 flex items-center gap-2 overflow-x-auto pb-1 sm:flex-wrap shrink-0">
            <button
              onClick={() => onJourneyStepClick(2)}
              className="px-2.5 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 shrink-0 shadow-2xs"
            >
              <span>🌾</span>
              <span>{t.actFindBiz}</span>
            </button>
            <button
              onClick={() => onSendMessage(language === 'mr' ? 'माझ्या व्यवसायासाठी सप्लायर आणि मशिनरी यादी दाखवा' : language === 'hi' ? 'मेरे व्यवसाय के लिए सप्लायर और मशीनरी सूची दिखाएं' : 'Show me machinery and verified supplier details')}
              className="px-2.5 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 shrink-0 shadow-2xs"
            >
              <span>⚙️</span>
              <span>{language === 'mr' ? 'सप्लायर व मशिनरी पहा' : language === 'hi' ? 'सप्लायर एवं मशीनरी देखें' : 'View Machinery & Suppliers'}</span>
            </button>
            <button
              onClick={() => onJourneyStepClick(3)}
              className="px-2.5 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 shrink-0 shadow-2xs"
            >
              <span>💰</span>
              <span>{t.actCalcFinance}</span>
            </button>
            <button
              onClick={() => onJourneyStepClick(4)}
              className="px-2.5 py-1 rounded-lg text-xs font-semibold text-[#075247] bg-[#edf7ee] hover:bg-[#e0f2e2] transition flex items-center gap-1.5 shrink-0 shadow-2xs"
            >
              <span>🏛️</span>
              <span>{t.actCheckSchemes}</span>
            </button>
          </div>
        </div>

      </div>



    </div>
  );
}
