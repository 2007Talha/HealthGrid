import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface SeverityBadgeProps {
  severity?: 'CRITICAL' | 'HIGH' | 'WARNING' | 'NORMAL' | 'INFO' | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity = 'NORMAL',
  size = 'md',
  showIcon = true
}) => {
  const { t } = useLanguage();
  const sev = (severity || 'NORMAL').toUpperCase();

  let colorClasses = 'bg-emerald-950/80 text-emerald-600 border-emerald-500/40';
  let Icon = CheckCircle;
  let labelKey = 'severity.normal';

  if (sev === 'CRITICAL') {
    colorClasses = 'bg-red-950/90 text-red-600 border-red-500/60 shadow-sm shadow-red-900/40';
    Icon = AlertCircle;
    labelKey = 'severity.critical';
  } else if (sev === 'HIGH') {
    colorClasses = 'bg-orange-950/80 text-orange-300 border-orange-500/50';
    Icon = AlertTriangle;
    labelKey = 'severity.high';
  } else if (sev === 'WARNING') {
    colorClasses = 'bg-amber-950/80 text-amber-600 border-amber-500/50';
    Icon = AlertTriangle;
    labelKey = 'severity.warning';
  } else if (sev === 'INFO') {
    colorClasses = 'bg-blue-950/80 text-blue-600 border-blue-500/50';
    Icon = Info;
    labelKey = 'severity.info';
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs font-semibold gap-1',
    md: 'px-2.5 py-1 text-xs font-bold gap-1.5',
    lg: 'px-3.5 py-1.5 text-sm font-extrabold gap-2'
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border tracking-wide uppercase font-mono ${sizeClasses} ${colorClasses}`}
      role="status"
      aria-label={`Severity: ${sev}`}
    >
      {showIcon && <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />}
      <span>{t(labelKey) || sev}</span>
    </span>
  );
};
