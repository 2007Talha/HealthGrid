import React, { useState, useEffect } from 'react';
import {
  Pill,
  ArrowLeft,
  RefreshCw,
  Truck,
  TrendingUp,
  Building2,
  Calendar,
  ExternalLink,
  ShieldCheck
} from 'lucide-react';
import { forecastsApi } from '../api/forecasts';
import { operationalApi } from '../api/operational';
import { ForecastItem, InventoryRecord, DeliveryRecord } from '../types';
import { ForecastLineChart } from '../components/charts/ForecastLineChart';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonCard } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';

interface MedicineDetailProps {
  medicineCode: string;
  onBack: () => void;
  onNavigateRedistribution: () => void;
}

export const MedicineDetail: React.FC<MedicineDetailProps> = ({
  medicineCode,
  onBack,
  onNavigateRedistribution
}) => {
  const [forecasts, setForecasts] = useState<ForecastItem[]>([]);
  const [deliveries, setDeliveries] = useState<DeliveryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch 14-day forecast for primary facility and deliveries
      const [fRes, delRes] = await Promise.all([
        forecastsApi.getMedicineForecast('PHC-BR-PAT-001', medicineCode, 14).catch(() => ({ forecasts: [] })),
        operationalApi.getDeliveries(undefined, false).catch(() => ({ deliveries: [] }))
      ]);

      setForecasts(fRes.forecasts || []);
      setDeliveries(
        (delRes.deliveries || []).filter((d: DeliveryRecord) => d.medicine_code === medicineCode)
      );
    } catch (err: any) {
      setError(err.message || 'Failed to load medicine forecast.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [medicineCode]);

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-command-900 border border-slate-200 hover:border-slate-200 text-slate-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <span>Essential Medicine Telemetry</span>
              <span className="font-mono text-xs text-blue-600">({medicineCode})</span>
            </h1>
            <p className="text-xs text-slate-500">
              Multi-day machine learning demand forecast & national supply-chain in-transit tracking
            </p>
          </div>
        </div>

        <button
          onClick={onNavigateRedistribution}
          className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-emerald-200/50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Launch Redistribution Optimization</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadData} />}

      {/* 14-Day ML Demand Forecast Chart */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-600" />
            14-Day ML Demand Forecast (Ridge & LightGBM Multi-Horizon)
          </h3>
          <span className="text-[10px] font-mono text-slate-500">
            Model Version: <strong>Ridge-TimeSeries-v1.4</strong>
          </span>
        </div>

        {loading ? (
          <SkeletonCard rows={4} />
        ) : (
          <ForecastLineChart
            data={forecasts}
            title="Projected Daily Consumption Demand (Units)"
            unit="Units"
            height={340}
          />
        )}
      </div>

      {/* In-Transit Deliveries & Logistics Section */}
      <div className="p-5 rounded-2xl border border-slate-200 bg-command-900 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center gap-2">
            <Truck className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Active Supply Chain Deliveries ({medicineCode})
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {deliveries.length} Shipments Tracked
          </span>
        </div>

        {deliveries.length === 0 ? (
          <div className="text-center py-6 text-xs text-slate-500">
            No scheduled or in-transit delivery shipments found for {medicineCode}.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {deliveries.map((del) => (
              <div
                key={del.delivery_id}
                className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-slate-700">{del.delivery_id}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      del.status === 'IN_TRANSIT'
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                    }`}
                  >
                    {del.status}
                  </span>
                </div>
                <div className="space-y-1 text-slate-600">
                  <p>
                    <strong className="text-slate-500">Destination:</strong> {del.facility_name || del.phc_id}
                  </p>
                  <p>
                    <strong className="text-slate-500">Units:</strong> {((del as any).quantity ?? del.units ?? 0).toLocaleString()}
                  </p>
                  <p>
                    <strong className="text-slate-500">Expected ETA:</strong> {del.expected_arrival_date || 'Scheduled'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
