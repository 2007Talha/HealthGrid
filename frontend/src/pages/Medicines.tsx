import React, { useState, useEffect } from 'react';
import { Pill, Search, ArrowRight } from 'lucide-react';
import { operationalApi } from '../api/operational';
import { MedicineSummary } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { EmptyState } from '../components/common/EmptyState';
import { useLanguage } from '../context/LanguageContext';

interface MedicinesPageProps {
  onSelectMedicine: (medicineCode: string) => void;
}

export const Medicines: React.FC<MedicinesPageProps> = ({ onSelectMedicine }) => {
  const { t } = useLanguage();
  const [medicines, setMedicines] = useState<MedicineSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const loadMedicines = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await operationalApi.getMedicinesSummary();
      setMedicines(res.medicines || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load medicine inventory summary.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMedicines();
  }, []);

  const categories = Array.from(new Set(medicines.map((m) => m.therapeutic_category).filter(Boolean)));

  const filteredMedicines = medicines.filter((m) => {
    if (categoryFilter !== 'ALL' && m.therapeutic_category !== categoryFilter) return false;
    if (riskFilter !== 'ALL' && m.risk_level !== riskFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        m.medicine_name.toLowerCase().includes(q) ||
        m.medicine_code.toLowerCase().includes(q) ||
        m.therapeutic_category.toLowerCase().includes(q)
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
            <Pill className="w-5 h-5 text-primary" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
              Essential Medicines
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            National stock telemetry, burn rates, and stockout risk (NLEM 2022)
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-100 text-blue-700 border border-blue-300">
          20 Medicines Monitored
        </span>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadMedicines} />}

      {/* Filters */}
      <div className="p-4 rounded-2xl border border-slate-200 bg-command-900/80 flex flex-col md:flex-row items-stretch md:items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name or code (e.g., Paracetamol, MED-PCM-500)..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-800 placeholder-slate-500 focus:outline-none focus:border-primary"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none max-w-[200px]"
        >
          <option value="ALL">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none"
        >
          <option value="ALL">All Levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="WARNING">Warning</option>
          <option value="NORMAL">Normal</option>
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : filteredMedicines.length === 0 ? (
        <EmptyState
          title="No medicines found"
          description="Try broadening your search or removing filters."
        />
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-command-900 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-command-950/80 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="p-4">Medicine</th>
                  <th className="p-4">Category</th>
                  <th className="p-4 text-right">Stock</th>
                  <th className="p-4 text-right">Daily Burn</th>
                  <th className="p-4 text-right">Runway</th>
                  <th className="p-4 text-center">Shortages</th>
                  <th className="p-4 text-center">Status</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredMedicines.map((m) => (
                  <tr
                    key={m.medicine_code}
                    onClick={() => onSelectMedicine(m.medicine_code)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors group"
                  >
                    <td className="p-4">
                      <div className="font-medium text-slate-800 group-hover:text-primary transition-colors">
                        {m.medicine_name}
                      </div>
                      <div className="text-xs font-mono text-slate-500 mt-0.5">
                        {m.medicine_code} · {m.strength} · {m.dosage_form}
                      </div>
                    </td>
                    <td className="p-4 text-slate-500">{m.therapeutic_category}</td>
                    <td className="p-4 text-right font-mono font-medium text-slate-700">
                      {(m.total_national_stock ?? 0).toLocaleString()}
                    </td>
                    <td className="p-4 text-right font-mono text-slate-500">
                      {(m.national_daily_consumption ?? 0).toLocaleString()} / day
                    </td>
                    <td className="p-4 text-right font-mono font-medium">
                      <span
                        className={
                          (m.national_dosa ?? 0) < 7
                            ? 'text-risk-critical'
                            : (m.national_dosa ?? 0) < 14
                            ? 'text-risk-warning'
                            : 'text-risk-normal'
                        }
                      >
                        {(m.national_dosa ?? 0).toFixed(1)}d
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      {m.facilities_with_shortage > 0 ? (
                        <span className="px-2 py-0.5 rounded text-xs font-mono font-medium bg-risk-critical/15 text-risk-critical border border-risk-critical/20">
                          {m.facilities_with_shortage} PHCs
                        </span>
                      ) : (
                        <span className="text-slate-500 font-mono">0</span>
                      )}
                    </td>
                    <td className="p-4 text-center">
                      <SeverityBadge severity={m.risk_level} size="sm" />
                    </td>
                    <td className="p-4 text-right">
                      <button className="px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary font-medium text-xs transition-colors flex items-center gap-1 ml-auto">
                        <span>Forecast</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
