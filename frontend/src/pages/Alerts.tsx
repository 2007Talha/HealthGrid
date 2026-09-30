import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Search,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { alertsApi } from '../api/alerts';
import { EarlyWarningAlert } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { EmptyState } from '../components/common/EmptyState';
import { useLanguage } from '../context/LanguageContext';

interface AlertsPageProps {
  onSelectAlert: (id: string) => void;
  onOpenCopilot: () => void;
}

export const Alerts: React.FC<AlertsPageProps> = ({ onSelectAlert, onOpenCopilot }) => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<EarlyWarningAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await alertsApi.listAlerts({ minSeverity: 'WARNING' });
      setAlerts(res.alerts || []);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve early warning alerts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const filteredAlerts = alerts.filter((a) => {
    if (severityFilter !== 'ALL' && a.severity !== severityFilter) return false;
    if (typeFilter !== 'ALL' && a.alert_type !== typeFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        a.facility_name.toLowerCase().includes(q) ||
        a.facility_id.toLowerCase().includes(q) ||
        a.resource_name.toLowerCase().includes(q) ||
        a.district.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-risk-warning" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
              Early Warning Alerts
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Proactive indicators for stockouts, bed surges, and staffing shortages
          </p>
        </div>
        <button
          onClick={onOpenCopilot}
          className="px-3 py-2 rounded-xl bg-primary/15 hover:bg-primary/25 text-primary text-xs font-semibold flex items-center gap-1.5 transition-colors border border-primary/25"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ask AI Assistant</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadAlerts} />}

      {/* Filters */}
      <div className="p-4 rounded-2xl border border-slate-200 bg-command-900/80 flex flex-col md:flex-row items-stretch md:items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search facility, medicine, or district..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-800 placeholder-slate-500 focus:outline-none focus:border-primary"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none"
        >
          <option value="ALL">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="WARNING">Warning</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none"
        >
          <option value="ALL">All Types</option>
          <option value="MEDICINE_STOCKOUT_RISK">Medicine Stock-Out</option>
          <option value="BED_CAPACITY_RISK">Bed Overflow</option>
          <option value="STAFF_SHORTAGE_RISK">Staffing Shortage</option>
        </select>
      </div>

      {/* Alerts Grid */}
      {loading ? (
        <SkeletonTable rows={6} cols={4} />
      ) : filteredAlerts.length === 0 ? (
        <EmptyState
          title="No alerts match the selected criteria"
          description="Try changing the severity or search filters."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.alert_id}
              onClick={() => onSelectAlert(alert.alert_id)}
              className="p-5 rounded-2xl border border-slate-200 bg-command-900 hover:border-primary/40 cursor-pointer transition-all flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-800 group-hover:text-primary transition-colors">
                      {alert.facility_name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {alert.district}, {alert.state} · <span className="font-mono">{alert.facility_id}</span>
                    </p>
                  </div>
                  <SeverityBadge severity={alert.severity} size="sm" />
                </div>

                <div className="p-3 rounded-xl bg-command-950 border border-slate-200 space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Resource:</span>
                    <span className="font-medium text-slate-700">{alert.resource_name}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Days Until Breach:</span>
                    <span
                      className={`font-mono font-semibold ${
                        (alert.days_until_breach ?? 0) < 2 ? 'text-risk-critical' : 'text-risk-warning'
                      }`}
                    >
                      {(alert.days_until_breach ?? 0) < 1 ? '< 1 Day' : `${(alert.days_until_breach ?? 0).toFixed(1)} Days`}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-500 leading-relaxed">
                  {alert.recommended_action || alert.recommended_next_step || ''}
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-200 text-xs">
                <span className="font-mono text-slate-500">
                  Confidence: {Math.round(alert.model_confidence * 100)}%
                </span>
                <span className="text-primary group-hover:text-primary-hover font-medium flex items-center gap-1">
                  View Details
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
