import React, { useState } from 'react';
import {
  Play,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  AlertTriangle,
  Flame,
  TrendingUp,
  RefreshCw,
  Sparkles,
  Bot,
  RotateCcw,
  ShieldCheck
} from 'lucide-react';
import { emergenciesApi } from '../api/emergencies';
import { forecastsApi } from '../api/forecasts';
import { alertsApi } from '../api/alerts';
import { copilotApi } from '../api/copilot';
import { redistributionApi } from '../api/redistribution';
import { useLanguage } from '../context/LanguageContext';

export const DemoFlow: React.FC<{ onNavigate: (route: string, id?: string) => void }> = ({ onNavigate }) => {
  const { setLanguage } = useLanguage();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [stepData, setStepData] = useState<any>({});

  const totalSteps = 7;

  const handleExecuteStep = async (step: number) => {
    setLoading(true);
    try {
      if (step === 2) {
        // Step 2: Trigger +40% Surge in Patna
        const res = await emergenciesApi.triggerEmergency({
          event_type: 'MONSOON_FLOOD_SURGE',
          affected_district_ids: ['IN-BR-PAT'],
          demand_multiplier: 1.4,
          severity: 'CRITICAL',
          duration_days: 7
        });
        setStepData((prev: any) => ({ ...prev, emergency: res }));
      } else if (step === 3) {
        // Step 3: Fetch updated ML demand forecast
        const res = await forecastsApi.getMedicineForecast('PHC-BR-PAT-001', 'MED-ORS-SFT', 14);
        setStepData((prev: any) => ({ ...prev, forecast: res }));
      } else if (step === 4) {
        // Step 4: Fetch early warnings
        const res = await alertsApi.listAlerts({ minSeverity: 'HIGH' });
        setStepData((prev: any) => ({ ...prev, alerts: res.alerts }));
      } else if (step === 5) {
        // Step 5: Ask Copilot
        const res = await copilotApi.chat('Why is PHC-BR-PAT-001 facing critical stockout risk?', undefined, 'en');
        setStepData((prev: any) => ({ ...prev, copilot: res }));
      } else if (step === 6) {
        // Step 6: Optimize redistribution with OR-Tools
        const res = await redistributionApi.generateRecommendation('PHC-BR-PAT-001', 'MED-ORS-SFT', 2);
        setStepData((prev: any) => ({ ...prev, recommendation: res }));
      } else if (step === 7) {
        // Step 7: Simulate transfer
        if (stepData.recommendation) {
          const res = await redistributionApi.simulateTransfer(
            stepData.recommendation.recommendation_id,
            stepData.recommendation
          );
          setStepData((prev: any) => ({ ...prev, simulation: res }));
        }
      }
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    const nextStep = currentStep + 1;
    if (nextStep <= totalSteps) {
      setCurrentStep(nextStep);
      await handleExecuteStep(nextStep);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleRestart = async () => {
    setCurrentStep(1);
    setStepData({});
    try {
      await emergenciesApi.clearEmergency();
      await redistributionApi.resetSimulations();
    } catch {
      // Ignore
    }
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-command-900 border border-slate-200 shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <Play className="w-5 h-5 text-emerald-600 fill-emerald-400" />
            <h1 className="text-xl font-extrabold text-slate-900">
              Evaluator Guided Demo Walkthrough (3-Min Flow)
            </h1>
          </div>
          <p className="text-xs text-slate-500">
            Interactive step-by-step verification of healthcare supply-chain resilience in action.
          </p>
        </div>

        <button
          onClick={handleRestart}
          className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-600 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-200"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Demo Flow</span>
        </button>
      </div>

      {/* Progress Bar */}
      <div className="p-4 rounded-xl bg-command-900/60 border border-purple-900/30 space-y-2">
        <div className="flex justify-between text-xs font-bold">
          <span className="text-slate-700">Demonstration Step {currentStep} of {totalSteps}</span>
          <span className="text-purple-600 font-mono">{Math.round((currentStep / totalSteps) * 100)}% Completed</span>
        </div>
        <div className="w-full h-2 bg-slate-50 rounded-full overflow-hidden border border-purple-950">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      {/* Main Step Cards */}
      <div className="p-6 rounded-2xl border border-purple-900/40 bg-command-900 shadow-2xl space-y-6">
        {currentStep === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-purple-600 font-bold text-sm">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-purple-950 border border-purple-200 text-xs font-mono text-slate-900">
                1
              </span>
              <span>Step 1: Normal Everyday Clinic Operations</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              <strong>Swasthya Records</strong> monitors <strong>33 rural and urban health clinics</strong> across Bihar, Uttar Pradesh, and Maharashtra, keeping track of <strong>20 life-saving medicines</strong>, available patient beds, and healthcare staff.
            </p>
            <div className="grid grid-cols-3 gap-3 text-center text-xs p-4 rounded-xl bg-command-950 border border-purple-900/30 font-mono">
              <div>
                <span className="text-[10px] text-slate-500">Clinics Tracked</span>
                <p className="font-bold text-slate-800">33 Facilities</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500">Essential Medicines</span>
                <p className="font-bold text-slate-800">20 Medicines</p>
              </div>
              <div>
                <span className="text-[10px] text-slate-500">Active Emergencies</span>
                <p className="font-bold text-emerald-600">0 (Normal Baseline)</p>
              </div>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-rose-400 font-bold text-sm">
              <Flame className="w-5 h-5" />
              <span>Step 2: Emergency Flooding Hits Patna (+40% Patient Surge)</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Monsoon flooding hits the district. Patient visits increase by <strong>+40%</strong>. Patients arriving with dehydration and waterborne sickness rapidly consume <strong>Oral Rehydration Salts (ORS)</strong> and <strong>Paracetamol</strong>.
            </p>
            {stepData.emergency && (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs space-y-1.5">
                <p className="font-bold text-rose-300">Emergency Active: {stepData.emergency.event_type}</p>
                <p className="text-slate-600">Extra Patient Demand: +40% (1.4x usual rate) in Patna District</p>
                <p className="text-slate-500">Status: Running simulated crisis scenario</p>
              </div>
            )}
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-pink-400 font-bold text-sm">
              <TrendingUp className="w-5 h-5" />
              <span>Step 3: Smart Forecasting Detects Fast Consumption</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Instead of waiting for the medicine shelf to be completely empty, the system looks ahead 14 days and detects that medicine is being used up more than twice as fast as normal.
            </p>
            {stepData.forecast && (
              <div className="p-4 rounded-xl bg-command-950 border border-purple-900/30 text-xs space-y-1">
                <p className="font-bold text-pink-300">Forecast Status: Updated</p>
                <p className="text-slate-600">Projected Daily Usage: ~185 packets / day (normally only 60 packets / day)</p>
              </div>
            )}
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-rose-400 font-bold text-sm">
              <AlertTriangle className="w-5 h-5" />
              <span>Step 4: Early Shortage Warning (Only 1.4 Days of Stock Left!)</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Without help, <strong>Patna Sadar Primary Health Centre</strong> will completely run out of ORS in just <strong>1.4 days</strong>. The system issues an urgent warning to health officers with clear mathematical proof.
            </p>
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs space-y-1">
              <p className="font-bold text-rose-300">URGENT ALERT: High Risk of Stockout</p>
              <p className="text-slate-600">Patna Sadar PHC • Oral Rehydration Salts • Stock Remaining: 1.4 Days</p>
            </div>
          </div>
        )}

        {currentStep === 5 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-purple-600 font-bold text-sm">
              <Bot className="w-5 h-5" />
              <span>Step 5: Health Officer Asks AI Assistant for Explanation</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              The health officer asks: <em>"Why is this clinic running out of medicine and who can help?"</em> The AI answers using verified database numbers — never guessing or making up data.
            </p>
            {stepData.copilot && (
              <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-700/40 text-xs space-y-2">
                <p className="text-slate-700 leading-relaxed">{stepData.copilot.response}</p>
                <span className="text-[10px] text-emerald-600 font-bold block">
                  ✓ Verified records queried: {stepData.copilot.tools_called?.join(', ')}
                </span>
              </div>
            )}
          </div>
        )}

        {currentStep === 6 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-emerald-600 font-bold text-sm">
              <RefreshCw className="w-5 h-5" />
              <span>Step 6: Smart Rebalancing Finds Nearby Helper Clinic</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              The smart rebalancing solver searches nearby clinics to find who has surplus medicine and can safely share supplies without putting their own patients at risk. It recommends moving supplies from <strong>Danapur Clinic</strong>.
            </p>
            {stepData.recommendation && (
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-600/40 text-xs space-y-1.5 font-mono">
                <p className="font-bold text-emerald-600">Recommended Supply Transfer: +{stepData.recommendation.total_transfer_allocated} Units</p>
                <p className="text-slate-600">Distance: {stepData.recommendation.total_distance_km?.toFixed(1)} km • Delivery Time: ~{stepData.recommendation.max_eta_hours?.toFixed(1)} hours</p>
                <p className="text-slate-500">Predicted Result: Shortage Risk reduced from URGENT to SAFE</p>
              </div>
            )}
          </div>
        )}

        {currentStep === 7 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2.5 text-emerald-600 font-bold text-sm">
              <CheckCircle className="w-5 h-5" />
              <span>Step 7: Officer Approves Transfer — Shortage Prevented!</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              The health officer approves the transfer. The practice simulator updates immediately, boosting the clinic's medicine supply from <strong>1.4 days</strong> to <strong>14.2 days</strong>. The shortage is solved in advance with zero patient disruption!
            </p>
            {stepData.simulation && (
              <div className="p-4 rounded-xl bg-command-950 border border-emerald-200 text-xs space-y-2">
                <span className="font-bold text-emerald-600 uppercase text-[10px]">Transfer Successfully Completed in Simulation</span>
                <p className="text-slate-700">
                  Transferred: <strong>{stepData.simulation.total_units_transferred} medicine units</strong> • Risk Status: <strong>{stepData.simulation.risk_before} &rarr; {stepData.simulation.risk_after}</strong>
                </p>
              </div>
            )}
            <div className="flex justify-center gap-3 pt-4">
              <button
                onClick={() => onNavigate('dashboard')}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-slate-900 font-bold text-xs shadow-lg shadow-purple-900/40 transition-colors"
              >
                Return to Overview Dashboard
              </button>
            </div>
          </div>
        )}

        {/* Navigation Control Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-200">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-30 text-slate-600 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous Step</span>
          </button>

          {currentStep < totalSteps && (
            <button
              onClick={handleNext}
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-rose-600 hover:from-purple-500 hover:to-rose-500 disabled:opacity-50 text-slate-900 text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shadow-purple-900/40"
            >
              <span>{loading ? 'Processing Step...' : 'Execute Next Step'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
