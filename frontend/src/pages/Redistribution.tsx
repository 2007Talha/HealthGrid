import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  Truck,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  RotateCcw,
  Info
} from 'lucide-react';
import { redistributionApi } from '../api/redistribution';
import {
  RedistributionShortage,
  RedistributionRecommendation,
  SimulationAudit
} from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { RouteVisualizer } from '../components/map/RouteVisualizer';
import { SkeletonCard, SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';

interface RedistributionProps {
  targetShortage?: string | null;
}

export const Redistribution: React.FC<RedistributionProps> = ({ targetShortage }) => {
  const [shortages, setShortages] = useState<RedistributionShortage[]>([]);
  const [selectedShortage, setSelectedShortage] = useState<RedistributionShortage | null>(null);
  const [recommendation, setRecommendation] = useState<RedistributionRecommendation | null>(null);
  const [simAudit, setSimAudit] = useState<SimulationAudit | null>(null);
  const [history, setHistory] = useState<SimulationAudit[]>([]);

  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadShortages = async () => {
    try {
      setLoading(true);
      setError(null);
      const [shortRes, histRes] = await Promise.all([
        redistributionApi.getShortages(),
        redistributionApi.getSimulationHistory().catch(() => ({ history: [] }))
      ]);

      const rawItems = shortRes.shortages || [];
      const items: RedistributionShortage[] = rawItems.map((s: any) => ({
        ...s,
        phc_id: s.phc_id || s.facility_id || s.destination_id || '',
        facility_name: s.facility_name || 'Health Facility',
        district: s.district || s.district_name || 'District',
        state: s.state || s.state_name || 'State',
        medicine_code: s.medicine_code || '',
        medicine_name: s.medicine_name || s.medicine_code || 'Medicine',
        current_stock: s.current_stock ?? 0,
        daily_consumption: s.daily_consumption ?? s.average_daily_predicted_demand ?? 1,
        days_of_stock_available: s.days_of_stock_available ?? 0,
        safety_stock: s.safety_stock ?? s.safety_stock_threshold ?? 50,
        shortage_units: s.shortage_units ?? s.net_deficit_quantity ?? 0,
        urgency: (s.urgency || s.risk_level || ((s.days_of_stock_available ?? 0) < 3.0 ? 'CRITICAL' : 'HIGH')) as any,
      }));

      setShortages(items);
      setHistory(histRes.history || []);

      let initial: RedistributionShortage | null = null;
      if (targetShortage) {
        const parts = targetShortage.split(':');
        const facId = parts[0];
        const medCode = parts[1];
        initial = items.find((s) => s.phc_id === facId && (!medCode || s.medicine_code === medCode)) ||
                  items.find((s) => s.phc_id === facId) || null;
      }
      if (!initial && items.length > 0) {
        initial = items[0];
      }

      if (initial && initial.phc_id && initial.medicine_code) {
        setSelectedShortage(initial);
        // Automatically optimize recommendation for the target/first shortage
        handleOptimize(initial.phc_id, initial.medicine_code);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load shortage records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadShortages();
  }, [targetShortage]);

  const handleOptimize = async (destId: string, medCode: string) => {
    if (!destId || !medCode) return;
    try {
      setOptimizing(true);
      setSimAudit(null);
      const rec = await redistributionApi.generateRecommendation(destId, medCode, 2);
      setRecommendation(rec);
    } catch (err: any) {
      alert(`Optimization solver error: ${err.message}`);
    } finally {
      setOptimizing(false);
    }
  };

  const handleSimulate = async () => {
    if (!recommendation) return;
    try {
      setSimulating(true);
      const audit = await redistributionApi.simulateTransfer(
        recommendation.recommendation_id,
        recommendation
      );
      setSimAudit(audit);
      const histRes = await redistributionApi.getSimulationHistory();
      setHistory(histRes.history || []);
    } catch (err: any) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setSimulating(false);
    }
  };

  const handleResetAllSimulations = async () => {
    try {
      await redistributionApi.resetSimulations();
      setSimAudit(null);
      setRecommendation(null);
      await loadShortages();
    } catch (err: any) {
      alert(`Reset error: ${err.message}`);
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-emerald-600" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
              Cross-District Resource Redistribution Center
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Google OR-Tools CBC MILP multi-source rebalancing solver & digital twin simulator.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleResetAllSimulations}
            className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-200"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset All Simulations</span>
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadShortages} />}

      {/* Main 2-Column Split: Shortages Table on Left, Optimizer & Map on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Shortages List */}
        <div className="p-4 rounded-2xl border border-slate-200 bg-command-900 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Active Facility Shortages ({shortages.length})
            </span>
          </div>

          <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {loading ? (
              <SkeletonCard rows={3} />
            ) : shortages.length === 0 ? (
              <div className="text-center py-12 text-xs text-slate-500">
                No active critical shortages detected across facilities.
              </div>
            ) : (
              shortages.map((s) => {
                const isSelected =
                  selectedShortage?.phc_id === s.phc_id &&
                  selectedShortage?.medicine_code === s.medicine_code;

                return (
                  <div
                    key={`${s.phc_id}-${s.medicine_code}`}
                    onClick={() => {
                      setSelectedShortage(s);
                      handleOptimize(s.phc_id, s.medicine_code);
                    }}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-2 ${
                      isSelected
                        ? 'border-emerald-400 bg-emerald-50 shadow-md shadow-emerald-100'
                        : 'border-slate-200 bg-slate-50 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="text-xs font-bold text-slate-800">{s.facility_name}</h4>
                        <span className="text-[10px] font-mono text-slate-500">
                          {s.district}, {s.state}
                        </span>
                      </div>
                      <SeverityBadge severity={s.urgency} size="sm" />
                    </div>

                    <div className="p-2 rounded-lg bg-command-950 border border-slate-200/80 flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-600 font-bold">{s.medicine_name}</span>
                      <span className="text-red-600 font-bold">-{s.shortage_units} units</span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span>Stock: {s.current_stock}</span>
                      <span>Runway: {(s.days_of_stock_available ?? 0).toFixed(1)}d</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: OR-Tools Optimization Recommendation & Transfer Visualizer */}
        <div className="lg:col-span-2 space-y-4">
          {optimizing ? (
            <div className="p-12 rounded-2xl border border-slate-200 bg-command-900 text-center space-y-3">
              <Sparkles className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
              <h4 className="text-sm font-bold text-slate-700">
                Running Google OR-Tools CBC MILP Rebalancing Optimization...
              </h4>
              <p className="text-xs text-slate-500">
                Evaluating candidate donor facilities, distance matrix, and safety thresholds.
              </p>
            </div>
          ) : recommendation ? (
            <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-5">
              {/* Header */}
              {(() => {
                const recAny = recommendation as any;
                const medName = recommendation.medicine_name || recAny.resource?.medicine_name || 'Essential Medicine';
                const destName = recommendation.destination_name || recAny.destination?.facility_name || 'Destination PHC';
                const deficitUnits = recommendation.deficit_units ?? recAny.destination?.net_deficit ?? 0;
                const fulfillmentPct = recommendation.fulfillment_rate_pct ?? recAny.fulfillment_percentage ?? 100;
                const riskBefore = recommendation.risk_before ?? recAny.destination?.risk_level_before ?? 'CRITICAL';
                const riskAfter = recommendation.projected_risk_after ?? recAny.projected_impact?.risk_level_after ?? 'SAFE';
                const rawSources = (recommendation.sources && recommendation.sources.length > 0)
                  ? recommendation.sources
                  : (recAny.transfers?.map((t: any) => ({
                      source_id: t.source_facility_id,
                      source_name: t.source_facility_name,
                      transfer_units: t.transfer_quantity,
                      distance_km: t.distance_km,
                      travel_time_hours: t.duration_hours,
                      safe_surplus_remaining: Math.max(0, (t.source_surplus_before || 0) - t.transfer_quantity)
                    })) || []);

                return (
                  <>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
                      <div>
                        <span className="text-[10px] font-mono uppercase font-bold text-emerald-600">
                          Optimal Decision Support Plan
                        </span>
                        <h3 className="text-lg font-extrabold text-slate-900">
                          {medName} Transfer to {destName}
                        </h3>
                        <p className="text-xs text-slate-500">
                          Deficit: <strong className="text-red-600">{deficitUnits} units</strong> • Fulfillment: <strong className="text-emerald-600">{fulfillmentPct}%</strong>
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-700 border border-emerald-300">
                          Status: {recommendation.status}
                        </span>
                      </div>
                    </div>

                    {/* Interactive Route Map */}
                    <RouteVisualizer recommendation={recommendation} />

                    {/* Source Allocations Breakdown */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                        Donor Facilities Allocation
                      </h4>
                      <div className="space-y-2">
                        {rawSources.map((src: any) => (
                          <div
                            key={src.source_id}
                            className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                          >
                            <div>
                              <span className="font-bold text-slate-700">{src.source_name}</span>
                              <p className="text-[10px] text-slate-500">
                                Distance: {Number(src.distance_km || 0).toFixed(1)} km • Safe Surplus Left: {src.safe_surplus_remaining ?? 0} units
                              </p>
                            </div>

                            <div className="flex items-center gap-3">
                              <span className="font-mono text-cyan-600">ETA: {Number(src.travel_time_hours || 0).toFixed(1)}h</span>
                              <span className="px-2.5 py-1 rounded-lg font-mono font-bold bg-emerald-100 text-emerald-700 border border-emerald-300">
                                +{src.transfer_units} units
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Prototype Simulation Disclaimer Box */}
                    <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-200 flex items-start gap-2.5">
                      <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                      <p className="leading-relaxed text-[11px] text-slate-600">
                        <strong>Prototype Simulation Disclaimer:</strong> Approving this transfer applies the relocation to the real-time operational Digital Twin without executing physical shipment. Baseline inventory remains safely restorable.
                      </p>
                    </div>

                    {/* Simulation Approval Trigger */}
                    <div className="flex items-center justify-between pt-2">
                      <div className="text-xs text-slate-500">
                        Projected Risk: <strong className="text-red-600">{riskBefore}</strong> &rarr; <strong className="text-emerald-600">{riskAfter}</strong>
                      </div>

                      <button
                        onClick={handleSimulate}
                        disabled={simulating}
                        className="py-2.5 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-200/50 transition-all active:scale-98"
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span>{simulating ? 'Applying Digital Twin Update...' : 'Approve & Simulate Transfer'}</span>
                      </button>
                    </div>

                    {/* Simulation Result Audit Box */}
                    {simAudit && (() => {
                      const sAny = simAudit as any;
                      const unitsDispatched = simAudit.total_units_transferred ?? sAny.transfer?.total_quantity ?? 0;
                      const dosaBefore = Number(simAudit.dosa_before ?? sAny.before?.days_of_stock_available ?? 0);
                      const dosaAfter = Number(simAudit.dosa_after ?? sAny.after?.days_of_stock_available ?? 0);
                      const rBefore = simAudit.risk_before ?? sAny.before?.risk_level ?? 'CRITICAL';
                      const rAfter = simAudit.risk_after ?? sAny.after?.risk_level ?? 'SAFE';
                      const timeStr = simAudit.timestamp || sAny.simulated_at || 'Just now';

                      return (
                        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-3 animate-in fade-in">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-emerald-600 uppercase flex items-center gap-1.5">
                              <ShieldCheck className="w-4 h-4 text-emerald-600" /> Digital Twin Simulation Applied
                            </span>
                            <span className="text-[10px] font-mono text-emerald-600">{timeStr}</span>
                          </div>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
                            <div className="p-2 rounded bg-slate-50">
                              <span className="text-[10px] text-slate-500">Units Dispatched</span>
                              <p className="font-mono font-bold text-slate-800">{unitsDispatched}</p>
                            </div>
                            <div className="p-2 rounded bg-slate-50">
                              <span className="text-[10px] text-slate-500">Runway Before</span>
                              <p className="font-mono font-bold text-red-600">{dosaBefore.toFixed(1)}d</p>
                            </div>
                            <div className="p-2 rounded bg-slate-50">
                              <span className="text-[10px] text-slate-500">Runway After</span>
                              <p className="font-mono font-bold text-emerald-600">{dosaAfter.toFixed(1)}d</p>
                            </div>
                            <div className="p-2 rounded bg-slate-50">
                              <span className="text-[10px] text-slate-500">Risk Mitigation</span>
                              <p className="font-bold text-emerald-600">{rBefore} &rarr; {rAfter}</p>
                            </div>
                          </div>
                        </div>
                      );
                    })()}
                  </>
                );
              })()}
            </div>
          ) : (
            <div className="p-12 rounded-2xl border border-slate-200 bg-command-900 text-center text-xs text-slate-500">
              Select a shortage from the list to compute an optimal redistribution plan.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
