import React, { useState, useEffect } from 'react';
import {
  Building2,
  ArrowLeft,
  Pill,
  Bed,
  Users,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import { facilitiesApi } from '../api/facilities';
import { operationalApi } from '../api/operational';
import { alertsApi } from '../api/alerts';
import { Facility, InventoryRecord, BedStatus, StaffingStatus, EarlyWarningAlert } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonCard, SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { InventoryTrendChart } from '../components/charts/InventoryTrendChart';
import { BedOccupancyChart } from '../components/charts/BedOccupancyChart';

interface FacilityDetailProps {
  facilityId: string;
  onBack: () => void;
  onNavigateRedistribution: () => void;
  onOpenWhatIf: () => void;
}

export const FacilityDetail: React.FC<FacilityDetailProps> = ({
  facilityId,
  onBack,
  onNavigateRedistribution,
  onOpenWhatIf
}) => {
  const [facility, setFacility] = useState<Facility | null>(null);
  const [inventory, setInventory] = useState<InventoryRecord[]>([]);
  const [beds, setBeds] = useState<BedStatus[]>([]);
  const [staffing, setStaffing] = useState<StaffingStatus[]>([]);
  const [alerts, setAlerts] = useState<EarlyWarningAlert[]>([]);

  const [activeTab, setActiveTab] = useState<'inventory' | 'beds' | 'staff' | 'alerts'>('inventory');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFacilityData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [facRes, invRes, bedRes, staffRes, alertRes] = await Promise.all([
        facilitiesApi.getFacilityById(facilityId),
        operationalApi.getPHCInventory(facilityId).catch(() => ({ inventory: [] })),
        operationalApi.getBedStatus(facilityId).catch(() => ({ bed_status: [] })),
        operationalApi.getStaffingStatus(facilityId).catch(() => ({ staffing_status: [] })),
        alertsApi.listAlerts({ facilityId }).catch(() => ({ alerts: [] }))
      ]);

      setFacility(facRes);
      setInventory(invRes.inventory || []);
      setBeds(bedRes.bed_status || []);
      setStaffing(staffRes.staffing_status || []);
      setAlerts(alertRes.alerts || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load facility telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFacilityData();
  }, [facilityId]);

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-command-900 border border-slate-200 shadow-xl">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-command-950 border border-slate-200 hover:border-slate-200 text-slate-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-extrabold text-slate-900">{facility?.facility_name || facilityId}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-100 text-blue-700 border border-blue-300">
                {facility?.facility_type || 'PHC'}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              {facility?.district_name}, {facility?.state_name} • ID: <span className="font-mono text-slate-600">{facilityId}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenWhatIf}
            className="px-3.5 py-2 rounded-xl bg-purple-100 hover:bg-purple-200 border border-purple-300 text-purple-700 text-xs font-bold flex items-center gap-1.5 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-700" />
            <span>Simulate What-If Surge</span>
          </button>

          <button
            onClick={onNavigateRedistribution}
            className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-emerald-200/50"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Request Redistribution</span>
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadFacilityData} />}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-4 text-xs font-bold">
        {[
          { id: 'inventory', label: 'Medicine Inventory & DOSA', icon: Pill, count: inventory.length },
          { id: 'beds', label: 'Bed Telemetry', icon: Bed, count: beds.length },
          { id: 'staff', label: 'Workforce Attendance', icon: Users, count: staffing.length },
          { id: 'alerts', label: 'Active Alerts', icon: AlertTriangle, count: alerts.length }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`pb-3 flex items-center gap-2 border-b-2 transition-all ${
                isActive
                  ? 'border-blue-500 text-blue-600 font-extrabold'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-100 text-slate-500 border border-slate-200">
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {loading ? (
        <SkeletonTable rows={6} cols={5} />
      ) : activeTab === 'inventory' ? (
        <div className="space-y-6">
          <InventoryTrendChart
            data={inventory.slice(0, 14)}
            title={`Telemetry Stock Levels — ${facility?.facility_name || facilityId}`}
          />

          <div className="rounded-2xl border border-slate-200 bg-command-900 overflow-hidden shadow-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-command-950 text-[11px] uppercase text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="p-4">Medicine Code</th>
                  <th className="p-4 text-right">Current Stock</th>
                  <th className="p-4 text-right">Daily Burn</th>
                  <th className="p-4 text-right">Safety Stock</th>
                  <th className="p-4 text-right">Runway (DOSA)</th>
                  <th className="p-4 text-center">Stock-Out Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {inventory.map((item) => (
                  <tr key={item.medicine_code} className="hover:bg-slate-50">
                    <td className="p-4 font-mono font-bold text-slate-700">{item.medicine_code}</td>
                    <td className="p-4 text-right font-mono text-slate-800">
                      {item.current_stock || item.closing_stock || 0}
                    </td>
                    <td className="p-4 text-right font-mono text-slate-500">{item.daily_consumption}</td>
                    <td className="p-4 text-right font-mono text-slate-500">{item.safety_stock}</td>
                    <td className="p-4 text-right font-mono font-bold">
                      <span
                        className={
                          item.days_of_stock_available < 3
                            ? 'text-red-600'
                            : item.days_of_stock_available < 7
                            ? 'text-amber-600'
                            : 'text-emerald-600'
                        }
                      >
                        {(item.days_of_stock_available ?? 0).toFixed(1)} days
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      {item.days_of_stock_available < 3 ? (
                        <SeverityBadge severity="CRITICAL" size="sm" />
                      ) : item.days_of_stock_available < 7 ? (
                        <SeverityBadge severity="HIGH" size="sm" />
                      ) : (
                        <SeverityBadge severity="NORMAL" size="sm" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'beds' ? (
        <div className="space-y-6">
          <BedOccupancyChart data={beds} />
        </div>
      ) : activeTab === 'staff' ? (
        <div className="rounded-2xl border border-slate-200 bg-command-900 p-4">
          <h4 className="text-xs font-bold text-slate-600 uppercase mb-3">Workforce Attendance History</h4>
          <div className="space-y-2">
            {staffing.map((s, i) => (
              <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex justify-between text-xs">
                <span className="font-mono text-slate-500">{s.record_date}</span>
                <span className="text-slate-700">
                  Doctors: <strong>{s.doctors_present}/{s.doctors_scheduled}</strong>
                </span>
                <span className="text-slate-700">
                  Nurses: <strong>{s.nurses_present}/{s.nurses_scheduled}</strong>
                </span>
                <span className={s.doctor_shortage ? 'text-red-600 font-bold' : 'text-emerald-600'}>
                  {s.doctor_shortage ? 'Doctor Shortage' : 'Adequate'}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500 rounded-xl border border-slate-200 bg-command-900/40">
              No active alerts for this facility.
            </div>
          ) : (
            alerts.map((a) => (
              <div key={a.alert_id} className="p-4 rounded-xl bg-command-900 border border-slate-200 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-red-600 text-xs">{a.resource_name}</span>
                  <SeverityBadge severity={a.severity} size="sm" />
                </div>
                <p className="text-xs text-slate-600">{a.recommended_action}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
