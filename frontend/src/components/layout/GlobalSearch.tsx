import React, { useState, useEffect } from 'react';
import { Search, X, Building2, Pill, AlertTriangle, ArrowRight } from 'lucide-react';
import { facilitiesApi } from '../../api/facilities';
import { operationalApi } from '../../api/operational';
import { alertsApi } from '../../api/alerts';
import { Facility, MedicineSummary, EarlyWarningAlert } from '../../types';

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectFacility: (id: string) => void;
  onSelectMedicine: (code: string) => void;
  onSelectAlert: (id: string) => void;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  isOpen,
  onClose,
  onSelectFacility,
  onSelectMedicine,
  onSelectAlert
}) => {
  const [query, setQuery] = useState('');
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [medicines, setMedicines] = useState<MedicineSummary[]>([]);
  const [alerts, setAlerts] = useState<EarlyWarningAlert[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      Promise.all([
        facilitiesApi.listFacilities().catch(() => []),
        operationalApi.getMedicinesSummary().then(r => r.medicines).catch(() => []),
        alertsApi.listAlerts().then(r => r.alerts).catch(() => [])
      ]).then(([facs, meds, alts]) => {
        setFacilities(facs);
        setMedicines(meds);
        setAlerts(alts);
        setLoading(false);
      });
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        isOpen ? onClose() : undefined;
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const q = query.toLowerCase().trim();

  const filteredFacilities = q
    ? facilities.filter(
        (f) =>
          f.facility_name.toLowerCase().includes(q) ||
          f.facility_id.toLowerCase().includes(q) ||
          f.district_name.toLowerCase().includes(q) ||
          f.state_name.toLowerCase().includes(q)
      ).slice(0, 5)
    : [];

  const filteredMedicines = q
    ? medicines.filter(
        (m) =>
          m.medicine_name.toLowerCase().includes(q) ||
          m.medicine_code.toLowerCase().includes(q) ||
          m.therapeutic_category.toLowerCase().includes(q)
      ).slice(0, 5)
    : [];

  const filteredAlerts = q
    ? alerts.filter(
        (a) =>
          a.facility_name.toLowerCase().includes(q) ||
          a.resource_name.toLowerCase().includes(q) ||
          a.recommended_action.toLowerCase().includes(q)
      ).slice(0, 5)
    : [];

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/20 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-xl border border-command-700 bg-command-900 shadow-2xl overflow-hidden flex flex-col">
        {/* Search Input */}
        <div className="flex items-center px-4 py-3 border-b border-command-700 gap-3">
          <Search className="w-5 h-5 text-primary shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search facilities, medicines, alerts..."
            className="w-full bg-transparent text-sm text-slate-800 placeholder-slate-500 focus:outline-none"
          />
          {query && (
            <button onClick={() => setQuery('')} className="p-1 text-slate-500 hover:text-slate-900">
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="px-2 py-1 text-xs rounded bg-command-800 text-slate-500 hover:text-slate-900"
          >
            ESC
          </button>
        </div>

        {/* Results */}
        <div className="max-h-96 overflow-y-auto p-4 space-y-4">
          {loading ? (
            <p className="text-sm text-slate-500 text-center py-6">Loading...</p>
          ) : !q ? (
            <div className="text-center py-8 text-sm text-slate-500 space-y-2">
              <p>Search across 33 facilities, 20 medicines, and alerts</p>
              <div className="flex justify-center gap-2 pt-2">
                <span className="px-2 py-1 rounded bg-command-800 text-slate-600 text-xs">PHC-BR-PAT-001</span>
                <span className="px-2 py-1 rounded bg-command-800 text-slate-600 text-xs">Paracetamol</span>
                <span className="px-2 py-1 rounded bg-command-800 text-slate-600 text-xs">Patna</span>
              </div>
            </div>
          ) : (
            <>
              {filteredFacilities.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-primary" /> Facilities
                  </h5>
                  <div className="space-y-1">
                    {filteredFacilities.map((f) => (
                      <button
                        key={f.facility_id}
                        onClick={() => {
                          onSelectFacility(f.facility_id);
                          onClose();
                        }}
                        className="w-full text-left p-2.5 rounded-lg bg-command-850 hover:bg-command-800 border border-command-700 hover:border-primary/40 flex items-center justify-between text-sm transition-colors group"
                      >
                        <div>
                          <span className="font-medium text-slate-800">{f.facility_name}</span>
                          <span className="text-xs text-slate-500 ml-2">({f.facility_id})</span>
                          <p className="text-xs text-slate-500">{f.district_name}, {f.state_name}</p>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-primary" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {filteredMedicines.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <Pill className="w-3.5 h-3.5 text-risk-normal" /> Medicines
                  </h5>
                  <div className="space-y-1">
                    {filteredMedicines.map((m) => (
                      <button
                        key={m.medicine_code}
                        onClick={() => {
                          onSelectMedicine(m.medicine_code);
                          onClose();
                        }}
                        className="w-full text-left p-2.5 rounded-lg bg-command-850 hover:bg-command-800 border border-command-700 hover:border-risk-normal/40 flex items-center justify-between text-sm transition-colors group"
                      >
                        <div>
                          <span className="font-medium text-slate-800">{m.medicine_name}</span>
                          <span className="text-xs text-slate-500 ml-2">({m.medicine_code})</span>
                          <p className="text-xs text-slate-500">{m.therapeutic_category} · {m.strength}</p>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-risk-normal" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {filteredAlerts.length > 0 && (
                <div>
                  <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-risk-critical" /> Warnings
                  </h5>
                  <div className="space-y-1">
                    {filteredAlerts.map((a) => (
                      <button
                        key={a.alert_id}
                        onClick={() => {
                          onSelectAlert(a.alert_id);
                          onClose();
                        }}
                        className="w-full text-left p-2.5 rounded-lg bg-command-850 hover:bg-command-800 border border-command-700 hover:border-risk-critical/40 flex items-center justify-between text-sm transition-colors group"
                      >
                        <div>
                          <span className="font-medium text-risk-critical">{a.facility_name}: {a.resource_name}</span>
                          <p className="text-xs text-slate-500">{a.recommended_action}</p>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-risk-critical" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {filteredFacilities.length === 0 && filteredMedicines.length === 0 && filteredAlerts.length === 0 && (
                <p className="text-sm text-slate-500 text-center py-6">No results for "{query}"</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
