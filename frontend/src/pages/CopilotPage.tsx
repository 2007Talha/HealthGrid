import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Sparkles,
  Send,
  ShieldCheck,
  RotateCcw,
  ExternalLink,
  Sliders,
  History,
  CheckCircle,
  Database
} from 'lucide-react';
import { copilotApi, ChatResponse } from '../api/copilot';
import { CopilotMessage } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { VoiceInput } from '../components/copilot/VoiceInput';
import { WhatIfPanel } from '../components/copilot/WhatIfPanel';
import { EvidenceDrawer } from '../components/copilot/EvidenceDrawer';

const SUGGESTIONS = [
  'Which PHCs are at highest medicine stock-out risk?',
  'Which districts have the most critical shortages?',
  'Why is PHC-BR-PAT-001 at risk?',
  'Which PHC can supply Paracetamol to PHC-BR-PAT-001?',
  'What is the current bed occupancy in Patna?',
  'Show today active emergency status.'
];

export const CopilotPage: React.FC = () => {
  const { language, t } = useLanguage();
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<'chat' | 'what-if' | 'audit'>('chat');
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
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [activeEvidence, setActiveEvidence] = useState<{ evidence?: Record<string, any>; sources?: string[] } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadAuditLogs = async () => {
    try {
      const res = await copilotApi.getAuditLog(50);
      setAuditLogs(res.audit_log || []);
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    if (activeTab === 'audit') {
      loadAuditLogs();
    }
  }, [activeTab]);

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
        'fullscreen-session-01',
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
        text: err.message || 'Unable to connect to AI Assistant reasoning service. Please retry.',
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-md text-white">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl flex items-center gap-2">
              <span>Swasthya AI Assistant</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-blue-100 text-blue-700 border border-blue-300">
                AI ASSISTANT GROUNDED
              </span>
            </h1>
            <p className="text-xs text-slate-500">
              Deterministic tool execution with verified natural language explanation and zero hallucination.
            </p>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex rounded-xl bg-command-950 border border-slate-200 p-1 text-xs">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-colors ${
              activeTab === 'chat' ? 'bg-blue-600 text-white' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            Conversational Agent
          </button>
          <button
            onClick={() => setActiveTab('what-if')}
            className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition-colors ${
              activeTab === 'what-if' ? 'bg-purple-600 text-white' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>What-If Sandbox</span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition-colors ${
              activeTab === 'audit' ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Audit Trail</span>
          </button>
        </div>
      </div>

      {/* Main Tab Views */}
      {activeTab === 'what-if' ? (
        <WhatIfPanel />
      ) : activeTab === 'audit' ? (
        <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Immutable Tool Invocation Audit Logs
          </h3>
          <div className="space-y-2">
            {auditLogs.length === 0 ? (
              <p className="text-xs text-slate-500 py-8 text-center">No tool invocations recorded yet in this session.</p>
            ) : (
              auditLogs.map((log, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex justify-between items-center text-xs">
                  <div>
                    <span className="font-mono font-bold text-blue-600">{log.tool_name}</span>
                    <p className="text-[11px] text-slate-500">User: {log.user_id} ({log.user_role})</p>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">{log.timestamp}</span>
                </div>
              ))
            )}
          </div>
        </div>
      ) : (
        <div className="h-[640px] rounded-2xl border border-slate-200 bg-command-900 shadow-xl flex flex-col justify-between overflow-hidden">
          {/* Message List */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m) => (
              <div key={m.id} className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.sender === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white text-xs font-bold mt-1 shadow-md">
                    AI
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed space-y-2.5 ${
                    m.sender === 'user'
                      ? 'bg-blue-600 text-white font-medium rounded-tr-none shadow-md'
                      : 'bg-command-950 border border-slate-200 text-slate-700 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>

                  {m.evidence && Object.keys(m.evidence).length > 0 && (
                    <div className="pt-2 border-t border-slate-200/80 flex items-center justify-between">
                      <div className="flex items-center gap-1 text-[10px] text-emerald-600 font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Verified Evidence Attached</span>
                      </div>
                      <button
                        onClick={() => setActiveEvidence({ evidence: m.evidence, sources: m.sources_used })}
                        className="text-[10px] text-blue-600 hover:text-blue-600 font-bold underline flex items-center gap-0.5"
                      >
                        <span>Inspect Evidence Sources</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </button>
                    </div>
                  )}
                </div>

                {m.sender === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600 text-xs font-bold mt-1 border border-slate-200">
                    {user.avatar || '👤'}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start items-center">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white text-xs font-bold">
                  AI
                </div>
                <div className="p-3.5 rounded-2xl rounded-tl-none bg-command-950 border border-slate-200 text-xs text-slate-500 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 text-blue-600 animate-spin" />
                  <span>Executing deterministic microservice tools...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div className="px-5 py-2.5 border-t border-slate-200 bg-command-950/40">
            <p className="text-[10px] uppercase font-bold text-slate-500 mb-1.5">Suggested Questions</p>
            <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(s)}
                  className="shrink-0 px-3 py-1 rounded-full bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-600 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
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
              placeholder="Ask AI Assistant about medicine stocks, forecasts, shortages, or redistribution..."
              className="flex-1 px-4 py-3 rounded-xl bg-command-900 border border-slate-200 text-xs text-slate-800 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

      {/* Grounded Evidence Drawer */}
      <EvidenceDrawer
        isOpen={Boolean(activeEvidence)}
        onClose={() => setActiveEvidence(null)}
        evidence={activeEvidence?.evidence}
        sources={activeEvidence?.sources}
      />
    </div>
  );
};
