import React from 'react';
import { Database, ShieldAlert, FileText, CheckCircle2, AlertTriangle, ExternalLink } from 'lucide-react';

interface DataSourceItem {
  dataset: string;
  publisher: string;
  sourceType: 'Official Public Data' | 'Government Formulary' | 'Official Demographics' | 'Prototype Simulation';
  coverage: string;
  retrievedDate: string;
  howUsed: string;
  isSimulated: boolean;
  link?: string;
}

const DATA_SOURCES: DataSourceItem[] = [
  {
    dataset: 'Rural Health Statistics (RHS) 2021-2022',
    publisher: 'Ministry of Health and Family Welfare (MoHFW), Govt of India',
    sourceType: 'Official Public Data',
    coverage: 'National, 36 States & UTs, District and Sub-District Healthcare Infrastructure',
    retrievedDate: '2024 / RHS Annual Release',
    howUsed: 'Establishes the foundational registry of 33 sentinel Primary Health Centres (PHCs), Community Health Centres (CHCs), Sub-Divisional and District Hospitals, including geolocations, sanctioned bed capacities, and catchment demographics.',
    isSimulated: false,
    link: 'https://mohfw.gov.in/'
  },
  {
    dataset: 'Health Management Information System (HMIS) 2022-2023',
    publisher: 'National Health Mission (NHM), MoHFW',
    sourceType: 'Official Public Data',
    coverage: 'District-level outpatient (OPD) and inpatient (IPD) clinical load aggregates',
    retrievedDate: '2024 Annual Release',
    howUsed: 'Calibrates seasonal patient footfall baselines, typical outpatient visit volumes, and inpatient bed occupancy patterns for public healthcare facilities across Bihar, Uttar Pradesh, and Maharashtra.',
    isSimulated: false,
    link: 'https://hmis.mohfw.gov.in/'
  },
  {
    dataset: 'National List of Essential Medicines (NLEM) 2022',
    publisher: 'Department of Pharmaceuticals & Ministry of Health and Family Welfare',
    sourceType: 'Government Formulary',
    coverage: '384 Core Essential Medicines & Healthcare Consumables in India',
    retrievedDate: 'September 2022 / Gazette of India',
    howUsed: 'Standardizes the 20 tracked essential therapeutic medicines (ORS, Paracetamol, Amoxicillin, Metformin, Atorvastatin, Rabies Vaccine, etc.) with standardized clinical categories, safety buffer minimums, and standard packaging units.',
    isSimulated: false,
    link: 'https://cdsco.gov.in/'
  },
  {
    dataset: 'Census of India (Demographic & Administrative Boundaries)',
    publisher: 'Office of the Registrar General & Census Commissioner, Ministry of Home Affairs',
    sourceType: 'Official Demographics',
    coverage: 'State and District Administrative Geometries & Population Totals',
    retrievedDate: 'Census Data Repository',
    howUsed: 'Provides district-level population distributions and inter-facility transit distances used by the Google OR-Tools optimization solver to evaluate transfer feasibility and travel times.',
    isSimulated: false,
    link: 'https://censusindia.gov.in/'
  },
  {
    dataset: 'Operational Digital Twin (Inventory, Demand & Emergencies)',
    publisher: 'Swasthya Records Simulation Engine',
    sourceType: 'Prototype Simulation',
    coverage: '33 Sentinel Health Facilities (Daily time-series telemetry)',
    retrievedDate: 'Simulated in real-time / Demonstration Mode',
    howUsed: 'Because real-time, minute-by-minute inventory telemetry from rural PHCs is not publicly accessible via open APIs, the platform simulates daily medicine consumption, bed occupancy, doctor attendance, and emergency flood surges for prototype demonstration.',
    isSimulated: true
  }
];

export const DataSources: React.FC = () => {
  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-command-900 border border-slate-200">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/15 text-primary border border-primary/25">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight sm:text-2xl">Data Sources & Provenance</h1>
            <p className="text-xs text-slate-500">
              Complete transparency regarding official public government data sources versus prototype simulated records.
            </p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-blue-100 text-blue-700 border border-blue-300">
          5 Datasets Registered
        </span>
      </div>

      {/* Mandatory Disclaimers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Data Disclaimer */}
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 space-y-2">
          <div className="flex items-center gap-2 text-amber-700 font-bold text-xs uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4" />
            <span>Official Data Disclaimer</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            <strong>Swasthya Records</strong> is a prototype decision-support platform. Public and government datasets are used where available, while operational PHC inventory, demand, staffing and emergency conditions are simulated for demonstration. The prototype does not execute real-world medical logistics.
          </p>
        </div>

        {/* AI Disclaimer */}
        <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 space-y-2">
          <div className="flex items-center gap-2 text-blue-700 font-bold text-xs uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4" />
            <span>AI Decision-Support Disclaimer</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            AI-generated forecasts and recommendations are decision-support outputs and should always be reviewed and confirmed by authorized human health officers before any real-world operational or supply-chain action is taken.
          </p>
        </div>
      </div>

      {/* Provenance Table */}
      <div className="rounded-2xl border border-slate-200 bg-command-900 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-200 bg-command-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-slate-900">Dataset Provenance Matrix</h3>
          </div>
          <span className="text-[11px] text-slate-500 font-medium">5 Datasets Registered</span>
        </div>

        <div className="divide-y divide-slate-200">
          {DATA_SOURCES.map((ds, idx) => (
            <div key={idx} className="p-4 hover:bg-slate-50 transition-colors space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  {ds.isSimulated ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-300 uppercase tracking-wider">
                      Simulated Operational
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-300 uppercase tracking-wider flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Official Public
                    </span>
                  )}
                  <h4 className="text-sm font-bold text-slate-900">{ds.dataset}</h4>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-500">
                  <span className="text-primary font-medium">{ds.publisher}</span>
                  {ds.link && (
                    <a
                      href={ds.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary-hover inline-flex items-center gap-1"
                    >
                      <span>Portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                  <p className="text-[10px] font-bold uppercase text-slate-500 mb-1">Source Type & Release</p>
                  <p className="text-slate-600 font-medium">{ds.sourceType} • {ds.retrievedDate}</p>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 md:col-span-2">
                  <p className="text-[10px] font-bold uppercase text-slate-500 mb-1">Geographic & Clinical Coverage</p>
                  <p className="text-slate-600">{ds.coverage}</p>
                </div>
              </div>

              <div className="text-xs bg-blue-50 p-3 rounded-xl border border-blue-100">
                <span className="text-slate-500 font-bold">How Swasthya Records Uses This: </span>
                <span className="text-slate-700">{ds.howUsed}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture Provenance Note */}
      <div className="p-4 rounded-2xl bg-command-900 border border-slate-200 text-xs text-slate-500 space-y-2">
        <h4 className="text-sm font-bold text-primary">Data Architecture Principles</h4>
        <ul className="list-disc pl-5 space-y-1 text-slate-600">
          <li><strong>Zero Hallucinated Records:</strong> Facilities, geo-coordinates, and medicine IDs strictly map to official Indian government identifiers.</li>
          <li><strong>Clear Simulation Labelling:</strong> Any operational state generated via the simulator is tagged with <code className="text-amber-700 bg-amber-50 px-1 py-0.5 rounded text-[11px] border border-amber-200">DEMO MODE</code> to maintain strict ethical data standards.</li>
          <li><strong>Production Extensibility:</strong> In production environments, the simulation layer can be swapped with real-time state e-Aushadhi and DVDMS (Drug & Vaccine Distribution Management System) APIs via standard FHIR / ABDM adapters.</li>
        </ul>
      </div>
    </div>
  );
};
