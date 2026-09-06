import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Keyboard,
  Volume2,
  VolumeX,
  Sparkles,
  ArrowRight,
  Sprout,
  AlertCircle,
  Zap,
  Play,
  Power,
  Send,
  X,
  Globe
} from 'lucide-react';
import { getTranslation } from '../services/translations';
import { createSpeechRecognizer, speakText, stopSpeaking, playActivationChime } from '../services/voice';
import robotAvatarImg from '../assets/robot_avatar_1788638099080.jpg';

export default function VoiceChatMode({
  messages = [],
  onSendMessage,
  onSwitchToText,
  language = 'en',
  onLanguageChange,
  isLoading
}) {
  const t = getTranslation(language);
  const [isListening, setIsListening] = useState(false);
  const [isBotActivated, setIsBotActivated] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [transcript, setTranscript] = useState('');
  const [interimText, setInterimText] = useState('');
  const [audioLevel, setAudioLevel] = useState([40, 70, 30, 90, 60, 45, 80, 55, 65, 35]);
  const recognitionRef = useRef(null);
  const isHoldingRef = useRef(false);

  // Latest assistant message
  const lastBotMessage = messages.slice().reverse().find(m => m.role === 'assistant');

  useEffect(() => {
    return () => {
      stopSpeaking();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, []);

  // When language changes, update active speech synthesis or recognition if needed
  const handleLangSelect = (newLang) => {
    stopSpeaking();
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
    }
    if (onLanguageChange) {
      onLanguageChange(newLang);
    }
  };

  const handleActivateBot = () => {
    try {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
      }
    } catch (e) {}
    playActivationChime();
    setIsBotActivated(true);
    setErrorMessage('');
    if (lastBotMessage && lastBotMessage.content && !isMuted) {
      speakText(lastBotMessage.content, language);
    }
    // Note: Auto-start listening removed so random noise is never recorded. User explicitly holds or taps mic.
  };

  const handleDeactivateBot = () => {
    stopSpeaking();
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    setIsListening(false);
    setIsBotActivated(false);
    setTranscript('');
    setInterimText('');
  };

  // Animated wave visualizer effect when listening
  useEffect(() => {
    let interval = null;
    if (isListening) {
      interval = setInterval(() => {
        setAudioLevel([
          Math.floor(Math.random() * 70) + 30,
          Math.floor(Math.random() * 85) + 15,
          Math.floor(Math.random() * 95) + 10,
          Math.floor(Math.random() * 90) + 20,
          Math.floor(Math.random() * 80) + 30,
          Math.floor(Math.random() * 95) + 10,
          Math.floor(Math.random() * 85) + 20,
          Math.floor(Math.random() * 75) + 25,
          Math.floor(Math.random() * 90) + 10,
          Math.floor(Math.random() * 60) + 30,
        ]);
      }, 150);
    } else {
      setAudioLevel([25, 35, 20, 45, 30, 20, 35, 25, 30, 20]);
    }
    return () => clearInterval(interval);
  }, [isListening]);

  const toggleMute = () => {
    if (!isMuted) {
      stopSpeaking();
      setIsMuted(true);
    } else {
      setIsMuted(false);
      if (lastBotMessage?.content) {
        speakText(lastBotMessage.content, language);
      }
    }
  };

  // Speech Recognition Handling
  const startListening = () => {
    stopSpeaking(); // stop AI bot voice if currently speaking
    setErrorMessage('');
    setTranscript('');
    setInterimText('');

    const rec = createSpeechRecognizer(language, {
      onStart: () => {
        setIsListening(true);
      },
      onResult: (event) => {
        let finalStr = '';
        let interimStr = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          if (res.isFinal) {
            finalStr += res[0].transcript;
          } else {
            interimStr += res[0].transcript;
          }
        }
        if (finalStr) {
          setTranscript(prev => (prev ? prev + ' ' + finalStr : finalStr).trim());
        }
        setInterimText(interimStr.trim());
      },
      onError: (e) => {
        console.error('Speech recognition error:', e);
        setIsListening(false);
        if (e.error === 'not-allowed' || e.error === 'permission-denied') {
          setErrorMessage('Microphone access denied. Please click the mic icon in your browser address bar to allow access.');
        } else if (e.error !== 'no-speech' && e.error !== 'aborted') {
          setErrorMessage('Could not capture audio clearly. Please tap or hold the mic button to speak again.');
        }
      },
      onEnd: () => {
        setIsListening(false);
      }
    });

    if (!rec) {
      setErrorMessage('Speech recognition is not supported in this browser. Please switch to Text mode.');
      return;
    }

    try {
      recognitionRef.current = rec;
      rec.start();
    } catch (err) {
      console.error('Speech start error:', err);
      setIsListening(false);
    }
  };

  const stopListening = (autoSendIfText = false) => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    setIsListening(false);

    if (autoSendIfText) {
      const fullText = (transcript + ' ' + interimText).trim();
      if (fullText) {
        onSendMessage(fullText);
        setTranscript('');
        setInterimText('');
      }
    }
  };

  const handleManualSend = () => {
    const fullText = (transcript + ' ' + interimText).trim();
    if (fullText) {
      stopListening(false);
      onSendMessage(fullText);
      setTranscript('');
      setInterimText('');
    }
  };

  const handleClearTranscript = () => {
    setTranscript('');
    setInterimText('');
  };

  // Hold-to-Talk & Tap-to-Talk Event Handlers
  const handleMouseDown = () => {
    isHoldingRef.current = true;
    if (!isListening) {
      startListening();
    }
  };

  const handleMouseUp = () => {
    if (isHoldingRef.current) {
      isHoldingRef.current = false;
      stopListening(true);
    }
  };

  const handleTouchStart = (e) => {
    e.preventDefault();
    isHoldingRef.current = true;
    if (!isListening) {
      startListening();
    }
  };

  const handleTouchEnd = (e) => {
    e.preventDefault();
    if (isHoldingRef.current) {
      isHoldingRef.current = false;
      stopListening(true);
    }
  };

  const handleClickMic = () => {
    // If it was just a tap without holding
    if (!isHoldingRef.current) {
      if (isListening) {
        stopListening(true);
      } else {
        startListening();
      }
    }
  };

  const handleQuickStarter = (queryText) => {
    onSendMessage(queryText);
    onSwitchToText();
  };

  const starterChips = [
    {
      icon: Sprout,
      primaryText: t.voiceStarter1,
      subText: t.voiceStarter1Sub,
      query: language === 'mr' ? 'मला माझ्या गावात चांगला व्यवसाय सुरू करायचा आहे.' : language === 'hi' ? 'मुझे अपने गाँव में एक अच्छा व्यवसाय शुरू करना है।' : 'I want to explore suitable rural business options for my skills and capital.'
    },
    {
      icon: '₹',
      primaryText: t.voiceStarter2,
      subText: t.voiceStarter2Sub,
      query: language === 'mr' ? 'माझ्याकडे १ लाख रुपये भांडवल आहे, योग्य नफा मिळणारा व्यवसाय सांगा.' : language === 'hi' ? 'मेरे पास 1 लाख रुपये हैं, मुझे अच्छा लाभ देने वाला काम बताएं।' : 'I have 1 lakh rupees capital and I want to start a business with good monthly profit.'
    },
    {
      icon: '📍',
      primaryText: t.voiceStarter3,
      subText: t.voiceStarter3Sub,
      query: language === 'mr' ? 'माझे गाव पुणे जिल्ह्यात आहे, येथे कोणत्या व्यवसायाला जास्त मागणी आहे?' : language === 'hi' ? 'मेरा गाँव पुणे के पास है, यहाँ कौन सा व्यवसाय सबसे ज्यादा चलेगा?' : 'I am located near Pune, Maharashtra. What business is feasible here?'
    }
  ];

  // ================= VIEW 1: DORMANT / BOT NOT ACTIVATED YET =================
  if (!isBotActivated) {
    return (
      <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-between min-h-[560px] p-6 sm:p-10 bg-gradient-to-b from-[#eaf5ee] via-[#f7fbf8] to-[#f0f7f2] rounded-3xl border border-[#d6e5da] shadow-card text-center relative overflow-hidden">
        
        {/* Top Header Tagline & Language Selector */}
        <div className="w-full flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-emerald-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              🌱
            </div>
            <div className="text-left">
              <h4 className="text-sm font-extrabold text-[#072a24] font-display">
                {t.voiceTitle}
              </h4>
              <p className="text-[11px] text-[#527068]">
                {t.tagline}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Switcher Pills */}
            <div className="flex rounded-xl bg-white p-1 border border-emerald-200 shadow-2xs">
              <button
                onClick={() => handleLangSelect('en')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                  language === 'en' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => handleLangSelect('hi')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                  language === 'hi' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
                }`}
              >
                हिन्दी
              </button>
              <button
                onClick={() => handleLangSelect('mr')}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                  language === 'mr' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
                }`}
              >
                मराठी
              </button>
            </div>

            <button
              onClick={onSwitchToText}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white border border-emerald-200 text-xs font-bold text-[#075247] hover:bg-emerald-50 shadow-2xs transition"
            >
              <Keyboard size={15} />
              <span>{t.voiceSwitchToText}</span>
            </button>
          </div>
        </div>

        {/* Center Activation Card */}
        <div className="flex flex-col items-center my-auto py-8 space-y-6 max-w-lg">
          
          {/* Avatar with Animated Pulse Ring & Status Badge */}
          <div className="relative">
            <div className="w-36 h-36 sm:w-44 sm:h-44 rounded-full p-2 bg-gradient-to-tr from-emerald-500 via-teal-400 to-amber-300 shadow-2xl animate-pulse">
              <img
                src={robotAvatarImg}
                alt="Aarambh Saathi Bot"
                className="w-full h-full object-cover rounded-full bg-emerald-950 border-4 border-white shadow-inner"
              />
            </div>
            <span className="absolute bottom-2 right-2 px-3 py-1 bg-amber-400 text-slate-950 text-xs font-black rounded-full shadow-md border-2 border-white flex items-center gap-1">
              <Zap size={14} className="fill-slate-950" />
              <span>READY</span>
            </span>
          </div>

          <div className="space-y-2">
            <h3 className="text-xl sm:text-2xl font-black text-[#072a24] font-display">
              {t.botActivateTitle}
            </h3>
            <p className="text-xs sm:text-sm text-[#527068] leading-relaxed">
              {t.botActivateDesc}
            </p>
          </div>

          {/* Prominent START BOT Button */}
          <button
            onClick={handleActivateBot}
            className="w-full py-4 px-8 rounded-2xl bg-gradient-to-r from-[#075247] via-[#15803d] to-emerald-600 hover:from-[#063f39] hover:to-emerald-700 text-white font-black text-base shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3 border-2 border-amber-300/40 active:scale-95 group cursor-pointer"
          >
            <Play size={24} className="fill-white text-white group-hover:translate-x-0.5 transition" />
            <div className="flex flex-col items-start text-left">
              <span className="font-display tracking-wide">{t.botActivateBtn}</span>
              <span className="text-[11px] font-normal text-emerald-100">{t.botActivateSub}</span>
            </div>
          </button>

        </div>

        {/* Quick Starters at Bottom */}
        <div className="w-full pt-4 border-t border-emerald-100">
          <div className="flex items-center justify-between text-xs text-[#527068]">
            <span className="flex items-center gap-2">
              <Sparkles size={14} className="text-amber-500" />
              <span>{t.voiceLangSupport}</span>
            </span>
            <button
              onClick={onSwitchToText}
              className="font-bold text-[#075247] hover:underline flex items-center gap-1"
            >
              <span>{t.voiceFooterSwitchBtn}</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

      </div>
    );
  }

  // ================= VIEW 2: BOT ACTIVATED & READY FOR HOLD/TAP TO SPEAK =================
  const activeTranscript = (transcript + ' ' + interimText).trim();

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-between min-h-[580px] p-4 sm:p-8 bg-gradient-to-b from-[#eaf5ee] via-[#f7fbf8] to-[#f0f7f2] rounded-3xl border border-[#d6e5da] shadow-card">
      
      {/* Top Banner Tagline & Active Controls */}
      <div className="w-full flex flex-wrap items-center justify-between gap-2.5 pb-3 sm:pb-4 border-b border-emerald-100">
        <div className="flex items-center gap-2">
          <div className="relative shrink-0">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              🌱
            </div>
            <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-white animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-xs sm:text-sm font-extrabold text-[#072a24] font-display">
                {t.voiceTitle}
              </h4>
              <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[9px] sm:text-[10px] font-black uppercase tracking-wider flex items-center gap-1 shadow-2xs">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-300 animate-pulse" />
                Active
              </span>
            </div>
            <p className="text-[11px] text-[#527068] hidden sm:block">
              {t.tagline}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {/* Language Switcher Pills */}
          <div className="flex rounded-xl bg-white p-0.5 border border-emerald-200 shadow-2xs">
            <button
              onClick={() => handleLangSelect('en')}
              className={`px-2 py-0.5 rounded-lg text-[10px] sm:text-xs font-bold transition ${
                language === 'en' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => handleLangSelect('hi')}
              className={`px-2 py-0.5 rounded-lg text-[10px] sm:text-xs font-bold transition ${
                language === 'hi' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => handleLangSelect('mr')}
              className={`px-2 py-0.5 rounded-lg text-[10px] sm:text-xs font-bold transition ${
                language === 'mr' ? 'bg-[#075247] text-white' : 'text-slate-600 hover:text-emerald-900'
              }`}
            >
              मराठी
            </button>
          </div>

          <button
            onClick={toggleMute}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold border transition ${
              isMuted
                ? 'bg-rose-50 text-rose-700 border-rose-200'
                : 'bg-emerald-50 text-[#075247] border-emerald-200 hover:bg-emerald-100'
            }`}
            title={isMuted ? 'Unmute Assistant Voice' : 'Mute Assistant Voice'}
          >
            {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
            <span className="hidden xs:inline">{isMuted ? 'Muted' : 'Voice'}</span>
          </button>

          <button
            onClick={handleDeactivateBot}
            className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-amber-50 border border-amber-300 text-xs font-bold text-amber-900 hover:bg-amber-100 transition shadow-2xs"
            title="Stop / Deactivate Bot"
          >
            <Power size={13} className="text-amber-700" />
            <span>Stop</span>
          </button>

          <button
            onClick={onSwitchToText}
            className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-white border border-emerald-200 text-xs font-bold text-[#075247] hover:bg-emerald-50 shadow-2xs transition"
          >
            <Keyboard size={14} />
            <span className="hidden xs:inline">{t.voiceSwitchToText}</span>
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="w-full max-w-md my-2 p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-center gap-2 shadow-xs">
          <AlertCircle size={16} className="shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Center AI Bot Mascot + Wave & Mic Control */}
      <div className="flex flex-col items-center text-center my-4 sm:my-6 space-y-3.5 max-w-xl w-full">
        
        {/* Robot Avatar & Speech Bubble (Clean layout without overlap) */}
        <div className="flex flex-col items-center space-y-3">
          {/* Speech Bubble cleanly positioned ABOVE avatar */}
          <div className="bg-white rounded-2xl border-2 border-[#15803d] px-4 py-2 sm:px-5 sm:py-2.5 shadow-md text-center max-w-[240px] sm:max-w-[260px] mx-auto">
            <p className="text-xs sm:text-sm font-black text-[#064e3b] font-display leading-tight">
              {t.voiceBubblePrompt}
            </p>
            <p className="text-[9px] sm:text-[10px] text-emerald-700 font-semibold mt-0.5">
              {t.voiceBubbleSub}
            </p>
          </div>

          {/* Robot Avatar Image */}
          <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-full p-2 bg-gradient-to-tr from-emerald-400 via-teal-300 to-amber-300 shadow-2xl animate-soft-pulse mx-auto">
            <img
              src={robotAvatarImg}
              alt="Aarambh Saathi Bot"
              className="w-full h-full object-cover rounded-full bg-emerald-950 border-4 border-white shadow-inner"
            />
          </div>
        </div>

        {/* Audio Wave Visualizer */}
        <div className="flex items-center justify-center gap-1.5 h-12 px-6 py-2 bg-white/80 backdrop-blur-sm rounded-full border border-emerald-200 shadow-inner">
          {audioLevel.map((height, idx) => (
            <span
              key={idx}
              style={{ height: `${height}%` }}
              className={`w-1.5 rounded-full transition-all duration-150 ${
                isListening ? 'bg-gradient-to-t from-emerald-600 to-amber-400' : 'bg-slate-300'
              }`}
            />
          ))}
        </div>

        {/* Status Prompt */}
        <div>
          <h3 className="text-base sm:text-lg font-black text-[#072a24]">
            {isListening
              ? (activeTranscript ? `"${activeTranscript}"` : t.voiceListening)
              : (isLoading ? t.chatThinking : (activeTranscript ? `"${activeTranscript}"` : t.voiceTapToSpeak))}
          </h3>
          <p className="text-xs text-[#527068] mt-0.5 font-medium">
            {isListening
              ? "Hold mic or tap again to stop & send"
              : "Hold or Tap mic button to record your question"}
          </p>
        </div>

        {/* Live Transcript Display Box with Send & Clear Buttons */}
        {activeTranscript && (
          <div className="w-full p-4 rounded-2xl bg-white border border-emerald-300 shadow-md flex items-center justify-between gap-3 animate-fade-in">
            <div className="text-left flex-1 min-w-0">
              <span className="text-[10px] uppercase tracking-wider font-extrabold text-emerald-700 block">
                Recorded Input ({language === 'mr' ? 'मराठी' : language === 'hi' ? 'हिंदी' : 'English'}):
              </span>
              <p className="text-xs sm:text-sm font-semibold text-slate-800 break-words mt-0.5">
                "{activeTranscript}"
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleClearTranscript}
                className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition"
                title="Clear transcript"
              >
                <X size={16} />
              </button>
              <button
                onClick={handleManualSend}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#075247] hover:bg-[#063f39] text-white text-xs font-bold shadow-md transition cursor-pointer"
              >
                <Send size={14} />
                <span>Send</span>
              </button>
            </div>
          </div>
        )}

        {/* Big Glowing Microphone Button (Hold or Tap) */}
        <div className="pt-2">
          <button
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            onClick={handleClickMic}
            disabled={isLoading}
            className={`w-20 h-20 sm:w-24 sm:h-24 rounded-full flex flex-col items-center justify-center text-white shadow-2xl transition-all duration-300 transform active:scale-95 cursor-pointer user-select-none select-none touch-none ${
              isListening
                ? 'bg-rose-600 hover:bg-rose-700 animate-pulse ring-8 ring-rose-300/50'
                : 'bg-gradient-to-tr from-[#075247] to-[#15803d] hover:scale-105 ring-8 ring-emerald-200/60'
            }`}
          >
            {isListening ? <MicOff size={32} /> : <Mic size={36} />}
            <span className="text-[10px] font-extrabold mt-1 tracking-wider uppercase">
              {isListening ? t.voiceTapToStop : t.voiceTapAction}
            </span>
          </button>
          <p className="text-[11px] text-[#527068] mt-2 font-bold">
            👆 Press & Hold OR Tap to Speak
          </p>
        </div>
      </div>

      {/* Bottom Quick Voice Starters */}
      <div className="w-full space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {starterChips.map((chip, idx) => {
            const Icon = chip.icon;
            return (
              <button
                key={idx}
                onClick={() => handleQuickStarter(chip.query)}
                className="flex items-center gap-3 p-3 rounded-2xl bg-white border border-[#dce8e0] text-left hover:border-emerald-400 hover:shadow-md transition group cursor-pointer"
              >
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-800 font-bold flex items-center justify-center shrink-0 border border-emerald-100 group-hover:bg-[#075247] group-hover:text-white transition">
                  {typeof Icon === 'string' ? Icon : <Icon size={20} />}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs sm:text-sm font-extrabold text-[#072a24] truncate">
                    {chip.primaryText}
                  </p>
                  <p className="text-[11px] text-[#527068] truncate">
                    {chip.subText}
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer switch prompt */}
        <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-white/70 border border-emerald-100 text-xs text-[#527068]">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>{t.voiceFooterPrompt}</span>
          </span>
          <button
            onClick={onSwitchToText}
            className="font-bold text-[#075247] hover:underline flex items-center gap-1"
          >
            <span>{t.voiceFooterSwitchBtn}</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

    </div>
  );
}
