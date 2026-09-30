import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

export const Footer: React.FC<{ onNavigateAbout?: () => void }> = ({ onNavigateAbout }) => {
  const { t } = useLanguage();

  return (
    <footer className="w-full border-t border-command-700 bg-command-950 py-3 px-6 text-xs text-slate-500">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
        <span>
          <strong className="text-slate-600">Swasthya Records</strong> — Predict. Warn. Redistribute. Respond.
        </span>
        <div className="flex items-center gap-3">
          <span>Data: MoHFW RHS 2022, HMIS, NLEM</span>
          {onNavigateAbout && (
            <button
              onClick={onNavigateAbout}
              className="text-primary hover:text-primary-hover underline font-medium"
            >
              Data Sources
            </button>
          )}
        </div>
      </div>
    </footer>
  );
};
