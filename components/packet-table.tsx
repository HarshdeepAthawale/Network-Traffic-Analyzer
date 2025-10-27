"use client"

import * as React from "react"
import useSWRInfinite from "swr/infinite"
import { fetchJSON } from "@/lib/api"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"

type Packet = {
  id: string
  ts: string
  src: string
  dst: string
  proto: string
  size: number
  info: string
  layers?: Record<string, any>
  hex?: string
}

const PAGE_SIZE = 25
const getKey = (pageIndex: number, previousPageData: any, q: string) => {
  if (previousPageData && !previousPageData.items.length) return null
  const page = pageIndex + 1
  return `/api/packets?page=${page}&perPage=${PAGE_SIZE}${q}`
}

export function PacketTable({ protocol, filterIp }: { protocol: string | null; filterIp: string }) {
  const q = [
    protocol ? `&protocol=${encodeURIComponent(protocol)}` : "",
    filterIp ? `&ip=${encodeURIComponent(filterIp)}` : "",
  ].join("")
  const { data, size, setSize, isValidating } = useSWRInfinite((i, prev) => getKey(i, prev, q), fetchJSON, {
    revalidateOnFocus: false,
  })
  const items: Packet[] = (data || []).flatMap((p) => p.items)

  const [open, setOpen] = React.useState(false)
  const [selected, setSelected] = React.useState<Packet | null>(null)

  function openPacket(p: Packet) {
    setSelected(p)
    setOpen(true)
  }

  const hasMore = (data?.[data.length - 1]?.items?.length || 0) === PAGE_SIZE

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between p-4">
        <div>
          <h3 className="text-sm font-medium">Packet List</h3>
          <p className="text-xs text-muted-foreground">Timestamp | Source | Destination | Protocol | Size | Info</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => setSize(size + 1)} disabled={isValidating || !hasMore}>
          {hasMore ? "Load more" : "No more"}
        </Button>
      </div>
      <div className="max-h-[500px] overflow-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-background">
            <tr className="text-left">
              <th className="px-4 py-2">Timestamp</th>
              <th className="px-4 py-2">Source IP</th>
              <th className="px-4 py-2">Destination IP</th>
              <th className="px-4 py-2">Protocol</th>
              <th className="px-4 py-2">Size</th>
              <th className="px-4 py-2">Info</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map((p) => (
                <tr key={p.id} className="cursor-pointer border-t hover:bg-accent/20" onClick={() => openPacket(p)}>
                  <td className="px-4 py-2">{p.ts}</td>
                  <td className="px-4 py-2">{p.src}</td>
                  <td className="px-4 py-2">{p.dst}</td>
                  <td className="px-4 py-2">{p.proto}</td>
                  <td className="px-4 py-2">{p.size}</td>
                  <td className="px-4 py-2">{p.info}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-3 text-muted-foreground" colSpan={6}>
                  {isValidating ? "Loading..." : "No packets found. Upload a PCAP file to see packet data."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="right" className="w-[90vw] max-w-3xl">
          <SheetHeader>
            <SheetTitle>Packet Details</SheetTitle>
          </SheetHeader>
          {selected ? (
            <div className="mt-6 space-y-6">
              {/* Summary Section */}
              <div className="rounded-lg border bg-card p-4">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-xs text-muted-foreground">Timestamp</div>
                    <div className="mt-1 font-medium">{selected.ts}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Protocol</div>
                    <div className="mt-1 font-medium">{selected.proto}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Source IP</div>
                    <div className="mt-1 font-medium">{selected.src}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Destination IP</div>
                    <div className="mt-1 font-medium">{selected.dst}</div>
                  </div>
                  <div className="col-span-2">
                    <div className="text-xs text-muted-foreground">Size</div>
                    <div className="mt-1 font-medium">{selected.size} B</div>
                  </div>
                </div>
              </div>

              {/* Layers Section */}
              <div className="rounded-lg border bg-card p-4">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Layers</h3>
                <div className="max-h-64 overflow-auto rounded bg-muted/30 p-3">
                  <pre className="text-xs font-mono">
                    {JSON.stringify(selected.layers || { ethernet: {}, ip: {}, transport: {}, app: {} }, null, 2)}
                  </pre>
                </div>
              </div>

              {/* Hex Section */}
              <div className="rounded-lg border bg-card p-4">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Hex</h3>
                <div className="max-h-64 overflow-auto rounded bg-muted/30 p-3">
                  <pre className="text-xs font-mono">
                    {selected.hex || "0000  ff aa bb cc dd ee ..."}
                  </pre>
                </div>
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </Card>
  )
}
