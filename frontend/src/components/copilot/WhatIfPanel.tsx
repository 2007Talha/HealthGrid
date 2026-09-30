import React, { useState } from 'react';
import { Play, RotateCcw, AlertTriangle, ArrowRight, ShieldAlert, Sparkles } from 'lucide-react';
import { copilotApi, WhatIfResponse } from '../../api/copilot';
import { SeverityBadge } from '../common/SeverityBadge';

interface WhatIfPanelProps {
  initialFacilityId?: string;
  initialMedicineCode?: string;
  onClose?: () => void;
}

export const WhatIfPanel: React.FC<WhatIfPanelProps> = ({
  initialFacilityId = 'PHC-BR-PAT-001',
  initialMedicineCode = 'MED-PCM-500',
  onClose
}) => {
  const [facilityId, setFacilityId] = useState(initialFacilityId);
  const [medicineCode, setMedicineCode] = useState(initialMedicineCode);
  const [demandSurgePct, setDemandSurgePct] = useState<number>(30);
  const [deliveryDelayDays, setDeliveryDelayDays] = useState<number>(0);
  const [transferUnits, setTransferUnits] = useState<number>(0);
  const [result, setResult] = useState<WhatIfResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    try {
      setLoading(true);
      const res = await copilotApi.runWhatIf({
        facility_id: facilityId,
        medicine_code: medicineCode,
        demand_surge_pct: demandSurgePct,
        delivery_delay_days: deliveryDelayDays,
        transfer_units: transferUnits
      });
      setResult(res);
    } catch (e: any) {
      alert(e.message || 'What-If simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDemandSurgePct(30);
    setDeliveryDelayDays(0);
    setTransferUnits(0);
    setResult(null);
  };

  return (
    <div className="p-5 rounded-2xl border border-indigo-900/60 bg-command-900 shadow-2xl space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-950/80 border border-purple-200 text-purple-600">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">What-If Shadow Simulator</h3>
            <span className="text-[10px] font-mono text-purple-600 uppercase font-bold tracking-wider">
              [ISOLATED SIMULATION — ZERO PRODUCTION IMPACT]
            </span>
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-xs text-slate-500 hover:text-slate-900">
            Close
          </button>
        )}
      </div>

      {/* Target Selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase mb-1">Target PHC Facility</label>
          <select
            value={facilityId}
            onChange={(e) => setFacilityId(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-purple-500"
          >
            <option value="PHC-BR-PAT-001">PHC-BR-PAT-001 (Patna Sadar)</option>
            <option value="PHC-BR-PAT-002">PHC-BR-PAT-002 (Danapur PHC)</option>
            <option value="PHC-UP-VAR-001">PHC-UP-VAR-001 (Varanasi Cantt)</option>
            <option value="PHC-MH-PUN-001">PHC-MH-PUN-001 (Haveli PHC)</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-bold text-slate-500 uppercase mb-1">Essential Medicine</label>
          <select
            value={medicineCode}
            onChange={(e) => setMedicineCode(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-command-950 border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-purple-500"
          >
            <option value="MED-PCM-500">Paracetamol 500mg (MED-PCM-500)</option>
            <option value="MED-ORS-SFT">ORS Sachet (MED-ORS-SFT)</option>
            <option value="MED-AMX-500">Amoxicillin 500mg (MED-AMX-500)</option>
            <option value="MED-IVF-NS500">Normal Saline IV (MED-IVF-NS500)</option>
          </select>
        </div>
      </div>

      {/* Scenario Sliders */}
      <div className="space-y-4 pt-2">
        {/* Demand Surge Slider */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-600">Hypothetical Demand Surge:</span>
            <span className="font-mono font-bold text-purple-600">+{demandSurgePct}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="150"
            step="10"
            value={demandSurgePct}
            onChange={(e) => setDemandSurgePct(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>0%</span>
            <span>+30% (Standard Surge)</span>
            <span>+50% (Outbreak)</span>
            <span>+100% (Emergency)</span>
          </div>
        </div>

        {/* Shipment Delay Slider */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-600">Transit Supply Delay:</span>
            <span className="font-mono font-bold text-amber-600">+{deliveryDelayDays} Days</span>
          </div>
          <input
            type="range"
            min="0"
            max="14"
            step="1"
            value={deliveryDelayDays}
            onChange={(e) => setDeliveryDelayDays(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
        </div>

        {/* Hypothetical Incoming Transfer Slider */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="font-semibold text-slate-600">Simulated Incoming Transfer:</span>
            <span className="font-mono font-bold text-emerald-600">+{transferUnits} Units</span>
          </div>
          <input
            type="range"
            min="0"
            max="2000"
            step="100"
            value={transferUnits}
            onChange={(e) => setTransferUnits(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 pt-2">
        <button
          onClick={handleSimulate}
          disabled={loading}
          className="flex-1 py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-200/50 transition-colors"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{loading ? 'Evaluating Scenario...' : 'Run Shadow Simulation'}</span>
        </button>
        <button
          onClick={handleReset}
          className="py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-200"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Result Comparison Card */}
      {result && (
        <div className="p-4 rounded-xl bg-slate-50 border border-purple-200 space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2">
            <span className="text-xs font-bold text-purple-600 uppercase">Impact Assessment</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-100 text-purple-700 border border-purple-300">
              SIMULATION DATA
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-center">
            {/* Baseline */}
            <div className="p-3 rounded-lg bg-command-900 border border-slate-200 space-y-1">
              <p className="text-[10px] uppercase font-bold text-slate-500">Baseline Actual</p>
              <div className="flex justify-center my-1">
                <SeverityBadge severity={result.baseline.risk} size="sm" />
              </div>
              <p className="text-xs text-slate-600 font-mono">
                Stock: <strong>{result.baseline.stock}</strong> units
              </p>
              <p className="text-[11px] text-slate-500 font-mono">
                Runway: <strong>{(result.baseline.dosa ?? 0).toFixed(1)}</strong> days
              </p>
            </div>

            {/* Simulated */}
            <div className="p-3 rounded-lg bg-command-900 border border-purple-200 space-y-1">
              <p className="text-[10px] uppercase font-bold text-purple-600">Simulated Scenario</p>
              <div className="flex justify-center my-1">
                <SeverityBadge severity={result.simulated.risk} size="sm" />
              </div>
              <p className="text-xs text-slate-600 font-mono">
                Stock: <strong>{result.simulated.stock}</strong> units
              </p>
              <p className="text-[11px] text-slate-500 font-mono">
                Runway: <strong>{(result.simulated.dosa ?? 0).toFixed(1)}</strong> days
              </p>
            </div>
          </div>

          <p className="text-xs text-slate-600 p-2.5 rounded-lg bg-slate-50 border border-slate-200 leading-relaxed">
            {result.impact_summary}
          </p>
        </div>
      )}
    </div>
  );
};
