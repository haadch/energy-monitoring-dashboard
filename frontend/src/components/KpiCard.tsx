type Props = {
  title: string
  value: string | number
  subtitle?: string
  color?: string
}

export default function KpiCard({ title, value, subtitle, color = "blue" }: Props) {
  const colors: Record<string, string> = {
    blue:   "border-blue-500",
    green:  "border-green-500",
    orange: "border-orange-500",
    red:    "border-red-500",
  }

  return (
    <div className={`bg-gray-900 rounded-xl p-5 border-l-4 ${colors[color]}`}>
      <p className="text-gray-400 text-sm mb-1">{title}</p>
      <p className="text-white text-2xl font-bold">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
    </div>
  )
}