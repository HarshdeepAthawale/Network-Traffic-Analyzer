"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"

type Point = { t: string; pps: number; bps: number }

export function PpsGraph({ data, loading }: { data: Point[]; loading?: boolean }) {
  const [live, setLive] = React.useState(false)

  React.useEffect(() => {
    let id: any
    if (live) {
      id = setInterval(() => {
        // noop: SWR revalidation could be triggered here if needed
      }, 2000)
    }
    return () => clearInterval(id)
  }, [live])

  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium">Packets per Second</h3>
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`inline-block h-2 w-2 rounded-full ${live ? "bg-brand animate-pulse" : "bg-muted-foreground/40"}`}
            aria-hidden
          />
          Live
          <Switch checked={live} onCheckedChange={setLive} aria-label="Toggle live mode" />
        </div>
      </div>
      <div className="h-64">
        {loading ? (
          <div className="flex h-full items-center justify-center text-muted-foreground">Loading...</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="g1" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-brand)" stopOpacity={0.7} />
                  <stop offset="100%" stopColor="var(--color-brand)" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="hsl(0 0% 50% / 0.15)" />
              <XAxis dataKey="t" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Area type="monotone" dataKey="pps" stroke="var(--color-brand)" fill="url(#g1)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
