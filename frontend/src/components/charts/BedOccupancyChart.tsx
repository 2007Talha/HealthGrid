import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine
} from 'recharts';
import { BedStatus } from '../../types';

interface BedOccupancyChartProps {
  data: BedStatus[];
  title?: string;
  height?: number;
}

export const BedOccupancyChart: React.FC<BedOccupancyChartProps> = ({
  data,
  title = 'Bed Occupancy Rate (%)',
  height = 260
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-xs border border-slate-200 rounded-xl bg-command-900/30">
        No bed occupancy records available.
      </div>
    );
  }

  const formatted = data.map((d: any) => ({
    date: (d.record_date || '').slice(5),
    occupancy_pct: d.occupancy_rate_pct ?? d.bed_occupancy_rate_pct ?? 0,
    occupied: d.occupied_beds ?? d.beds_occupied ?? 0,
    total: d.total_beds ?? d.beds_total ?? 0
  }));

  return (
    <div className="p-4 rounded-xl border border-slate-200 bg-command-900/60">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">{title}</h4>
        <span className="text-[10px] font-mono text-slate-500">Critical Threshold: 90%</span>
      </div>

      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <AreaChart data={formatted} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="occupancyGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0b1329',
                borderColor: '#1e305e',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '12px'
              }}
              formatter={(val: any) => [`${val}%`, 'Occupancy']}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

            <ReferenceLine
              y={90}
              stroke="#ef4444"
              strokeDasharray="4 4"
              label={{ value: 'Overflow Warning (90%)', fill: '#ef4444', fontSize: 10, position: 'insideTopRight' }}
            />

            <Area
              type="monotone"
              dataKey="occupancy_pct"
              stroke="#f59e0b"
              strokeWidth={2}
              fill="url(#occupancyGradient)"
              name="Bed Occupancy Rate (%)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
