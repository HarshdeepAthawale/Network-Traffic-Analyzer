"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"

export function ThemeToggle({
  lightIcon,
  darkIcon,
}: {
  lightIcon?: React.ReactNode
  darkIcon?: React.ReactNode
}) {
  const [dark, setDark] = React.useState(true)

  React.useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark")
    setDark(isDark)
  }, [])

  function toggle() {
    const el = document.documentElement
    const isDark = el.classList.toggle("dark")
    setDark(isDark)
  }

  return (
    <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
      {dark ? lightIcon : darkIcon}
    </Button>
  )
}
