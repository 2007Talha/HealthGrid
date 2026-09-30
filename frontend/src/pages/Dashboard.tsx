import React, { useState, useEffect } from 'react';
import {
  Building2,
  AlertTriangle,
  Pill,
  RefreshCw,
  ArrowRight,
  Play
} from 'lucide-react';
import { operationalApi } from '../api/operational';
import { facilitiesApi } from '../api/facilities';
import { alertsApi } from '../api/alerts';
import { emergenciesApi } from '../api/emergencies';
import { simulationApi } from '../api/simulation';
import { NationalKPIs, Facility, EarlyWarningAlert, EmergencyScenario } from '../types';
import { StatCard } from '../components/common/StatCard';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { IndiaMap } from '../components/map/IndiaMap';
import { BedOccupancyChart } from '../components/charts/BedOccupancyChart';
import { SkeletonCard, SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';

interface DashboardProps {
  onNavigate: (route: string, entityId?: string) => void;
  onOpenCopilot: () => void;
  onOpenWhatIf: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  onNavigate,
  onOpenCopilot,
  onOpenWhatIf
}) => {
  const { t } = useLanguage();
  const { user } = useAuth();

  const [kpis, setKpis] = useState<NationalKPIs | null>(null);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [alerts, setAlerts] = useState<EarlyWarningAlert[]>([]);
  const [emergencies, setEmergencies] = useState<EmergencyScenario[]>([]);
  const [bedStatus, setBedStatus] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [kpiRes, facRes, alertRes, emergRes, bedRes] = await Promise.all([
        operationalApi.getNationalKPIs().catch((e) => {
          console.error('KPI error:', e);
          return null;
        }),
        facilitiesApi.listFacilities().catch((e) => {
          console.error('Facilities error:', e);
          return [];
        }),
        alertsApi.listAlerts({ minSeverity: 'WARNING' }).catch((e) => {
          console.error('Alerts error:', e);
          return { total_active_alerts: 0, alerts: [] };
        }),
        emergenciesApi.listActiveEmergencies().catch((e) => {
          console.error('Emergencies error:', e);
          return [];
        }),
        operationalApi.getBedHistory(undefined, 14).catch((e) => {
          console.error('Beds error:', e);
          return { total_days: 0, bed_history: [] };
        })
      ]);

      if (kpiRes) setKpis(kpiRes);

      const alertsList = alertRes?.alerts || [];
      const criticalFacIds = new Set(
        alertsList.filter((a) => a.severity === 'CRITICAL').map((a) => a.facility_id)
      );
      const highFacIds = new Set(
        alertsList.filter((a) => a.severity === 'HIGH').map((a) => a.facility_id)
      );

      const enhancedFacs = (facRes || []).map((f) => {
        let risk: 'CRITICAL' | 'HIGH' | 'WARNING' | 'NORMAL' = 'NORMAL';
        if (criticalFacIds.has(f.facility_id)) risk = 'CRITICAL';
        else if (highFacIds.has(f.facility_id)) risk = 'HIGH';
        return { ...f, overall_risk: risk };
      });

      setFacilities(enhancedFacs);
      setAlerts(alertsList);
      setEmergencies(emergRes || []);
      setBedStatus((bedRes as any)?.bed_history || (bedRes as any)?.bed_status || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [user.role]);

  const handleStepDay = async () => {
    try {
      await simulationApi.stepForward();
      await loadDashboardData();
    } catch (e: any) {
      alert(`Simulation step failed: ${e.message}`);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
            Health Resource Command Center
          </h1>
          <p className="text-xs text-slate-500">
            Supply-chain monitoring, forecasting & redistribution intelligence
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('demo')}
            className="px-3 py-2 rounded-xl bg-risk-normal/15 hover:bg-risk-normal/25 text-risk-normal text-xs font-semibold flex items-center gap-1.5 transition-colors border border-risk-normal/25"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Guided Demo</span>
          </button>
          <button
            onClick={handleStepDay}
            className="px-3 py-2 rounded-xl border border-slate-200 hover:border-slate-300 text-slate-600 text-xs font-medium flex items-center gap-1.5 transition-colors"
            title="Advance operational day by +1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>{t('actions.step_day')}</span>
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadDashboardData} />}

      {/* 4 Primary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title={t('kpi.facilities_monitored')}
          value={kpis?.facilities_monitored ?? 33}
          subValue="3 States • 8 Districts"
          icon={Building2}
          onClick={() => onNavigate('facilities')}
          isLoading={loading}
        />
        <StatCard
          title={t('kpi.critical_alerts')}
          value={kpis?.critical_alerts ?? 0}
          subValue={`${kpis?.total_active_alerts ?? 0} active warnings`}
          icon={AlertTriangle}
          severity={kpis?.critical_alerts ? 'critical' : 'normal'}
          onClick={() => onNavigate('alerts')}
          isLoading={loading}
        />
        <StatCard
          title={t('kpi.medicine_shortages')}
          value={kpis?.medicine_shortages ?? 0}
          subValue="Projected < 7 Days DOSA"
          icon={Pill}
          severity={kpis?.medicine_shortages ? 'high' : 'normal'}
          onClick={() => onNavigate('medicines')}
          isLoading={loading}
        />
        <StatCard
          title={t('kpi.redistribution_opps')}
          value={kpis?.redistribution_opportunities ?? 0}
          subValue="Optimized transfers available"
          icon={RefreshCw}
          severity="info"
          onClick={() => onNavigate('redistribution')}
          isLoading={loading}
        />
      </div>

      {/* Main Grid: Map + Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map (2 cols) */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between p-3 rounded-2xl bg-command-900 border border-slate-200">
            <div>
              <h3 className="text-sm font-bold text-slate-700">
                Healthcare Grid Map
              </h3>
              <p className="text-xs text-slate-500">
                PHC & CHC status across monitored states
              </p>
            </div>
          </div>

          <IndiaMap
            facilities={facilities}
            filterRisk="ALL"
            filterState="ALL"
            onSelectFacility={(id) => onNavigate('facilities', id)}
            className="h-[480px]"
          />
        </div>

        {/* Active Alerts Panel (1 col) */}
        <div className="p-4 rounded-2xl border border-slate-200 bg-command-900 flex flex-col">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-risk-critical" />
              <h3 className="text-sm font-bold text-slate-700">
                Active Warnings
              </h3>
            </div>
            <button
              onClick={() => onNavigate('alerts')}
              className="text-xs text-primary hover:text-primary-hover font-medium"
            >
              View All ({alerts.length})
            </button>
          </div>

          <div className="space-y-2 flex-1 overflow-y-auto max-h-[420px]">
            {loading ? (
              <SkeletonCard rows={3} />
            ) : alerts.length === 0 ? (
              <div className="text-center py-10 text-xs text-slate-500">
                No active warnings
              </div>
            ) : (
              alerts.slice(0, 5).map((a) => (
                <div
                  key={a.alert_id}
                  onClick={() => onNavigate('alerts', a.alert_id)}
                  className="p-3 rounded-xl bg-command-950 border border-slate-200 hover:border-primary/40 cursor-pointer transition-colors space-y-1.5 group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold text-slate-700 text-xs group-hover:text-primary">
                      {a.facility_name}
                    </span>
                    <SeverityBadge severity={a.severity} size="sm" />
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-2">{a.recommended_action || (a as any).recommended_next_step || 'Review resource stock'}</p>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200">
                    <span>{a.resource_name}</span>
                    <span className="font-mono text-risk-critical">
                      {(a.days_until_breach != null && a.days_until_breach < 1) ? '< 1d' : `${(a.days_until_breach ?? 0).toFixed(1)}d`}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Lower Row: Bed Chart + Redistribution CTA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BedOccupancyChart data={bedStatus} title="Bed Occupancy Trend (14 Days)" />

        {/* Simplified Redistribution CTA */}
        <div className="p-5 rounded-2xl border border-slate-200 bg-command-900 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <RefreshCw className="w-4 h-4 text-risk-normal" />
              <h3 className="text-sm font-bold text-slate-700">
                Redistribution Opportunities
              </h3>
            </div>

            <div className="p-4 rounded-xl bg-command-950 border border-slate-200 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[11px] font-semibold uppercase text-risk-normal">Recommended Transfer</span>
                  <h4 className="text-sm font-semibold text-slate-800 mt-0.5">ORS Rehydration Salts</h4>
                  <p className="text-xs text-slate-500 mt-0.5">Danapur → Patna Sadar · 14.2 km</p>
                </div>
                <span className="px-2 py-1 rounded-md text-xs font-mono font-semibold bg-risk-normal/15 text-risk-normal border border-risk-normal/25">
                  +900 Units
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2 border-t border-slate-200">
                <div>
                  <span className="text-[11px] text-slate-500">ETA</span>
                  <p className="font-mono font-semibold text-slate-600">0.4 hrs</p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500">Distance</span>
                  <p className="font-mono font-semibold text-slate-600">14.2 km</p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500">Risk Impact</span>
                  <p className="font-semibold text-risk-normal">Critical → Low</p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => onNavigate('redistribution')}
            className="mt-4 w-full py-2.5 rounded-xl bg-primary/15 hover:bg-primary/25 text-primary text-xs font-semibold transition-colors flex items-center justify-center gap-1.5 border border-primary/25"
          >
            <span>View All Transfers</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
