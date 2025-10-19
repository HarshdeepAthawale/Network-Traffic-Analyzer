"use client"

import { Pie, PieChart, Cell, Tooltip, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/card"

type Item = { protocol: string; count: number; pct: number }
const COLORS = [
  "var(--color-brand)",
  "var(--color-accent-1)",
  "var(--color-accent-2)",
  "hsl(210 40% 35%)",
  "hsl(15 70% 55%)",
  "hsl(140 45% 45%)",
]

export function ProtocolChart({
  data,
  loading,
  selected,
  onSelect,
}: {
  data: Item[]
  loading?: boolean
  selected: string | null
  onSelect: (p: string) => void
}) {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium">Protocol Distribution</h3>
        <p className="text-xs text-muted-foreground">Click a slice to filter</p>
      </div>
      <div className="h-64">
        {loading ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="count"
                nameKey="protocol"
                innerRadius={60}
                outerRadius={90}
                onClick={(e) => onSelect(e?.protocol)}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    opacity={selected && selected !== entry.protocol ? 0.45 : 1}
                    cursor="pointer"
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: any, _name: any, p: any) => [`${value} (${p?.payload?.pct}%)`, p?.payload?.protocol]}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
