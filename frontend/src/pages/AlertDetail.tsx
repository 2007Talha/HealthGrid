import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  ShieldCheck,
  Sparkles,
  RefreshCw,
  Building2,
  Calendar,
  CheckCircle,
  TrendingDown,
  Database
} from 'lucide-react';
import { alertsApi } from '../api/alerts';
import { EarlyWarningAlert } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonCard } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { useLanguage } from '../context/LanguageContext';

interface AlertDetailProps {
  alertId: string;
  onBack: () => void;
  onNavigateRedistribution: (target?: string) => void;
}

export const AlertDetail: React.FC<AlertDetailProps> = ({
  alertId,
  onBack,
  onNavigateRedistribution
}) => {
  const { language, t } = useLanguage();
  const [alert, setAlert] = useState<EarlyWarningAlert | null>(null);
  const [geminiExplanation, setGeminiExplanation] = useState<{
    explanation_en: string;
    explanation_hi: string;
    evidence: Record<string, any>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [explaining, setExplaining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAlertDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await alertsApi.getAlertById(alertId);
      setAlert(res);

      // Automatically trigger grounded Gemini explanation
      setExplaining(true);
      const aiRes = await alertsApi.explainAlertWithGemini(alertId, language);
      setGeminiExplanation(aiRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load alert details.');
    } finally {
      setLoading(false);
      setExplaining(false);
    }
  };

  useEffect(() => {
    loadAlertDetails();
  }, [alertId, language]);

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-5xl mx-auto">
      {/* Back Button and Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="p-2 rounded-xl bg-command-900 border border-slate-200 hover:border-slate-200 text-slate-600 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-lg sm:text-xl font-bold text-slate-900 flex items-center gap-2">
            <span>Early Warning Alert Breakdown</span>
            <span className="font-mono text-xs text-slate-500">({alertId})</span>
          </h1>
          <p className="text-xs text-slate-500">Root-cause investigation and grounded predictive evidence</p>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadAlertDetails} />}

      {loading ? (
        <SkeletonCard rows={5} />
      ) : alert ? (
        <div className="space-y-6">
          {/* Main Alert Card */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  {alert.alert_type.replace(/_/g, ' ')}
                </span>
                <h2 className="text-xl font-extrabold text-slate-800">{alert.facility_name}</h2>
                <p className="text-xs text-slate-500">
                  {alert.district}, {alert.state} • Facility ID: <span className="font-mono text-slate-600">{alert.facility_id}</span>
                </p>
              </div>
              <SeverityBadge severity={alert.severity} size="lg" />
            </div>

            {/* Metric KPI Pillows */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">Target Resource</span>
                <p className="text-sm font-bold text-slate-800 mt-0.5">{alert.resource_name}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">Current Balance</span>
                <p className="text-sm font-mono font-bold text-slate-700 mt-0.5">
                  {alert.current_value} units
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">Estimated Runway</span>
                <p
                  className={`text-sm font-mono font-bold mt-0.5 ${
                    (alert.days_until_breach ?? 0) < 2 ? 'text-red-600' : 'text-amber-600'
                  }`}
                >
                  {(alert.days_until_breach ?? 0) < 1 ? '< 1 Day' : `${(alert.days_until_breach ?? 0).toFixed(1)} Days`}
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200">
                <span className="text-[10px] uppercase font-bold text-slate-500">ML Confidence</span>
                <p className="text-sm font-mono font-bold text-blue-600 mt-0.5">
                  {Math.round((alert.model_confidence ?? 0) * 100)}%
                </p>
              </div>
            </div>

            {/* Recommended Action Box */}
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs space-y-1.5">
              <h4 className="font-bold text-blue-600 uppercase tracking-wide text-[11px]">
                Recommended Clinical Action
              </h4>
              <p className="text-slate-700 leading-relaxed">{alert.recommended_action || (alert as any).recommended_next_step || ''}</p>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => onNavigateRedistribution(alert ? `${alert.facility_id}:${alert.resource_id}` : undefined)}
                className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-2 transition-colors shadow-md shadow-emerald-200/50"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Launch Cross-District Redistribution</span>
              </button>
            </div>
          </div>

          {/* Grounded AI Reasoning Section */}
          <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white">
                  <Sparkles className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                    <span>Why Am I Seeing This? (Grounded AI Reasoning)</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-100 text-blue-700 border border-blue-300">
                      AI VERIFIED
                    </span>
                  </h3>
                  <p className="text-[11px] text-slate-500">Synthesized directly from verified healthcare telemetry facts</p>
                </div>
              </div>
            </div>

            {explaining ? (
              <div className="py-6 text-center text-xs text-slate-500 space-y-2">
                <Sparkles className="w-5 h-5 text-blue-600 animate-spin mx-auto" />
                <p>Generating evidence-grounded explanation with AI...</p>
              </div>
            ) : geminiExplanation ? (
              <div className="space-y-4">
                <p className="text-xs text-slate-700 leading-relaxed p-4 rounded-xl bg-slate-50 border border-slate-200 font-normal">
                  {language === 'hi'
                    ? geminiExplanation.explanation_hi
                    : geminiExplanation.explanation_en}
                </p>

                {/* Grounded Evidence Breakdown */}
                {geminiExplanation.evidence && (
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      Extracted Analytical Factors
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      {Object.entries(geminiExplanation.evidence).map(([k, v]) => (
                        <div key={k} className="p-2.5 rounded-lg bg-command-900 border border-slate-200">
                          <span className="text-slate-500 capitalize block text-[10px]">
                            {k.replace(/_/g, ' ')}
                          </span>
                          <strong className="text-slate-800 font-mono text-xs">
                            {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                          </strong>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">No explanation available.</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
