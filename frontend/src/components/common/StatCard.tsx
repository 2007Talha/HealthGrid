import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  icon: LucideIcon;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    text: string;
  };
  severity?: 'critical' | 'high' | 'warning' | 'normal' | 'info' | 'default';
  onClick?: () => void;
  isLoading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subValue,
  icon: Icon,
  trend,
  severity = 'default',
  onClick,
  isLoading = false
}) => {
  const severityStyles = {
    critical: 'border-risk-critical/30 text-risk-critical',
    high: 'border-risk-high/30 text-risk-high',
    warning: 'border-risk-warning/30 text-risk-warning',
    normal: 'border-risk-normal/25 text-risk-normal',
    info: 'border-risk-info/25 text-risk-info',
    default: 'border-command-700 text-primary'
  }[severity];

  return (
    <div
      onClick={onClick}
      className={`relative p-5 rounded-xl border transition-all duration-200 bg-command-900 ${
        onClick ? 'cursor-pointer hover:border-primary/50 hover:-translate-y-0.5 hover:shadow-lg' : ''
      } ${severityStyles}`}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1.5">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
          {isLoading ? (
            <div className="h-8 w-24 bg-command-800 animate-pulse rounded my-1" />
          ) : (
            <h3 className="text-2xl font-bold text-slate-800 font-mono tracking-tight">
              {value}
            </h3>
          )}
        </div>
        <div className="p-2.5 rounded-lg bg-command-850 border border-command-700">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(subValue || trend) && (
        <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-command-700">
          {subValue && <span>{subValue}</span>}
          {trend && (
            <span
              className={`inline-flex items-center gap-1 font-medium ${
                trend.direction === 'up'
                  ? 'text-risk-normal'
                  : trend.direction === 'down'
                  ? 'text-risk-critical'
                  : 'text-slate-400'
              }`}
            >
              {trend.direction === 'up' && <TrendingUp className="w-3.5 h-3.5" />}
              {trend.direction === 'down' && <TrendingDown className="w-3.5 h-3.5" />}
              {trend.direction === 'neutral' && <Minus className="w-3.5 h-3.5" />}
              {trend.text}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
