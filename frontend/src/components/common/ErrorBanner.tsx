import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface ErrorBannerProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => {
  const { t } = useLanguage();

  return (
    <div className="flex items-center justify-between p-4 rounded-xl border border-red-200 bg-red-50 text-red-700">
      <div className="flex items-center gap-3">
        <AlertOctagon className="w-5 h-5 text-red-600 shrink-0" />
        <div>
          <h5 className="text-sm font-bold text-red-800">{t('common.error_title')}</h5>
          <p className="text-xs text-red-600">{message || t('common.error_desc')}</p>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-red-100 hover:bg-red-200 border border-red-300 text-red-700 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>{t('actions.retry')}</span>
        </button>
      )}
    </div>
  );
};
