"use client"
import { Card } from "@/components/ui/card"

type Props = {
  onSetIp: (ip: string) => void
  onClearFilters: () => void
}

export function Sidebar({ onSetIp, onClearFilters }: Props) {
  return (
    <aside className="hidden border-r md:block">
      <div className="flex h-dvh flex-col gap-4 p-4">
      </div>
    </aside>
  )
}
