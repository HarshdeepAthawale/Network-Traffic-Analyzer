"use client"

import * as React from "react"
import useSWR from "swr"
import { fetchJSON } from "@/lib/api"
import { Navbar } from "@/components/navbar"
import { CardStats } from "@/components/card-stats"
import { ProtocolChart } from "@/components/protocol-chart"
import { PpsGraph } from "@/components/pps-graph"
import { PacketSizeChart } from "@/components/packet-size-chart"
import { IpMacTable } from "@/components/ip-mac-table"
import { PacketTable } from "@/components/packet-table"
import { FiltersSection } from "@/components/filters-section"

export default function DashboardPage() {
  const [selectedProtocol, setSelectedProtocol] = React.useState<string | null>(null)
  const [filterIp, setFilterIp] = React.useState<string>("")

  const {
    data: summary,
    isLoading,
    error,
    mutate,
  } = useSWR("/api/summary", fetchJSON, {
    revalidateOnFocus: false,
    refreshInterval: 0,
    dedupingInterval: 0,
  })

  // Get file info from summary data
  const fileInfo = summary?.overview ? {
    fileName: "Network Capture",
    sizeBytes: summary.overview.totalBytes
  } : {
    fileName: "No file uploaded",
    sizeBytes: 0
  }

  return (
    <div className="min-h-dvh">
      <main className="bg-network/30">
        <Navbar
          fileName={fileInfo.fileName}
          sizeBytes={fileInfo.sizeBytes}
        />
        <div className="mx-auto max-w-[1400px] gap-6 p-4 md:p-6">
          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
              <h3 className="text-lg font-semibold text-red-800">No Data Available</h3>
              <p className="mt-2 text-red-600">
                Please upload a PCAP file first to see network analysis.
              </p>
              <p className="mt-1 text-sm text-red-500">
                Error: {error.message || "Failed to load data"}
              </p>
            </div>
          ) : (
            <>
              <CardStats loading={isLoading} data={summary?.overview} />

              <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
                <ProtocolChart
                  loading={isLoading}
                  data={summary?.protocolDistribution || []}
                  selected={selectedProtocol}
                  onSelect={(p) => setSelectedProtocol((prev) => (prev === p ? null : p))}
                />
                <PpsGraph loading={isLoading} data={summary?.pps || []} />
              </div>

              <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
                <PacketSizeChart loading={isLoading} data={summary?.sizeHistogram || []} />
                <IpMacTable protocol={selectedProtocol} filterIp={filterIp} />
              </div>

              <div className="mt-6">
                <PacketTable protocol={selectedProtocol} filterIp={filterIp} />
              </div>

              <FiltersSection
                filterIp={filterIp}
                onSetIp={setFilterIp}
                onClearFilters={() => {
                  setFilterIp("")
                  setSelectedProtocol(null)
                }}
              />
            </>
          )}
        </div>
      </main>
    </div>
  )
}
