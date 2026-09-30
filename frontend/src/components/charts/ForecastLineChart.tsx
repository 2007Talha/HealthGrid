import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { ForecastItem } from '../../types';

interface ForecastLineChartProps {
  data: ForecastItem[];
  title?: string;
  unit?: string;
  height?: number;
}

export const ForecastLineChart: React.FC<ForecastLineChartProps> = ({
  data,
  title,
  unit = 'units',
  height = 320
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-xs border border-slate-200 rounded-xl bg-command-900/30">
        No forecast telemetry points available.
      </div>
    );
  }

  // Format data for chart
  const formatted = data.map((d: any, idx: number) => {
    const rawDate = d.date || d.target_date || '';
    const dateLabel = typeof rawDate === 'string' && rawDate.length >= 10
      ? rawDate.slice(5)
      : (rawDate || `Day ${d.horizon_day || idx + 1}`);
    const predicted = d.predicted_demand ?? d.predicted_consumption ?? d.predicted_footfall ?? d.predicted_occupancy ?? d.p50_median ?? 0;
    const lower = d.p10_lower !== undefined ? d.p10_lower : (d.lower_bound_p10 !== undefined ? d.lower_bound_p10 : null);
    const upper = d.p90_upper !== undefined ? d.p90_upper : (d.upper_bound_p90 !== undefined ? d.upper_bound_p90 : null);

    return {
      date: dateLabel,
      observed: d.actual_value !== undefined ? d.actual_value : null,
      predicted: Math.round(predicted * 10) / 10,
      lower: lower !== null ? Math.round(lower * 10) / 10 : null,
      upper: upper !== null ? Math.round(upper * 10) / 10 : null,
      range: lower !== null && upper !== null ? [lower, upper] : null
    };
  });

  return (
    <div className="p-4 rounded-xl border border-slate-200 bg-command-900/60 backdrop-blur-sm">
      {title && (
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">{title}</h4>
          <span className="text-[10px] font-mono text-slate-500">P10 — P90 Confidence Bounds</span>
        </div>
      )}

      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <ComposedChart data={formatted} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="confidenceBand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0b1329',
                borderColor: '#1e305e',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '12px'
              }}
              formatter={(val: any) => [`${val} ${unit}`, '']}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

            {/* Confidence Area (p10 to p90) */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="transparent"
              fill="url(#confidenceBand)"
              name="90% Upper Bound"
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="transparent"
              fill="#0b1329"
              name="10% Lower Bound"
            />

            {/* Predicted Demand Line (Dashed) */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#38bdf8"
              strokeWidth={2.5}
              strokeDasharray="4 4"
              dot={{ r: 3, fill: '#38bdf8' }}
              activeDot={{ r: 5 }}
              name="Predicted (ML Forecast)"
            />

            {/* Observed Historical Demand Line (Solid) */}
            <Line
              type="monotone"
              dataKey="observed"
              stroke="#10b981"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#10b981' }}
              name="Observed Telemetry"
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
