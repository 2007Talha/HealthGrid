import React from 'react';
import { Database, ShieldCheck, ExternalLink, Cpu, Layers, CheckCircle2 } from 'lucide-react';
import { Logo } from '../components/common/Logo';

export const About: React.FC = () => {
  return (
    <div className="p-4 sm:p-6 space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="flex justify-center">
          <Logo size={64} glow />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Swasthya Records (SwasthyaGrid AI)
        </h1>
        <p className="text-sm text-slate-600 font-medium max-w-xl mx-auto">
          Federated National Healthcare Resource & Supply-Chain Resilience Platform for India
        </p>
        <div className="flex justify-center gap-2 pt-1">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-950 text-blue-600 border border-blue-700/50">
            Hackathon Track 3: Smart Health & Supply Chain Resilience
          </span>
        </div>
      </div>

      {/* Core Problem & Mission */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          The Healthcare Supply-Chain Vulnerability
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Public healthcare networks across India face persistent supply-chain vulnerabilities. Lack of unified real-time visibility into medicine stock-outs, bed capacity surges, and medical staffing at the Primary Health Centre (PHC) level causes avoidable treatment delays during climate shocks and infectious disease outbreaks.
        </p>
        <p className="text-xs text-slate-600 leading-relaxed">
          <strong>SwasthyaGrid AI</strong> bridges this gap by unifying official Indian government healthcare dataset foundations with federated machine learning demand forecasting, Google OR-Tools cross-district redistribution optimization, and a grounded Swasthya AI Assistant.
        </p>
      </div>

      {/* Official Government Data Sources Provenance Table */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <Database className="w-4 h-4 text-blue-600" />
          Official Government Data Provenance & Sources
        </h3>

        <div className="space-y-3">
          {[
            {
              name: 'National List of Essential Medicines (NLEM 2022)',
              authority: 'Ministry of Health & Family Welfare / CDSCO',
              tier: 'OFFICIAL_GOVERNMENT',
              description: 'Standard formulations, strengths, unit packaging, and clinical essentiality tiers.',
              url: 'https://cdsco.gov.in/opencms/export/sites/CDSCO_WEB/Pdf-documents/NLEM_2022.pdf'
            },
            {
              name: 'Rural Health Statistics (RHS) & Health Directory',
              authority: 'MoHFW / Open Government Data Platform (data.gov.in)',
              tier: 'OFFICIAL_GOVERNMENT',
              description: 'Infrastructure metrics, sanctioned beds, geographical coordinates, and district hierarchy.',
              url: 'https://data.gov.in'
            },
            {
              name: 'Health Management Information System (HMIS)',
              authority: 'Ministry of Health & Family Welfare',
              tier: 'OFFICIAL_GOVERNMENT',
              description: 'Outpatient footfall, inpatient bed occupancy baselines, and seasonal epidemic trends.',
              url: 'https://hmis.mohfw.gov.in'
            }
          ].map((src, i) => (
            <div key={i} className="p-4 rounded-xl bg-slate-100/60 border border-slate-200 space-y-1.5 text-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span className="font-bold text-slate-800">{src.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-950 text-blue-600 border border-blue-700/40 w-fit">
                  {src.tier}
                </span>
              </div>
              <p className="text-slate-500">{src.authority}</p>
              <p className="text-slate-600">{src.description}</p>
              <a
                href={src.url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-blue-600 hover:text-blue-600 underline inline-flex items-center gap-1 pt-1"
              >
                <span>Verify Source Repository</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* System Architecture */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-command-900 shadow-xl space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-600" />
          Technical Multi-Layer Architecture
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200 space-y-1">
            <strong className="text-blue-600">1. Data Foundation Layer</strong>
            <p className="text-slate-500">
              Cleaned official MoHFW schemas, BigQuery telemetry warehouse, and realistic operational digital twin simulator.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200 space-y-1">
            <strong className="text-cyan-600">2. Predictive Intelligence</strong>
            <p className="text-slate-500">
              Ridge, LightGBM, and Random Forest models generating 14-day demand forecasts with P10/P50/P90 prediction intervals.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200 space-y-1">
            <strong className="text-emerald-600">3. Redistribution Optimizer</strong>
            <p className="text-slate-500">
              Google OR-Tools Mixed Integer Linear Programming (CBC MILP) solver balancing surplus and deficits while preserving safety stock.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-100/60 border border-slate-200 space-y-1">
            <strong className="text-purple-600">4. Grounded AI Operations Assistant</strong>
            <p className="text-slate-500">
              Deterministic tool execution with natural language explanation synthesis, What-If shadow simulator, and bilingual audio pipeline.
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-100/80 border border-slate-200 text-[11px] text-slate-500 text-center leading-relaxed">
        Swasthya Records is an operational hackathon prototype and decision-support tool. All simulated inventory rebalances and scenario forecasts execute within a sandboxed digital twin without altering live medical shipments.
      </div>
    </div>
  );
};
