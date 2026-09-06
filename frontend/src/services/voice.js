let cachedVoices = [];

function initVoices() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      cachedVoices = window.speechSynthesis.getVoices() || [];
    } catch (e) {}
  }
}

if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  initVoices();
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = () => {
      try {
        cachedVoices = window.speechSynthesis.getVoices() || [];
      } catch (e) {}
    };
  }
}

export function speakText(text, lang = 'en') {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    console.warn('Speech synthesis not supported in this browser.');
    return;
  }

  // Ensure speech synthesis is unpaused in Chrome/Edge/Safari
  try {
    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();
  } catch (e) {}

  // Strip markdown formatting (*, #, emojis, URLs, bullets) for clean natural voice reading
  let cleanText = text
    .replace(/\*+/g, '')
    .replace(/#+/g, '')
    .replace(/[`_~]/g, '')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
    .replace(/•/g, '')
    .replace(/\n+/g, '. ')
    .replace(/\s+/g, ' ')
    .trim();

  if (!cleanText) return;

  // Truncate to first 300 chars to avoid Chromium long-utterance freeze bug
  if (cleanText.length > 320) {
    let periodIdx = cleanText.indexOf('.', 200);
    if (periodIdx === -1) periodIdx = cleanText.indexOf('।', 200);
    if (periodIdx !== -1 && periodIdx < 350) {
      cleanText = cleanText.substring(0, periodIdx + 1);
    } else {
      cleanText = cleanText.substring(0, 300) + '...';
    }
  }

  let freshVoices = [];
  try {
    freshVoices = window.speechSynthesis.getVoices() || [];
  } catch (e) {}
  const availableVoices = freshVoices.length > 0 ? freshVoices : cachedVoices;
  
  let targetLang = 'en-IN';
  let selectedVoice = null;

  if (lang === 'mr') {
    // 1. Check for native Marathi voice
    selectedVoice = availableVoices.find(v => 
      v.lang.toLowerCase().includes('mr') || 
      v.name.toLowerCase().includes('marathi')
    );
    if (selectedVoice) {
      targetLang = 'mr-IN';
    } else {
      // 2. Fallback to Hindi voice (Hindi engine reads Marathi Devanagari script fluently)
      targetLang = 'hi-IN';
      selectedVoice = availableVoices.find(v => 
        v.lang.toLowerCase().includes('hi') || 
        v.name.toLowerCase().includes('hindi')
      );
    }
  } else if (lang === 'hi') {
    targetLang = 'hi-IN';
    selectedVoice = availableVoices.find(v => 
      v.lang.toLowerCase().includes('hi') || 
      v.name.toLowerCase().includes('hindi')
    );
  } else {
    targetLang = 'en-IN';
    selectedVoice = availableVoices.find(v => 
      v.lang.toLowerCase().includes('en-in') || 
      (v.lang.toLowerCase().includes('en') && v.name.toLowerCase().includes('india')) ||
      v.lang.toLowerCase().includes('en')
    );
  }

  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.lang = targetLang;
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }
  utterance.rate = 0.92;
  utterance.pitch = 1.0;

  // Utterance Error Fallback: retry with generic Hindi/English lang if browser rejects voice
  utterance.onerror = (evt) => {
    console.warn('SpeechSynthesis error, retrying with fallback voice:', evt);
    try {
      const fallbackUtterance = new SpeechSynthesisUtterance(cleanText);
      fallbackUtterance.lang = (lang === 'mr' || lang === 'hi') ? 'hi-IN' : 'en-IN';
      fallbackUtterance.rate = 0.92;
      window.speechSynthesis.resume();
      window.speechSynthesis.speak(fallbackUtterance);
    } catch (e) {}
  };

  setTimeout(() => {
    try {
      window.speechSynthesis.resume();
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn('Speech synthesis speak error:', err);
    }
  }, 60);
}

export function stopSpeaking() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }
}

export function playActivationChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(523.25, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.12);
    osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.25);
    
    gain.gain.setValueAtTime(0.18, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.45);
  } catch (e) {
    console.warn('Audio chime failed:', e);
  }
}

export function createSpeechRecognizer(lang, callbacks = {}) {
  if (typeof window === 'undefined') return null;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    return null;
  }

  const rec = new SpeechRecognition();
  rec.continuous = false;
  rec.interimResults = true;
  rec.lang = lang === 'mr' ? 'mr-IN' : lang === 'hi' ? 'hi-IN' : 'en-IN';

  if (callbacks.onStart) rec.onstart = callbacks.onStart;
  if (callbacks.onResult) rec.onresult = callbacks.onResult;
  if (callbacks.onError) rec.onerror = callbacks.onError;
  if (callbacks.onEnd) rec.onend = callbacks.onEnd;

  return rec;
}

