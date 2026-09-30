import React, { useState, useRef, useEffect } from 'react';
import {
  Sparkles,
  X,
  Send,
  ShieldCheck,
  Bot,
  User,
  ExternalLink,
  ChevronDown,
  RotateCcw
} from 'lucide-react';
import { copilotApi, ChatResponse } from '../../api/copilot';
import { CopilotMessage } from '../../types';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';
import { VoiceInput } from './VoiceInput';
import { EvidenceDrawer } from './EvidenceDrawer';
import { MarkdownMessage } from '../common/MarkdownMessage';

const SUGGESTIONS = [
  'Which PHCs are at highest medicine stock-out risk?',
  'Which districts have the most critical shortages?',
  'Why is PHC-BR-PAT-001 at risk?',
  'Which PHC can supply Paracetamol to PHC-BR-PAT-001?',
  'Show today active emergency status.',
  'What happens if demand increases by 30% in Patna?'
];

interface FloatingCopilotProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FloatingCopilot: React.FC<FloatingCopilotProps> = ({ isOpen, onClose }) => {
  const { language, t } = useLanguage();
  const { user } = useAuth();

  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<CopilotMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text:
        language === 'hi'
          ? 'नमस्ते! मैं स्वास्थ्य AI सहायक हूँ। स्वास्थ्य केंद्र स्टॉक, मांग पूर्वानुमान, प्रारंभिक चेतावनियों या पुनर्वितरण के बारे में पूछें।'
          : 'Hello! I am the Swasthya AI Assistant. Ask me about medicine inventory, stockout risks, demand forecasts, or cross-district redistribution options.',
      timestamp: new Date().toISOString(),
      sources_used: ['Inventory Telemetry', 'Risk Engine']
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [activeEvidence, setActiveEvidence] = useState<{ evidence?: Record<string, any>; sources?: string[] } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (!isOpen) return null;

  const handleSend = async (textToSend?: string) => {
    const queryText = (textToSend || input).trim();
    if (!queryText || loading) return;

    const userMsg: CopilotMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await copilotApi.chat(
        queryText,
        'floating-session-01',
        language,
        user.role,
        user.id
      );

      const assistantMsg: CopilotMessage = {
        id: `resp-${Date.now()}`,
        sender: 'assistant',
        text: res.response || res.response_en || res.response_hi || 'Operational data retrieved successfully.',
        language: res.language as any,
        evidence: res.evidence,
        sources_used: res.sources_used || res.tools_called,
        isSimulation: res.is_simulation,
        timestamp: new Date().toISOString()
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: CopilotMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: err.message || 'Unable to connect to Copilot reasoning service. Please retry.',
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetConversation = () => {
    setMessages([
      {
        id: `init-${Date.now()}`,
        sender: 'assistant',
        text:
          language === 'hi'
            ? 'सत्र रीसेट कर दिया गया है। नया प्रश्न पूछें।'
            : 'Conversation context reset. How can I assist you with operational logistics?',
        timestamp: new Date().toISOString()
      }
    ]);
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/20 backdrop-blur-sm animate-in fade-in">
        <div className="w-full max-w-lg h-full bg-command-900 border-l border-slate-200 shadow-2xl flex flex-col justify-between">
          {/* Top Bar */}
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-command-950/80">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-md text-white">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                  <span>Swasthya AI Assistant</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-100 text-blue-700 border border-blue-300">
                    AI ASSISTANT
                  </span>
                </h3>
                <p className="text-[11px] text-slate-500">Grounded Operations Intelligence</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleResetConversation}
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100"
                title="Reset Chat"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'assistant' && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white text-xs font-bold mt-1">
                    AI
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-blue-600 text-white font-medium rounded-tr-none shadow-md'
                      : 'bg-command-950 border border-slate-200 text-slate-700 rounded-tl-none space-y-2'
                  }`}
                >
                  {m.sender === 'assistant' ? (
                    <MarkdownMessage content={m.text} />
                  ) : (
                    <p className="whitespace-pre-wrap">{m.text}</p>
                  )}

                  {/* Grounded Evidence Badge & Button */}
                  {m.evidence && Object.keys(m.evidence).length > 0 && (
                    <div className="pt-2 border-t border-slate-200/80 flex items-center justify-between">
                      <div className="flex items-center gap-1 text-[10px] text-emerald-600 font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Verified Evidence</span>
                      </div>
                      <button
                        onClick={() =>
                          setActiveEvidence({ evidence: m.evidence, sources: m.sources_used })
                        }
                        className="text-[10px] text-blue-600 hover:text-blue-600 font-bold underline flex items-center gap-0.5"
                      >
                        <span>View Evidence</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </button>
                    </div>
                  )}
                </div>

                {m.sender === 'user' && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-200 text-slate-700 text-xs font-bold mt-1">
                    {user.avatar || '👤'}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start items-center">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white text-xs font-bold">
                  AI
                </div>
                <div className="p-3.5 rounded-2xl rounded-tl-none bg-command-950 border border-slate-200 text-xs text-slate-500 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-spin" />
                  <span>Executing grounded operational tools...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions Chips */}
          <div className="px-4 py-2 border-t border-slate-200/60 bg-command-950/40">
            <p className="text-[10px] uppercase font-bold text-slate-500 mb-1.5">Quick Prompts</p>
            <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(s)}
                  className="shrink-0 px-2.5 py-1 rounded-full bg-slate-50 hover:bg-slate-100 border border-slate-200/60 text-[11px] text-slate-600 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Input Footer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 border-t border-slate-200 bg-command-950 flex items-center gap-2"
          >
            <VoiceInput onTranscription={(t) => handleSend(t)} language={language} />

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t('copilot.placeholder')}
              className="flex-1 px-3.5 py-2.5 rounded-xl bg-command-900 border border-slate-200 text-xs text-slate-800 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Grounded Evidence Drawer Sub-modal */}
      <EvidenceDrawer
        isOpen={Boolean(activeEvidence)}
        onClose={() => setActiveEvidence(null)}
        evidence={activeEvidence?.evidence}
        sources={activeEvidence?.sources}
      />
    </>
  );
};
