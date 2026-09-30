import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine
} from 'recharts';
import { InventoryRecord } from '../../types';

interface InventoryTrendChartProps {
  data: InventoryRecord[];
  title?: string;
  height?: number;
}

export const InventoryTrendChart: React.FC<InventoryTrendChartProps> = ({
  data,
  title = 'Inventory Levels & Daily Consumption',
  height = 300
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-xs border border-slate-200 rounded-xl bg-command-900/30">
        No inventory historical records available.
      </div>
    );
  }

  const formatted = data.map((d) => ({
    date: d.record_date.slice(5),
    stock: d.closing_stock || d.current_stock || 0,
    consumption: d.daily_consumption || 0,
    safety: d.safety_stock || 50,
    reorder: d.reorder_level || 150
  }));

  const latestSafety = data[data.length - 1]?.safety_stock || 50;

  return (
    <div className="p-4 rounded-xl border border-slate-200 bg-command-900/60">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">{title}</h4>
        <span className="text-[10px] font-mono text-slate-500">Stock vs Daily Consumption</span>
      </div>

      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <ComposedChart data={formatted} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
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
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />

            <ReferenceLine
              y={latestSafety}
              stroke="#ef4444"
              strokeDasharray="3 3"
              label={{ value: 'Safety Stock', fill: '#ef4444', fontSize: 10, position: 'insideTopRight' }}
            />

            {/* Daily Consumption (Bar) */}
            <Bar dataKey="consumption" fill="#6366f1" opacity={0.6} name="Daily Consumption (Units)" />

            {/* Stock Level (Line) */}
            <Line
              type="monotone"
              dataKey="stock"
              stroke="#38bdf8"
              strokeWidth={2.5}
              dot={{ r: 2 }}
              name="Closing Stock (Units)"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
