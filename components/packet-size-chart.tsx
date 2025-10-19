"use client"

import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/card"

type Bin = { range: string; count: number; min: number; max: number; mean: number; median: number; p95: number }

export function PacketSizeChart({ data, loading }: { data: Bin[]; loading?: boolean }) {
  return (
    <Card className="p-4">
      <div className="mb-3">
        <h3 className="text-sm font-medium">Packet Size Distribution</h3>
        <p className="text-xs text-muted-foreground">Histogram of packet sizes</p>
      </div>
      <div className="h-64">
        {loading ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid stroke="hsl(0 0% 50% / 0.15)" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="var(--color-accent-2)" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
      {!loading && data?.length ? (
        <div className="mt-4 grid grid-cols-2 gap-4 text-xs sm:grid-cols-3">
          <div>Min: {data[0].min} B</div>
          <div>Max: {data[0].max} B</div>
          <div>Mean: {data[0].mean} B</div>
          <div>Median: {data[0].median} B</div>
          <div>95th: {data[0].p95} B</div>
        </div>
      ) : null}
    </Card>
  )
}
