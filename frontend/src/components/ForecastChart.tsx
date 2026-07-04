import { useEffect, useState } from 'react'
import { getForecast } from '../api'
import {
  ResponsiveContainer, ComposedChart, Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts'

type ForecastRow = {
  date:          string
  predicted_kwh: number
  lower_bound:   number
  upper_bound:   number
}

export default function ForecastChart() {
  const [data, setData] = useState<ForecastRow[]>([])

  useEffect(() => {
    getForecast().then(setData)
  }, [])

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tooltipFormatter = (value: any) => [`${Number(value).toLocaleString()} kWh`, '']

  return (
    <div className="bg-gray-900 rounded-xl p-6 mb-6">
      <h2 className="text-lg font-semibold text-white mb-1">
        14-Day Forecast
      </h2>
      <p className="text-gray-500 text-sm mb-4">
        Prophet model · 88.81% accuracy on held-out data
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#9CA3AF', fontSize: 11 }}
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
          <Area
            type="monotone"
            dataKey="upper_bound"
            name="Upper bound"
            fill="#F97316"
            stroke="none"
            fillOpacity={0.15}
          />
          <Area
            type="monotone"
            dataKey="lower_bound"
            name="Lower bound"
            fill="#111827"
            stroke="none"
            fillOpacity={1}
          />
          <Line
            type="monotone"
            dataKey="predicted_kwh"
            name="Predicted kWh"
            stroke="#F97316"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ fill: '#F97316', r: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}