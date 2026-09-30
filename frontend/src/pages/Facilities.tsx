import React, { useState, useEffect } from 'react';
import { Building2, Search, Filter, ArrowRight, Shield, Bed, Users } from 'lucide-react';
import { facilitiesApi } from '../api/facilities';
import { operationalApi } from '../api/operational';
import { Facility } from '../types';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { SkeletonTable } from '../components/common/SkeletonLoader';
import { ErrorBanner } from '../components/common/ErrorBanner';
import { EmptyState } from '../components/common/EmptyState';

interface FacilitiesPageProps {
  onSelectFacility: (facilityId: string) => void;
}

export const Facilities: React.FC<FacilitiesPageProps> = ({ onSelectFacility }) => {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const loadFacilities = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await facilitiesApi.listFacilities();
      setFacilities(res || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load health facilities.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFacilities();
  }, []);

  const states = Array.from(new Set(facilities.map((f) => f.state_name).filter(Boolean)));
  const types = Array.from(new Set(facilities.map((f) => f.facility_type).filter(Boolean)));

  const filtered = facilities.filter((f) => {
    if (stateFilter !== 'ALL' && f.state_name !== stateFilter && f.state_code !== stateFilter) return false;
    if (typeFilter !== 'ALL' && f.facility_type !== typeFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        f.facility_name.toLowerCase().includes(q) ||
        f.facility_id.toLowerCase().includes(q) ||
        f.district_name.toLowerCase().includes(q)
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
            <Building2 className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">
              Healthcare Facility Directory (PHCs & CHCs)
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Real-time infrastructure capacity, doctor/nurse attendance, and inventory coverage.
          </p>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-950 text-blue-600 border border-blue-600/40">
          33 Official Verified Facilities
        </span>
      </div>

      {error && <ErrorBanner message={error} onRetry={loadFacilities} />}

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl border border-slate-200 bg-command-900/80 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search PHC name, district, or ID (e.g. Patna Sadar, PHC-BR-PAT-001)..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-800 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* State Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-semibold whitespace-nowrap">State:</span>
          <select
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none"
          >
            <option value="ALL">All States</option>
            {states.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {/* Type Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-semibold whitespace-nowrap">Facility Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Types</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Facilities Table */}
      {loading ? (
        <SkeletonTable rows={8} cols={6} />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No facilities found"
          description="Try modifying your search or removing filter restrictions."
        />
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-command-900 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-command-950/80 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="p-4">Facility Name & ID</th>
                  <th className="p-4">Location</th>
                  <th className="p-4">Type</th>
                  <th className="p-4 text-center">Sanctioned Beds</th>
                  <th className="p-4 text-center">Coordinates</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filtered.map((f) => (
                  <tr
                    key={f.facility_id}
                    onClick={() => onSelectFacility(f.facility_id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors group"
                  >
                    <td className="p-4">
                      <div className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
                        {f.facility_name}
                      </div>
                      <div className="text-[11px] font-mono text-slate-500">{f.facility_id}</div>
                    </td>
                    <td className="p-4 text-slate-600">
                      <div>{f.district_name}</div>
                      <div className="text-[11px] text-slate-500">{f.state_name} ({f.state_code})</div>
                    </td>
                    <td className="p-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                        {f.facility_type}
                      </span>
                    </td>
                    <td className="p-4 text-center font-mono font-bold text-slate-800">
                      {f.sanctioned_beds || 6}
                    </td>
                    <td className="p-4 text-center font-mono text-[11px] text-slate-500">
                      {f.latitude?.toFixed(3)}, {f.longitude?.toFixed(3)}
                    </td>
                    <td className="p-4 text-right">
                      <button className="px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary font-bold text-xs transition-all flex items-center gap-1 ml-auto">
                        <span>Command</span>
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
