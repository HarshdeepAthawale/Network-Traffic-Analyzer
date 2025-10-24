"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

type Props = {
  filterIp: string
  onSetIp: (ip: string) => void
  onClearFilters: () => void
}

export function FiltersSection({ filterIp, onSetIp, onClearFilters }: Props) {
  const [ip, setIp] = React.useState(filterIp)

  React.useEffect(() => {
    setIp(filterIp)
  }, [filterIp])

  return (
    <div className="mt-8">
      <Card className="p-4">
        <p className="mb-3 text-sm font-medium">IP Address Filter</p>
        <div className="space-y-3">
          <Input placeholder="e.g. 192.168.0.1" value={ip} onChange={(e) => setIp(e.target.value)} />
          <div className="flex gap-2">
            <Button size="sm" onClick={() => onSetIp(ip)} className="bg-brand text-background">
              Apply
            </Button>
            <Button size="sm" variant="outline" onClick={onClearFilters}>
              Clear
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
