import { useEffect, useState } from 'react'
import { getShifts } from '../api'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend
} from 'recharts'

type ShiftRow = {
  shift_date:  string
  shift:       string
  total_kwh:   number
  gap_pct:     number
  day_quality: string
}

type ChartRow = {
  shift_date: string
  'Shift A':  number
  'Shift B':  number
  'Shift C':  number
}

type Props = {
  start: string
  end:   string
}

export default function ShiftChart({ start, end }: Props) {
  const [data, setData] = useState<ChartRow[]>([])

  useEffect(() => {
    getShifts(start, end).then((rows: ShiftRow[]) => {
      const map: Record<string, ChartRow> = {}
      rows.forEach(row => {
        if (!map[row.shift_date]) {
          map[row.shift_date] = {
            shift_date: row.shift_date,
            'Shift A': 0,
            'Shift B': 0,
            'Shift C': 0
          }
        }
        map[row.shift_date][row.shift as 'Shift A' | 'Shift B' | 'Shift C'] = Math.round(row.total_kwh)
      })
      setData(Object.values(map))
    })
  }, [start, end])

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tooltipFormatter = (value: any) => [`${Number(value).toLocaleString()} kWh`, '']

  return (
    <div className="bg-gray-900 rounded-xl p-6 mb-6">
      <h2 className="text-lg font-semibold text-white mb-1">
        Shift-wise Consumption
      </h2>
      <p className="text-gray-500 text-sm mb-4">
        Shift A 06:00–14:00 · Shift B 14:00–22:00 · Shift C 22:00–06:00
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="shift_date"
            tick={{ fill: '#9CA3AF', fontSize: 10 }}
            interval={Math.floor(data.length / 6)}
          />
          <YAxis
            tickFormatter={(v) => `${(v/1000).toFixed(1)}k`}
            tick={{ fill: '#9CA3AF', fontSize: 11 }}
          />
          <Tooltip
            formatter={tooltipFormatter}
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
            labelStyle={{ color: '#F9FAFB' }}
          />
          <Legend />
          <Bar dataKey="Shift A" stackId="a" fill="#3B82F6" />
          <Bar dataKey="Shift B" stackId="a" fill="#8B5CF6" />
          <Bar dataKey="Shift C" stackId="a" fill="#06B6D4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}