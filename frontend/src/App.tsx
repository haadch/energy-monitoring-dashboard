import { useEffect, useState } from 'react'
import { getSummary } from './api'
import KpiCard from './components/KpiCard'
import DailyChart from './components/DailyChart'
import ForecastChart from './components/ForecastChart'
import ShiftChart from './components/ShiftChart'
import HourlyChart from './components/HourlyChart'

type Summary = {
  total_kwh:     number
  avg_daily_kwh: number
  peak_day:      string
  peak_kwh:      number
  total_days:    number
  good_days:     number
  poor_days:     number
  data_start:    string
  data_end:      string
}

export default function App() {
  const [summary, setSummary]   = useState<Summary | null>(null)
  const [loading, setLoading]   = useState(true)
  const [startDate, setStartDate] = useState('2025-09-02')
  const [endDate, setEndDate]     = useState('2026-06-30')

  useEffect(() => {
    getSummary()
      .then(setSummary)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <p className="text-gray-400 text-lg">Loading...</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Energy Monitoring Dashboard</h1>
          <p className="text-gray-400 mt-1">Branch A · Industrial Site</p>
        </div>

        {/* Date range filter */}
        <div className="flex items-center gap-3 bg-gray-900 rounded-xl px-4 py-3">
          <div className="flex flex-col">
            <label className="text-gray-500 text-xs mb-1">From</label>
            <input
              type="date"
              value={startDate}
              min={summary?.data_start}
              max={endDate}
              onChange={e => setStartDate(e.target.value)}
              className="bg-gray-800 text-gray-300 text-sm rounded px-3 py-1 border border-gray-700"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-gray-500 text-xs mb-1">To</label>
            <input
              type="date"
              value={endDate}
              min={startDate}
              max={summary?.data_end}
              onChange={e => setEndDate(e.target.value)}
              className="bg-gray-800 text-gray-300 text-sm rounded px-3 py-1 border border-gray-700"
            />
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <KpiCard
          title="Total Consumption"
          value={`${(summary!.total_kwh / 1000).toFixed(1)}M kWh`}
          subtitle="Full data range"
          color="blue"
        />
        <KpiCard
          title="Daily Average"
          value={`${summary!.avg_daily_kwh.toLocaleString()} kWh`}
          subtitle="Per business day"
          color="green"
        />
        <KpiCard
          title="Peak Day"
          value={`${summary!.peak_kwh.toLocaleString()} kWh`}
          subtitle={summary!.peak_day}
          color="orange"
        />
      </div>

      {/* Charts — all receive date range props */}
      <DailyChart start={startDate} end={endDate} />
      <ForecastChart />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <ShiftChart start={startDate} end={endDate} />
        <HourlyChart />
      </div>

    </div>
  )
}