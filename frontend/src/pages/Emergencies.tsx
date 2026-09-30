import React, { useState, useEffect } from 'react';
import { Flame, AlertTriangle, Play, RotateCcw, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { emergenciesApi } from '../api/emergencies';
import { EmergencyScenario } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonCard } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';

export const Emergencies: React.FC = () => {
  const [activeEmergencies, setActiveEmergencies] = useState<EmergencyScenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [eventType, setEventType] = useState('MONSOON_FLOOD_SURGE');
  const [district, setDistrict] = useState('IN-BR-PAT');
  const [multiplier, setMultiplier] = useState(1.4);
  const [severity, setSeverity] = useState('CRITICAL');
  const [duration, setDuration] = useState(7);

  const loadEmergencies = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await emergenciesApi.listActiveEmergencies();
      setActiveEmergencies(res || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load active emergencies.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmergencies();
  }, []);

  const handleTrigger = async () => {
    try {
      setTriggering(true);
      await emergenciesApi.triggerEmergency({
        event_type: eventType,
        affected_district_ids: [district],
        demand_multiplier: multiplier,
        severity: severity,
        duration_days: duration
      });
      await loadEmergencies();
    } catch (err: any) {
      alert(`Trigger failed: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  const handleClear = async (scenarioId?: string) => {
    try {
      await emergenciesApi.clearEmergency(scenarioId);
      await loadEmergencies();
    } catch (err: any) {
      alert(`Clear failed: ${err.message}`);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
              Healthcare Emergency & Surge Management
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Inject, test, and manage disaster multipliers across healthcare sectors.
          </p>
        </div>

        {activeEmergencies.length > 0 && (
          <button
            onClick={() => handleClear()}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-200"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Clear All Active Emergencies</span>
          </button>
        )}
      </div>

      {error && <ErrorBanner message={error} onRetry={loadEmergencies} />}

      {/* Main Grid: Active Emergencies vs Emergency Injector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Emergency Scenarios */}
        <div className="p-5 rounded-2xl border border-slate-200 bg-command-900 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-orange-400" /> Active Emergency Scenarios ({activeEmergencies.length})
            </h3>
          </div>

          {loading ? (
            <SkeletonCard rows={3} />
          ) : activeEmergencies.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 rounded-xl border border-dashed border-slate-200">
              No active emergency shocks. Use the scenario injector on the right to simulate a crisis.
            </div>
          ) : (
            <div className="space-y-3">
              {activeEmergencies.map((em) => (
                <div
                  key={em.scenario_id}
                  className="p-4 rounded-xl bg-orange-50 border border-orange-200 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-slate-800">{em.event_type}</h4>
                      <p className="text-xs text-slate-500">
                        Affected Districts: <strong className="text-orange-600 font-mono">{em.affected_district_ids?.join(', ')}</strong>
                      </p>
                    </div>
                    <SeverityBadge severity={em.severity} size="sm" />
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs pt-1 border-t border-slate-200">
                    <div>
                      <span className="text-[10px] text-slate-500">Demand Multiplier</span>
                      <p className="font-mono font-bold text-orange-600">{em.demand_multiplier}x</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500">Duration</span>
                      <p className="font-mono text-slate-700">{em.duration_days} Days</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500">Facilities Impacted</span>
                      <p className="font-mono text-slate-700">{em.facilities_impacted_count || 'All PHCs'}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleClear(em.scenario_id)}
                    className="w-full py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-600 transition-colors"
                  >
                    Clear Scenario
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Emergency Scenario Injector Panel */}
        <div className="p-5 rounded-2xl border border-slate-200 bg-command-900 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-orange-700">
              Admin Emergency Scenario Injector
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-orange-100 text-orange-700 border border-orange-300">
              CONTROL PANEL
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase text-slate-500 mb-1">
                Disaster / Outbreak Event Type
              </label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-orange-500"
              >
                <option value="MONSOON_FLOOD_SURGE">Monsoon Floods (ORS + Antibiotics Surge)</option>
                <option value="DENGUE_OUTBREAK">Dengue Epidemic (IV Saline + Paracetamol)</option>
                <option value="HEATWAVE_MASS_CASUALTY">Heatwave Emergency (IV Fluids + Beds Surge)</option>
                <option value="VIRAL_FEVER_SURGE">Seasonal Viral Fever Cluster</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">
                  Target District
                </label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-orange-500"
                >
                  <option value="IN-BR-PAT">Patna District (Bihar)</option>
                  <option value="IN-UP-VAR">Varanasi District (UP)</option>
                  <option value="IN-MH-PUN">Pune District (Maharashtra)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-slate-500 mb-1">
                  Severity Level
                </label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-orange-500"
                >
                  <option value="CRITICAL">CRITICAL (Red Alert)</option>
                  <option value="HIGH">HIGH (Amber Alert)</option>
                  <option value="WARNING">WARNING (Yellow Alert)</option>
                </select>
              </div>
            </div>

            {/* Multiplier Slider */}
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-slate-600">Daily Demand Multiplier:</span>
                <span className="font-mono font-bold text-orange-600">{multiplier}x (+{Math.round((multiplier - 1) * 100)}%)</span>
              </div>
              <input
                type="range"
                min="1.1"
                max="2.0"
                step="0.1"
                value={multiplier}
                onChange={(e) => setMultiplier(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
              />
            </div>

            <button
              onClick={handleTrigger}
              disabled={triggering}
              className="w-full py-3 rounded-xl bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-orange-200/50 transition-all active:scale-98"
            >
              <Flame className="w-4 h-4 fill-white" />
              <span>{triggering ? 'Applying Multipliers...' : 'Trigger Emergency Scenario'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
