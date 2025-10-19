"use client"

import useSWR from "swr"
import { fetchJSON } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useMemo, useState } from "react"

type Row = {
  ip: string
  mac: string
  host: string
  packets: number
  bytes: number
  vendor?: string
  user_name?: string
}

export function IpMacTable({ protocol, filterIp }: { protocol: string | null; filterIp: string }) {
  const { data, isLoading } = useSWR("/api/ip-mac-map", fetchJSON, { revalidateOnFocus: false })
  const [q, setQ] = useState("")

  const items = useMemo(() => {
    const list: Row[] = data?.items || []
    return list
      .filter((r) => (filterIp ? r.ip.includes(filterIp) : true))
      .filter((r) => (q ? r.ip.includes(q) || r.host?.toLowerCase().includes(q.toLowerCase()) || r.user_name?.toLowerCase().includes(q.toLowerCase()) : true))
      .sort((a, b) => b.packets - a.packets)
  }, [data, q, filterIp])

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between p-4">
        <div>
          <h3 className="text-sm font-medium">IP–MAC–Host–User</h3>
          <p className="text-xs text-muted-foreground">Sortable & searchable</p>
        </div>
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search IP, host, or user..."
          className="h-8 w-48"
        />
      </div>
      <div className="max-h-80 overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-background">
            <tr className="text-left">
              <th className="px-4 py-2">IP Address</th>
              <th className="px-4 py-2">MAC Address</th>
              <th className="px-4 py-2">Hostname</th>
              <th className="px-4 py-2">User</th>
              <th className="px-4 py-2">Packets</th>
              <th className="px-4 py-2">Bytes</th>
              <th className="px-4 py-2">Vendor</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td className="px-4 py-3 text-muted-foreground" colSpan={7}>
                  Loading...
                </td>
              </tr>
            ) : items.length ? (
              items.map((r) => (
                <tr key={r.ip} className="border-t">
                  <td className="px-4 py-2">{r.ip}</td>
                  <td className="px-4 py-2">{r.mac}</td>
                  <td className="px-4 py-2">{r.host}</td>
                  <td className="px-4 py-2 font-medium text-blue-600">{r.user_name || "-"}</td>
                  <td className="px-4 py-2">{r.packets}</td>
                  <td className="px-4 py-2">{r.bytes}</td>
                  <td className="px-4 py-2">{r.vendor || "-"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-3 text-muted-foreground" colSpan={7}>
                  {isLoading ? "Loading..." : "No IP-MAC mappings found. Upload a PCAP file to see network devices."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
