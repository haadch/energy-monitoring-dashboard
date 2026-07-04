import { useEffect, useState } from 'react'
import { getDaily } from '../api'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend
} from 'recharts'

type DailyRow = {
  shift_date:  string
  total_kwh:   number
  peak_kwh:    number
  gap_pct:     number
  day_quality: string
}

type Props = {
  start: string
  end:   string
}

export default function DailyChart({ start, end }: Props) {
  const [data, setData] = useState<DailyRow[]>([])

  useEffect(() => {
    getDaily(start, end).then(setData)
  }, [start, end])

  const formatDate = (d: string) => {
    const date = new Date(d)
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tooltipFormatter = (value: any) => [`${Number(value).toLocaleString()} kWh`, 'Daily kWh']

  return (
    <div className="bg-gray-900 rounded-xl p-6 mb-6">
      <h2 className="text-lg font-semibold text-white mb-4">
        Daily Consumption — Business Day (6AM to 6AM)
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="shift_date"
            tickFormatter={formatDate}
            tick={{ fill: '#9CA3AF', fontSize: 11 }}
            interval={Math.floor(data.length / 6)}
          />
          <YAxis
            tickFormatter={(v) => `${(v/1000).toFixed(1)}k`}
            tick={{ fill: '#9CA3AF', fontSize: 11 }}
          />
          <Tooltip
            formatter={tooltipFormatter}
            labelFormatter={(l) => `Date: ${l}`}
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
            labelStyle={{ color: '#F9FAFB' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="total_kwh"
            name="Daily kWh"
            stroke="#3B82F6"
            dot={false}
            strokeWidth={1.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}