"use client"
import { Sun, Moon, FileJson, FileDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

type Props = {
  fileName: string
  sizeBytes: number
}

export function Navbar({ fileName, sizeBytes }: Props) {
  return (
    <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between px-4 py-3 md:px-6">
        <div className="min-w-0">
          <h2 className="truncate text-lg font-semibold">{fileName}</h2>
          <p className="truncate text-sm text-muted-foreground">
            Size {(sizeBytes / 1024 / 1024).toFixed(2)} MB • Network capture analysis
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle lightIcon={<Sun className="h-5 w-5" />} darkIcon={<Moon className="h-5 w-5" />} />
          <Button
            variant="outline"
            size="sm"
            onClick={() => exportEndpoint("/api/summary", "summary.json")}
            className="hidden sm:inline-flex"
          >
            <FileJson className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => exportEndpoint("/api/packets?perPage=100", "packets.csv", "csv")}
            className="hidden sm:inline-flex"
          >
            <FileDown className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>
    </header>
  )
}

async function exportEndpoint(url: string, filename: string, type: "json" | "csv" = "json") {
  try {
    // Use backend API URL
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
    
    let data: any
    
    if (type === "csv" && url.includes("/api/packets")) {
      // For CSV export of packets, fetch all pages
      data = await fetchAllPackets(API_BASE_URL, url)
    } else {
      // Single request for JSON or other endpoints
      const res = await fetch(fullUrl)
      
      if (!res.ok) {
        const error = await res.text()
        throw new Error(`Failed to export: ${error}`)
      }
      
      data = await res.json()
    }
    
    let blob: Blob
    
    if (type === "csv") {
      const rows: string[] = []
      const items = Array.isArray(data?.items) ? data.items : []
      if (items.length) {
        // For packets, flatten the structure and exclude complex nested objects
        const firstItem = items[0]
        let headers: string[]
        
        if (firstItem.id && firstItem.ts && firstItem.proto) {
          // Packet CSV - use specific fields
          headers = ["id", "ts", "src", "dst", "proto", "size", "info"]
        } else {
          // Generic CSV - use all keys except complex objects
          headers = Object.keys(firstItem).filter(key => {
            const value = firstItem[key]
            return typeof value !== "object" || value === null
          })
        }
        
        rows.push(headers.join(","))
        for (const row of items) {
          rows.push(headers.map((h) => {
            const value = row[h]
            if (value === null || value === undefined) return '""'
            if (typeof value === "string") {
              // Escape quotes and wrap in quotes
              return `"${value.replace(/"/g, '""')}"`
            }
            return JSON.stringify(value)
          }).join(","))
        }
      }
      blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" })
    } else {
      blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
    }
    
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = filename
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error("Export failed:", error)
    alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

async function fetchAllPackets(apiBaseUrl: string, baseUrl: string): Promise<any> {
  const allItems: any[] = []
  let page = 1
  let total = 0
  
  while (true) {
    const url = `${apiBaseUrl}${baseUrl}&page=${page}`
    const res = await fetch(url)
    
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Failed to fetch page ${page}: ${error}`)
    }
    
    const data = await res.json()
    
    if (data.items && data.items.length > 0) {
      allItems.push(...data.items)
      total = data.total
      
      // Check if we've got all packets
      if (allItems.length >= total) {
        break
      }
      
      page++
    } else {
      break
    }
  }
  
  return {
    items: allItems,
    total: allItems.length,
    page: 1,
    per_page: allItems.length
  }
}
