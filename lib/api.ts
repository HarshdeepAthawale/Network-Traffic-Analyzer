// Backend API URL - update this to match your backend server
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchJSON<T = any>(url: string): Promise<T> {
  try {
    // Handle both relative and absolute URLs
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
    
    const res = await fetch(fullUrl, { 
      cache: "no-store",
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Failed to fetch ${url}: ${error}`)
    }
    
    return res.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Failed to connect to server. Please check if the backend is running.')
    }
    throw error
  }
}

export async function uploadFile(file: File): Promise<{ success: boolean; fileId: string; message: string }> {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    // Create an AbortController for timeout
    const controller = new AbortController()
    // Increased timeout to 5 minutes for large PCAP files
    const timeoutId = setTimeout(() => controller.abort(), 300000) // 300 second (5 minute) timeout
    
    const res = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    })
    
    clearTimeout(timeoutId)
    
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Upload failed: ${error}`)
    }
    
    return res.json()
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Failed to connect to server. Please check if the backend is running.')
    }
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Upload timed out. The file may be too large (max 500MB) or the server may be processing a large number of packets. Please try a smaller file or wait longer.')
    }
    throw error
  }
}