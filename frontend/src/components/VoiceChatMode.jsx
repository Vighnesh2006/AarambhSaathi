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
  Bot,
  AlertCircle,
  Zap,
  Play,
  Power
} from 'lucide-react';
import { getTranslation } from '../services/translations';
import { createSpeechRecognizer, speakText, stopSpeaking, playActivationChime } from '../services/voice';
import robotAvatarImg from '../assets/robot_avatar_1788638099080.jpg';

export default function VoiceChatMode({
  messages = [],
  onSendMessage,
  onSwitchToText,
  language = 'en',
  isLoading
}) {
  const t = getTranslation(language);
  const [isListening, setIsListening] = useState(false);
  const [isBotActivated, setIsBotActivated] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [transcript, setTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState([40, 70, 30, 90, 60, 45, 80, 55, 65, 35]);
  const recognitionRef = useRef(null);

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
    setTimeout(() => {
      startListening();
    }, 1000);
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
    setErrorMessage('');
    const rec = createSpeechRecognizer(language, {
      onStart: () => {
        setIsListening(true);
        setTranscript('');
      },
      onResult: (event) => {
        let currentText = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentText += event.results[i][0].transcript;
        }
        setTranscript(currentText);

        if (event.results[0].isFinal) {
          setIsListening(false);
          if (currentText.trim()) {
            onSendMessage(currentText.trim());
          }
        }
      },
      onError: (e) => {
        console.error('Speech recognition error:', e);
        setIsListening(false);
        if (e.error === 'not-allowed' || e.error === 'permission-denied') {
          setErrorMessage('Microphone access denied. Please click the camera/mic icon in your browser address bar to allow microphone access.');
        } else {
          setErrorMessage('Could not hear audio clearly. Please tap the mic to speak again or switch to Text mode.');
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

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    setIsListening(false);
    if (transcript.trim()) {
      onSendMessage(transcript.trim());
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
        
        {/* Top Header Tagline */}
        <div className="w-full flex items-center justify-between pb-4 border-b border-emerald-100">
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

          <button
            onClick={onSwitchToText}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white border border-emerald-200 text-xs font-bold text-[#075247] hover:bg-emerald-50 shadow-2xs transition"
          >
            <Keyboard size={15} />
            <span>{t.voiceSwitchToText}</span>
          </button>
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

          {/* Prominent START BOT / ACTIVATE MACHINE Button */}
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

  // ================= VIEW 2: BOT ACTIVATED & LISTENING =================
  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-between min-h-[580px] p-4 sm:p-8 bg-gradient-to-b from-[#eaf5ee] via-[#f7fbf8] to-[#f0f7f2] rounded-3xl border border-[#d6e5da] shadow-card">
      
      {/* Top Banner Tagline & Active Controls */}
      <div className="w-full flex items-center justify-between pb-4 border-b border-emerald-100">
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              🌱
            </div>
            <span className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-white animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-extrabold text-[#072a24] font-display">
                {t.voiceTitle}
              </h4>
              <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-black uppercase tracking-wider flex items-center gap-1 shadow-2xs">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-300 animate-pulse" />
                Active
              </span>
            </div>
            <p className="text-[11px] text-[#527068]">
              {t.tagline}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={toggleMute}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border transition ${
              isMuted
                ? 'bg-rose-50 text-rose-700 border-rose-200'
                : 'bg-emerald-50 text-[#075247] border-emerald-200 hover:bg-emerald-100'
            }`}
            title={isMuted ? 'Unmute Assistant Voice' : 'Mute Assistant Voice'}
          >
            {isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
            <span>{isMuted ? 'Voice Muted' : 'Voice Active'}</span>
          </button>

          <button
            onClick={handleDeactivateBot}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-300 text-xs font-bold text-amber-900 hover:bg-amber-100 transition shadow-2xs"
            title="Stop / Deactivate Bot"
          >
            <Power size={14} className="text-amber-700" />
            <span>Deactivate</span>
          </button>

          <button
            onClick={onSwitchToText}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white border border-emerald-200 text-xs font-bold text-[#075247] hover:bg-emerald-50 shadow-2xs transition"
          >
            <Keyboard size={15} />
            <span>{t.voiceSwitchToText}</span>
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="w-full max-w-md my-2 p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-center gap-2 shadow-xs">
          <AlertCircle size={18} className="shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Center AI Bot Mascot + Animated Waves */}
      <div className="flex flex-col items-center text-center my-6 space-y-4">
        
        {/* Robot Avatar with Speech Bubble */}
        <div className="relative">
          <div className="w-36 h-36 sm:w-44 sm:h-44 rounded-full p-2 bg-gradient-to-tr from-emerald-400 via-teal-300 to-amber-300 shadow-2xl animate-soft-pulse">
            <img
              src={robotAvatarImg}
              alt="Aarambh Saathi Bot"
              className="w-full h-full object-cover rounded-full bg-emerald-950 border-4 border-white shadow-inner"
            />
          </div>

          {/* Speech Bubble */}
          <div className="absolute -top-3 sm:-top-5 -right-16 sm:-right-24 bg-white rounded-2xl border-2 border-[#15803d] px-4 py-2.5 shadow-xl text-center max-w-[170px] sm:max-w-[190px]">
            <p className="text-xs sm:text-sm font-black text-[#064e3b] font-display">
              {t.voiceBubblePrompt}
            </p>
            <p className="text-[10px] text-emerald-700 font-semibold mt-0.5">
              {t.voiceBubbleSub}
            </p>
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

        {/* Status Text */}
        <div>
          <h3 className="text-base sm:text-lg font-black text-[#072a24]">
            {isListening
              ? (transcript ? `"${transcript}"` : t.voiceListening)
              : (isLoading ? t.chatThinking : t.voiceTapToSpeak)}
          </h3>
          <p className="text-xs text-[#527068] mt-0.5">
            {t.voiceLangSupport}
          </p>
        </div>

        {/* Big Glowing Microphone Button */}
        <div className="pt-2">
          <button
            onClick={isListening ? stopListening : startListening}
            disabled={isLoading}
            className={`w-20 h-20 sm:w-24 sm:h-24 rounded-full flex flex-col items-center justify-center text-white shadow-2xl transition-all duration-300 transform active:scale-95 ${
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
