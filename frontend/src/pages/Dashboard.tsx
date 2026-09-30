import React, { useState, useEffect } from 'react';
import {
  Building2,
  AlertTriangle,
  Pill,
  RefreshCw,
  ArrowRight,
  Play,
  Radio,
  Zap,
  CloudSun
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

  // Live telemetry & real-time weather state
  const [liveWeather, setLiveWeather] = useState<any[]>([]);
  const [isLiveStreaming, setIsLiveStreaming] = useState(true);
  const [isHarvesting, setIsHarvesting] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  const loadWeather = async () => {
    try {
      const res = await operationalApi.getLiveWeather();
      if (res?.districts) {
        setLiveWeather(res.districts);
      }
    } catch (e) {
      console.warn('Live weather poll:', e);
    }
  };

  const loadDashboardData = async (showLoadingState = true) => {
    try {
      if (showLoadingState) setLoading(true);
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
      if (showLoadingState) setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData(true);
    loadWeather();
  }, [user.role]);

  // Real-time automatic polling loop (15s)
  useEffect(() => {
    if (!isLiveStreaming) return;
    const interval = setInterval(() => {
      loadDashboardData(false);
      loadWeather();
    }, 15000);
    return () => clearInterval(interval);
  }, [isLiveStreaming]);

  const handleStepDay = async () => {
    try {
      await simulationApi.stepForward();
      await loadDashboardData(true);
    } catch (e: any) {
      alert(`Simulation step failed: ${e.message}`);
    }
  };

  const handleHarvestWeather = async () => {
    try {
      setIsHarvesting(true);
      await operationalApi.harvestLiveWeather();
      await loadWeather();
      await loadDashboardData(false);
    } catch (e: any) {
      alert(`Weather harvest failed: ${e.message}`);
    } finally {
      setIsHarvesting(false);
    }
  };

  const handleSimulateLiveDispense = async () => {
    try {
      setIsIngesting(true);
      const res = await operationalApi.ingestTelemetry({
        facility_id: 'PHC-BR-PAT-001',
        medicine_code: 'MED-PCM-500',
        quantity_dispensed: 35,
        source_system: 'PHC_TABLET_DISPENSER'
      });
      await loadDashboardData(false);
      alert(
        `✓ Real-Time Ingestion Success!\n\n` +
        `Source: PHC-BR-PAT-001 Tablet Dispenser\n` +
        `Medicine: Paracetamol 500mg\n` +
        `Dispensed: 35 units\n` +
        `New Current Stock: ${res.telemetry_update.new_current_stock} units\n` +
        `New Stock Runway: ${res.telemetry_update.new_days_of_stock} days\n` +
        `Risk Status: ${res.telemetry_update.new_risk_level}`
      );
    } catch (e: any) {
      alert(`Ingestion failed: ${e.message}`);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-5 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
            Health Resource Command Center
          </h1>
          <p className="text-xs text-slate-500">
            Supply-chain monitoring, real-time telemetry, forecasting & redistribution intelligence
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onNavigate('demo')}
            className="px-3 py-2 rounded-xl bg-risk-normal/15 hover:bg-risk-normal/25 text-risk-normal text-xs font-semibold flex items-center gap-1.5 transition-colors border border-risk-normal/25 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Guided Demo</span>
          </button>
          <button
            onClick={handleStepDay}
            className="px-3 py-2 rounded-xl bg-white border border-slate-200 hover:border-slate-300 text-slate-700 text-xs font-medium flex items-center gap-1.5 transition-colors shadow-2xs cursor-pointer"
            title="Advance operational day by +1"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('actions.step_day')}</span>
          </button>
        </div>
      </div>

      {/* Live Telemetry Stream & Open-Meteo Meteorological Weather Ticker */}
      <div className="p-3.5 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 overflow-x-auto py-0.5">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-800 font-bold border border-emerald-200 shrink-0">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isLiveStreaming ? 'bg-emerald-400 opacity-75' : 'bg-slate-400 opacity-0'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isLiveStreaming ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
            </span>
            <span className="text-[11px] uppercase tracking-wide">
              {isLiveStreaming ? 'LIVE TELEMETRY STREAM' : 'STREAM PAUSED'}
            </span>
          </div>

          {liveWeather.length > 0 ? (
            liveWeather.map((w, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 shrink-0 font-mono text-[11px]"
              >
                <CloudSun className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                <span className="font-bold text-slate-900 font-sans">{w.district_name}:</span>
                <span>{w.current_temperature_c}°C</span>
                <span className="text-slate-300">|</span>
                <span>{w.current_humidity_pct}% hum</span>
                <span className="text-slate-300">|</span>
                <span className={w.current_precipitation_mm_hr > 0 ? 'text-blue-600 font-bold' : 'text-slate-500'}>
                  {w.daily_precipitation_sum_mm}mm rain
                </span>
                {w.flood_risk_level !== 'LOW' && (
                  <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-rose-100 text-rose-700 border border-rose-300 uppercase">
                    Flood Alert
                  </span>
                )}
              </div>
            ))
          ) : (
            <span className="text-slate-500 font-mono text-[11px] py-1">
              Synchronizing Open-Meteo real-time climate telemetry...
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button
            onClick={handleSimulateLiveDispense}
            disabled={isIngesting}
            className="px-3 py-1.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs flex items-center gap-1.5 border border-blue-200 transition-colors shadow-2xs cursor-pointer disabled:opacity-50"
            title="Simulates real-time consumption event from a remote Primary Health Centre tablet dispenser"
          >
            <Zap className={`w-3.5 h-3.5 text-blue-600 ${isIngesting ? 'animate-bounce' : ''}`} />
            <span>{isIngesting ? 'Ingesting...' : '+ Ingest Dispense Event'}</span>
          </button>

          <button
            onClick={handleHarvestWeather}
            disabled={isHarvesting}
            className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-xs flex items-center gap-1.5 border border-slate-200 transition-colors shadow-2xs cursor-pointer disabled:opacity-50"
            title="Pull latest live weather from Open-Meteo"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isHarvesting ? 'animate-spin' : ''}`} />
            <span>Sync Climate</span>
          </button>

          <button
            onClick={() => setIsLiveStreaming(!isLiveStreaming)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 border transition-all cursor-pointer ${
              isLiveStreaming
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300 shadow-2xs'
                : 'bg-slate-100 text-slate-600 border-slate-200'
            }`}
          >
            <Radio className="w-3.5 h-3.5" />
            <span>{isLiveStreaming ? 'Auto-Sync (15s)' : 'Auto-Sync (Off)'}</span>
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
