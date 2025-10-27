"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { uploadFile } from "@/lib/api"
import { Upload, FileUp, CheckCircle2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

type Props = {
  onAnalyzed?: () => void
  className?: string
}

export function FileUpload({ onAnalyzed, className }: Props) {
  const [dragOver, setDragOver] = React.useState(false)
  const [file, setFile] = React.useState<File | null>(null)
  const [progress, setProgress] = React.useState(0)
  const [uploading, setUploading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  async function handleFiles(files: FileList | null) {
    if (!files || !files[0]) return
    const f = files[0]
    setFile(f)
    setError(null)
    
    // Don't auto-upload - let user click "Analyze Now"
    // await uploadFileToBackend(f)
  }

  async function uploadFileToBackend(file: File) {
    try {
      setUploading(true)
      setProgress(0)
      setError(null)
      
      // Show initial progress
      setProgress(10)
      
      // Upload file with progress updates
      const result = await uploadFile(file)
      
      if (result.success) {
        // Show upload success
        setProgress(100)
        
        // Navigate to dashboard after delay
        if (onAnalyzed) {
          setTimeout(() => {
            onAnalyzed()
            setUploading(false)
          }, 400)
        } else {
          setUploading(false)
        }
      }
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'Upload failed')
      setProgress(0)
      setUploading(false)
    }
  }

  return (
    <div className={cn("w-full", className)}>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFiles(e.dataTransfer.files)
        }}
        className={cn(
          "flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-colors",
          dragOver ? "border-brand bg-brand/5" : "border-border hover:bg-accent/10",
        )}
        onClick={() => document.getElementById("fileInput")?.click()}
        role="button"
        aria-label="Upload PCAP or PCAPNG"
        title="Upload PCAP or PCAPNG"
      >
        <Upload className="mb-3 h-8 w-8 text-brand" aria-hidden />
        <p className="text-center">
          Drag and drop .pcap / .pcapng here
          <br />
          <span className="text-sm text-muted-foreground">or click to browse</span>
        </p>
        <input
          id="fileInput"
          type="file"
          accept=".pcap,.pcapng"
          className="sr-only"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      <div className="mt-4 rounded-lg border p-4">
        {file ? (
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <FileUp className="h-5 w-5 text-accent-1" aria-hidden />
              <div className="text-sm">
                <p className="font-medium">{file.name}</p>
                <p className="text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              {progress === 100 && (
                <span className="ml-auto inline-flex items-center gap-1 text-sm text-brand">
                  <CheckCircle2 className="h-4 w-4" /> Ready
                </span>
              )}
            </div>
            <Progress value={progress} aria-label="Upload progress" />
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No file selected yet.</p>
        )}
        <div className="mt-4 flex justify-end">
          <Button
            disabled={!file || uploading}
            className="bg-brand text-background hover:bg-brand/90"
            onClick={() => file && uploadFileToBackend(file)}
          >
            {uploading ? "Uploading..." : "Analyze Now"}
          </Button>
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Upload Error</span>
          </div>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}
    </div>
  )
}
