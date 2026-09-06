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
  Bot
} from 'lucide-react';
import { getTranslation } from '../services/translations';
import robotAvatarImg from '../assets/robot_avatar_1788638099080.jpg';

export default function VoiceChatMode({
  onSendMessage,
  onSwitchToText,
  language = 'en',
  isLoading
}) {
  const t = getTranslation(language);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState([40, 70, 30, 90, 60, 45, 80, 55, 65, 35]);
  const recognitionRef = useRef(null);

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

  // Speech Recognition Handling
  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser. Please switch to Text mode.');
      return;
    }

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;
      rec.lang = language === 'mr' ? 'mr-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';

      rec.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };

      rec.onresult = (event) => {
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
      };

      rec.onerror = (e) => {
        console.error('Speech recognition error:', e);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
      rec.start();
    } catch (err) {
      console.error('Speech start error:', err);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
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

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-between min-h-[580px] p-4 sm:p-8 bg-gradient-to-b from-[#eaf5ee] via-[#f7fbf8] to-[#f0f7f2] rounded-3xl border border-[#d6e5da] shadow-card">
      
      {/* Top Banner Tagline */}
      <div className="w-full flex items-center justify-between pb-4 border-b border-emerald-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            🌱
          </div>
          <div>
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
                className="flex items-center gap-3 p-3 rounded-2xl bg-white border border-[#dce8e0] text-left hover:border-emerald-400 hover:shadow-md transition group"
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
            <span className="w-2 h-2 rounded-full bg-amber-400" />
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
