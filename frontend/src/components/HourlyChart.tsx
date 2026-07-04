import { useEffect, useState } from 'react'
import { getHourly } from '../api'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip
} from 'recharts'

type HourlyRow = {
  hour:      number
  total_kwh: number
}

export default function HourlyChart() {
  const [data, setData]               = useState<HourlyRow[]>([])
  const [selectedDate, setSelectedDate] = useState('2026-06-30')

  useEffect(() => {
    getHourly(selectedDate).then(setData)
  }, [selectedDate])

  const isEmpty = data.length === 0

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tooltipFormatter = (value: any) => [`${Number(value).toLocaleString()} kWh`, 'Consumption']

  return (
    <div className="bg-gray-900 rounded-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-lg font-semibold text-white">Hourly Pattern</h2>
        <input
          type="date"
          value={selectedDate}
          onChange={e => setSelectedDate(e.target.value)}
          className="bg-gray-800 text-gray-300 text-sm rounded px-3 py-1 border border-gray-700"
        />
      </div>
      <p className="text-gray-500 text-sm mb-4">
        Consumption by hour for selected date
      </p>

      {isEmpty ? (
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          No data available for this date
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="hour"
              tickFormatter={(h) => `${h}:00`}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              tickFormatter={(v) => `${(v/1000).toFixed(1)}k`}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <Tooltip
              formatter={tooltipFormatter}
              labelFormatter={(h) => `Hour: ${h}:00`}
              contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }}
              labelStyle={{ color: '#F9FAFB' }}
            />
            <Bar dataKey="total_kwh" name="kWh" fill="#10B981" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}