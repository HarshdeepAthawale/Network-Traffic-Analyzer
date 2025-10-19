"use client"

import { Card } from "@/components/ui/card"
import { Activity, Server, Network, Timer, HardDrive } from "lucide-react"

type Overview = {
  totalPackets: number
  totalBytes: number
  uniqueIps: number
  uniqueMacs: number
  durationSec: number
}

export function CardStats({ loading, data }: { loading?: boolean; data?: Overview }) {
  const items = [
    { label: "Total Packets", value: data?.totalPackets, icon: Activity },
    { label: "Total Bytes", value: data ? formatBytes(data.totalBytes) : undefined, icon: HardDrive },
    { label: "Unique IPs", value: data?.uniqueIps, icon: Network },
    { label: "Unique MACs", value: data?.uniqueMacs, icon: Server },
    { label: "Duration", value: data ? `${data.durationSec}s` : undefined, icon: Timer },
  ]

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {items.map((it) => (
        <Card key={it.label} className="flex items-center gap-3 p-4">
          <it.icon className="h-5 w-5 text-brand" />
          <div>
            <p className="text-xs text-muted-foreground">{it.label}</p>
            <p className="text-lg font-semibold">{loading ? <span className="animate-pulse">...</span> : it.value}</p>
          </div>
        </Card>
      ))}
    </div>
  )
}

function formatBytes(bytes: number) {
  const units = ["B", "KB", "MB", "GB", "TB"]
  let i = 0
  let v = bytes
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024
    i++
  }
  return `${v.toFixed(2)} ${units[i]}`
}
