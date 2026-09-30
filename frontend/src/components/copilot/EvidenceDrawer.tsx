import React from 'react';
import { ShieldCheck, Database, CheckCircle, FileText, X } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  evidence?: Record<string, any>;
  sources?: string[];
  title?: string;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  isOpen,
  onClose,
  evidence,
  sources = ['Inventory Telemetry', 'ML Forecast Engine', 'Stock-Out Risk Engine', 'Logistics Delivery Service'],
  title = 'Verified Evidence Sources'
}) => {
  const { t } = useLanguage();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/20 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-lg h-full bg-command-900 border-l border-slate-200 shadow-2xl p-6 overflow-y-auto flex flex-col justify-between">
        <div className="space-y-5">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-200 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-blue-950/80 border border-blue-500/40 text-blue-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-800">{title}</h3>
                <p className="text-[11px] text-slate-500">Deterministic backend facts & grounded metrics</p>
              </div>
            </div>
            <button onClick={onClose} className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-800">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Sources Used Checklist */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
              Microservices & Pipeline Sources
            </h4>
            <div className="grid grid-cols-1 gap-2">
              {sources.map((src, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 p-2.5 rounded-lg bg-slate-100/60 border border-slate-200 text-xs text-slate-700"
                >
                  <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="font-medium">{src}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Evidence Data Key-Values */}
          {evidence && Object.keys(evidence).length > 0 && (
            <div className="space-y-2">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Extracted Grounded Telemetry
              </h4>
              <div className="rounded-xl border border-slate-200 bg-slate-100/80 p-4 space-y-2.5 max-h-80 overflow-y-auto font-mono text-xs">
                {Object.entries(evidence).map(([key, val]) => (
                  <div key={key} className="flex items-start justify-between border-b border-slate-200/60 pb-1.5 gap-4">
                    <span className="text-slate-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                    <span className="text-slate-700 font-bold text-right">
                      {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Non-Hallucination Disclaimer */}
          <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-[11px] text-blue-600 space-y-1">
            <p className="font-bold flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" /> Zero-Hallucination Guardrail
            </p>
            <p className="text-slate-500">
              All statistical counts, inventory balances, and transit ETAs shown are computed by deterministic backend solvers. The AI Assistant synthesizes natural language and citations without altering underlying numerical truth.
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full mt-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-700 font-semibold text-xs transition-colors"
        >
          Close Evidence Panel
        </button>
      </div>
    </div>
  );
};
