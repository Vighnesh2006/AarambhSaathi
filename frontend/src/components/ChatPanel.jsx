import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Mic, MicOff, Trash2, ArrowRight, User, Bot, HelpCircle } from 'lucide-react';

export default function ChatPanel({
  messages,
  onSendMessage,
  isLoading,
  suggestedReplies,
  onClearChat,
  language
}) {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatContainerRef = useRef(null);

  // Auto-scroll to bottom inside container
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickClick = (text) => {
    if (isLoading) return;
    onSendMessage(text);
  };

  // Web Speech Recognition for rural accessibility
  const toggleSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported by your current browser.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = language === 'mr' ? 'mr-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';

    if (!isListening) {
      recognition.start();
      setIsListening(true);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
        setIsListening(false);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
    } else {
      recognition.stop();
      setIsListening(false);
    }
  };

  const initialPrompts = [
    { label: "🌱 Find a Business", query: "I want to explore suitable rural business options for my skills and capital." },
    { label: "🐄 Dairy Farming (₹1 Lakh)", query: "I want to start a dairy business. I have around 1 lakh rupees and experience with cattle." },
    { label: "💰 Calculate Finance", query: "I want to check my loan eligibility, monthly EMI, and credit subsidy options." },
    { label: "📜 Find Government Schemes", query: "Which government schemes provide subsidies for rural micro-enterprises in my district?" }
  ];

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-gv-primary to-gv-secondary px-5 py-3.5 text-white flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center border border-amber-300/40 text-amber-300">
              <Bot className="w-5 h-5" />
            </div>
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 ring-2 ring-gv-primary"></span>
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-1.5 font-display">
              <span>GramVantage AI Assistant</span>
              <span className="text-[10px] bg-amber-400/20 text-amber-300 px-1.5 py-0.2 rounded border border-amber-400/30">Live Hybrid AI</span>
            </h2>
            <p className="text-[11px] text-emerald-100">Decision-Support & Conversational Advisor</p>
          </div>
        </div>

        <button
          onClick={onClearChat}
          className="p-1.5 text-emerald-200 hover:text-white hover:bg-white/10 rounded-lg transition"
          title="Clear Conversation"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Message List */}
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-slate-50/50">
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={index}
              className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold shadow-sm ${
                  isUser
                    ? 'bg-slate-700 text-white'
                    : 'bg-gv-primary text-amber-300 border border-amber-400/40'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : 'GV'}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[82%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed shadow-sm ${
                  isUser
                    ? 'bg-gradient-to-br from-gv-primary to-gv-secondary text-white rounded-tr-none'
                    : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-line break-words">{msg.content}</div>
                {msg.timestamp && (
                  <div
                    className={`text-[10px] mt-1.5 text-right ${
                      isUser ? 'text-emerald-200/70' : 'text-slate-400'
                    }`}
                  >
                    {msg.timestamp}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading / Typing Indicator */}
        {isLoading && (
          <div className="flex items-start gap-2.5">
            <div className="w-8 h-8 rounded-full bg-gv-primary text-amber-300 flex items-center justify-center text-xs font-bold border border-amber-400/30">
              GV
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-gv-secondary animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-2 h-2 rounded-full bg-gv-secondary animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-2 h-2 rounded-full bg-gv-secondary animate-bounce"></span>
                <span className="text-xs text-slate-400 ml-2 font-medium">GramVantage AI is analyzing...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Quick Replies */}
      <div className="px-4 py-2 bg-slate-100/80 border-t border-slate-200">
        <div className="flex items-center space-x-1 mb-1.5 text-[11px] font-semibold text-slate-600">
          <Sparkles className="w-3 h-3 text-amber-500" />
          <span>Suggested Quick Replies:</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {suggestedReplies && suggestedReplies.length > 0 ? (
            suggestedReplies.map((reply, i) => (
              <button
                key={i}
                onClick={() => handleQuickClick(reply)}
                disabled={isLoading}
                className="text-xs bg-white hover:bg-emerald-50 text-gv-primary hover:text-gv-secondary font-medium px-2.5 py-1 rounded-full border border-gv-border shadow-2xs hover:border-gv-secondary transition flex items-center space-x-1"
              >
                <span>{reply}</span>
                <ArrowRight className="w-2.5 h-2.5 opacity-60" />
              </button>
            ))
          ) : (
            initialPrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handleQuickClick(p.query)}
                disabled={isLoading}
                className="text-xs bg-white hover:bg-emerald-50 text-gv-primary hover:text-gv-secondary font-medium px-2.5 py-1 rounded-full border border-gv-border shadow-2xs hover:border-gv-secondary transition flex items-center space-x-1"
              >
                <span>{p.label}</span>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-3 bg-white border-t border-slate-200 flex items-center gap-2">
        {/* Voice Input Button */}
        <button
          type="button"
          onClick={toggleSpeechRecognition}
          className={`p-2.5 rounded-xl border transition ${
            isListening
              ? 'bg-rose-500 text-white border-rose-600 animate-pulse'
              : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
          }`}
          title={isListening ? "Listening... click to stop" : "Voice Input (Hindi/Marathi/English)"}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            language === 'mr'
              ? 'येथे लिहा (उदा. मला दुग्ध व्यवसाय सुरू करायचा आहे...)'
              : language === 'hi'
              ? 'यहाँ लिखें (उदा. मुझे डेयरी बिजनेस शुरू करना है...)'
              : 'Type your message (e.g. I have 1 lakh and want to start dairy...)'
          }
          className="flex-1 bg-slate-50 border border-slate-300 focus:border-gv-primary focus:ring-1 focus:ring-gv-primary rounded-xl px-3.5 py-2.5 text-xs sm:text-sm text-slate-800 placeholder-slate-400 outline-none transition"
          disabled={isLoading}
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className={`p-2.5 rounded-xl font-medium text-white shadow transition flex items-center justify-center ${
            input.trim() && !isLoading
              ? 'bg-gradient-to-r from-gv-primary to-gv-secondary hover:from-gv-secondary hover:to-emerald-800 cursor-pointer'
              : 'bg-slate-300 text-slate-500 cursor-not-allowed'
          }`}
          title="Send message"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
