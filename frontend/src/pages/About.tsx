import React from 'react';
import { Database, ShieldCheck, ExternalLink, Cpu, Layers, CheckCircle2, Globe2 } from 'lucide-react';
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
          Federated National Healthcare Resource & Supply-Chain Resilience Platform
        </p>
        <div className="flex flex-wrap justify-center gap-2 pt-1">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-100 text-blue-700 border border-blue-300">
            Hackathon Track 3: Smart Health & Supply Chain Resilience
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-100 text-indigo-700 border border-indigo-300">
            BRICS Shared Predictive Modelling Ready
          </span>
        </div>
      </div>

      {/* Official Problem & Challenge Statement */}
      <div className="p-6 rounded-2xl border border-blue-200 bg-blue-50/70 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-blue-900 font-extrabold text-sm uppercase tracking-wider">
          <Globe2 className="w-5 h-5 text-blue-600" />
          <span>The Global Problem & BRICS Healthcare Challenge</span>
        </div>

        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
          <div className="p-3.5 rounded-xl bg-white border border-blue-200 space-y-1">
            <strong className="text-rose-700 block uppercase text-[10px] tracking-wider font-extrabold">The Problem</strong>
            <p className="text-slate-800">
              Public healthcare systems across developing nations face persistent supply chain vulnerabilities. The inability to track medicines, patient footfall, and resource utilisation in real time across vast networks of Primary Health Centres leads to stock-outs and limits a nation's capacity to respond when it matters most.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-white border border-blue-200 space-y-1">
            <strong className="text-blue-700 block uppercase text-[10px] tracking-wider font-extrabold">The Challenge</strong>
            <p className="text-slate-800">
              Build a federated AI platform for national-scale health resource and supply chain management — real-time visibility into medicine stocks, bed availability, and medical personnel attendance across a nation's entire PHC network. It should forecast demand, generate early warnings for potential stock-outs during health emergencies, and recommend automated cross-district resource redistribution, while allowing for shared predictive modelling across BRICS nations.
            </p>
          </div>
        </div>
      </div>

      {/* Core Solution Pillars */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          How Swasthya Records Solves The Challenge
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          <strong>Swasthya Records</strong> provides an operational end-to-end resilience grid unifying official Indian government healthcare dataset foundations with federated machine learning demand forecasting, Google OR-Tools cross-district redistribution optimization, and a deterministic AI assistant.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-slate-900 block font-bold">1. Real-Time Network Telemetry</strong>
            <p className="text-slate-600 text-[11px]">
              Continuous tracking of on-hand medicine quantities, burn rates, sanctioned bed availability, and on-duty medical personnel attendance across all PHCs.
            </p>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-slate-900 block font-bold">2. Predictive Demand Forecaster</strong>
            <p className="text-slate-600 text-[11px]">
              Multi-horizon (1-day to 14-day) machine learning forecasts with P10/P50/P90 prediction intervals accounting for climate shocks and population demographics.
            </p>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-slate-900 block font-bold">3. Early Warning Emergency Engine</strong>
            <p className="text-slate-600 text-[11px]">
              Proactive stockout countdowns (&lt; 36h) during monsoon floods, heatwaves, or epidemic disease surges before any clinical downtime occurs.
            </p>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-slate-900 block font-bold">4. Cross-District Rebalancing Solver</strong>
            <p className="text-slate-600 text-[11px]">
              Google OR-Tools Mixed Integer Linear Programming (CBC MILP) solver generating balanced multi-source redistribution plans while preserving 10-day donor safety stocks.
            </p>
          </div>
        </div>
      </div>

      {/* BRICS Federated AI Architecture */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
          <Globe2 className="w-4 h-4 text-indigo-600" />
          Shared Predictive Modelling Across BRICS Nations
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Swasthya Records implements privacy-preserving <strong>Federated Learning (FedAvg with Differential Privacy)</strong> to enable shared predictive modelling across <strong>BRICS partner nations (Brazil, Russia, India, China, South Africa)</strong>:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
          <div className="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-1">
            <strong className="text-indigo-900 font-bold block">1. Local Edge Training</strong>
            <p className="text-slate-600 text-[11px]">
              Each sovereign nation trains demand forecasting models on local PHC telemetry without sharing raw patient or sovereign stock data outside national borders.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-1">
            <strong className="text-indigo-900 font-bold block">2. Secure Weight Aggregation</strong>
            <p className="text-slate-600 text-[11px]">
              Only encrypted model weights and gradient updates are aggregated across BRICS nodes to build high-generalizability seasonal epidemic models.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-1">
            <strong className="text-indigo-900 font-bold block">3. Cross-Climate Surge Transfer</strong>
            <p className="text-slate-600 text-[11px]">
              Shared learnings from climate shocks (e.g. tropical disease outbreaks in Brazil) accelerate early warning readiness in India and partner nations.
            </p>
          </div>
        </div>
      </div>

      {/* Official Government Data Sources Provenance Table */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
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
            <div key={i} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 text-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span className="font-bold text-slate-800">{src.name}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-100 text-blue-700 border border-blue-300 w-fit">
                  {src.tier}
                </span>
              </div>
              <p className="text-slate-500">{src.authority}</p>
              <p className="text-slate-600">{src.description}</p>
              <a
                href={src.url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-blue-600 hover:text-blue-700 underline inline-flex items-center gap-1 pt-1 font-medium"
              >
                <span>Verify Source Repository</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Technical Multi-Layer Architecture */}
      <div className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-600" />
          Technical Multi-Layer Architecture
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-blue-700 font-bold block">1. Data Foundation Layer</strong>
            <p className="text-slate-600">
              Cleaned official MoHFW schemas, BigQuery telemetry warehouse, and realistic operational digital twin simulator.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-cyan-700 font-bold block">2. Predictive Intelligence</strong>
            <p className="text-slate-600">
              Ridge, LightGBM, and Random Forest models generating 14-day demand forecasts with P10/P50/P90 prediction intervals.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-emerald-700 font-bold block">3. Redistribution Optimizer</strong>
            <p className="text-slate-600">
              Google OR-Tools Mixed Integer Linear Programming (CBC MILP) solver balancing surplus and deficits while preserving safety stock.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
            <strong className="text-purple-700 font-bold block">4. Grounded AI Operations Assistant</strong>
            <p className="text-slate-600">
              Deterministic tool execution with natural language explanation synthesis, What-If shadow simulator, and bilingual audio pipeline.
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-500 text-center leading-relaxed">
        Swasthya Records is an operational hackathon prototype and decision-support tool. All simulated inventory rebalances and scenario forecasts execute within a sandboxed digital twin without altering live medical shipments.
      </div>
    </div>
  );
};
