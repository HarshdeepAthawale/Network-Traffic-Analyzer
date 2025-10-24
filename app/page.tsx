"use client"

import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { FileUpload } from "@/components/file-upload"

export default function Page() {
  const router = useRouter()
  return (
    <main className="min-h-dvh bg-network">
      <section className="mx-auto max-w-4xl px-4 py-12 md:py-20">
        <div className="mb-10 text-center">
          <motion.h1
            className="text-pretty text-3xl font-semibold tracking-tight md:text-4xl"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
          >
            Network Traffic Analyzer
          </motion.h1>
          <p className="mt-2 text-muted-foreground">
            Upload a PCAP or PCAPNG file to analyze network traffic, protocols, and packet details.
          </p>
        </div>

        <FileUpload
          onAnalyzed={() => router.push("/dashboard")}
          className="rounded-xl border bg-card/60 p-6 backdrop-blur"
        />

      </section>
    </main>
  )
}
