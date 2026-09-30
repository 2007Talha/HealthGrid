import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { NotificationProvider } from './context/NotificationContext';
import { Header } from './components/layout/Header';
import { Sidebar, NavRoute } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';
import { GlobalSearch } from './components/layout/GlobalSearch';
import { FloatingCopilot } from './components/copilot/FloatingCopilot';
import { WhatIfPanel } from './components/copilot/WhatIfPanel';

// Pages
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import { AlertDetail } from './pages/AlertDetail';
import { Medicines } from './pages/Medicines';
import { MedicineDetail } from './pages/MedicineDetail';
import { Facilities } from './pages/Facilities';
import { FacilityDetail } from './pages/FacilityDetail';
import { Forecasts } from './pages/Forecasts';
import { Redistribution } from './pages/Redistribution';
import { Emergencies } from './pages/Emergencies';
import { CopilotPage } from './pages/CopilotPage';
import { SystemStatus } from './pages/SystemStatus';
import { DataSources } from './pages/DataSources';
import { DemoFlow } from './pages/DemoFlow';

const MainLayout: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [currentRoute, setCurrentRoute] = useState<NavRoute>('dashboard');
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isWhatIfModalOpen, setIsWhatIfModalOpen] = useState(false);

  const handleNavigate = (route: string, entityId?: string) => {
    setCurrentRoute(route as NavRoute);
    setSelectedEntityId(entityId || null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => handleNavigate('dashboard')} />;
  }

  return (
    <div className="min-h-screen bg-command-950 text-slate-700 flex flex-col">
      <Header
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenCopilot={() => setIsCopilotOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentRoute={currentRoute}
          onNavigate={(route) => handleNavigate(route)}
        />

        <main className="flex-1 overflow-y-auto bg-command-950 pb-8">
          {currentRoute === 'dashboard' && (
            <Dashboard
              onNavigate={(r, id) => handleNavigate(r, id)}
              onOpenCopilot={() => setIsCopilotOpen(true)}
              onOpenWhatIf={() => setIsWhatIfModalOpen(true)}
            />
          )}

          {currentRoute === 'alerts' && (
            selectedEntityId ? (
              <AlertDetail
                alertId={selectedEntityId}
                onBack={() => setSelectedEntityId(null)}
                onNavigateRedistribution={(target) => handleNavigate('redistribution', target)}
              />
            ) : (
              <Alerts
                onSelectAlert={(id) => setSelectedEntityId(id)}
                onOpenCopilot={() => setIsCopilotOpen(true)}
              />
            )
          )}

          {currentRoute === 'medicines' && (
            selectedEntityId ? (
              <MedicineDetail
                medicineCode={selectedEntityId}
                onBack={() => setSelectedEntityId(null)}
                onNavigateRedistribution={() => handleNavigate('redistribution', `:${selectedEntityId}`)}
              />
            ) : (
              <Medicines
                onSelectMedicine={(code) => setSelectedEntityId(code)}
              />
            )
          )}

          {currentRoute === 'facilities' && (
            selectedEntityId ? (
              <FacilityDetail
                facilityId={selectedEntityId}
                onBack={() => setSelectedEntityId(null)}
                onNavigateRedistribution={() => handleNavigate('redistribution', selectedEntityId)}
                onOpenWhatIf={() => setIsWhatIfModalOpen(true)}
              />
            ) : (
              <Facilities
                onSelectFacility={(id) => setSelectedEntityId(id)}
              />
            )
          )}

          {currentRoute === 'forecasts' && <Forecasts />}

          {currentRoute === 'redistribution' && (
            <Redistribution targetShortage={selectedEntityId} />
          )}

          {currentRoute === 'emergencies' && <Emergencies />}

          {currentRoute === 'copilot' && <CopilotPage />}

          {currentRoute === 'demo' && (
            <DemoFlow onNavigate={(r, id) => handleNavigate(r, id)} />
          )}

          {currentRoute === 'system' && <SystemStatus />}

          {currentRoute === 'about' && <DataSources />}
        </main>
      </div>

      <Footer onNavigateAbout={() => handleNavigate('about')} />

      {/* Global Search Modal */}
      <GlobalSearch
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectFacility={(id) => handleNavigate('facilities', id)}
        onSelectMedicine={(code) => handleNavigate('medicines', code)}
        onSelectAlert={(id) => handleNavigate('alerts', id)}
      />

      {/* Floating Copilot Drawer */}
      <FloatingCopilot
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
      />

      {/* What-If Modal */}
      {isWhatIfModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <WhatIfPanel onClose={() => setIsWhatIfModalOpen(false)} />
          </div>
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <NotificationProvider>
          <MainLayout />
        </NotificationProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}
