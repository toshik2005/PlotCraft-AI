"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Bell, Search, Sun, Moon, LogOut, Home, Users, Settings as SettingsIcon, User as UserIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { useTheme } from "@/components/ui/theme-provider"

interface NavbarProps {
  // Remove isDark and setIsDark props since we'll use the theme context
}

const PAGES = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Candidates", href: "/dashboard/candidates" },
  { name: "Settings", href: "/dashboard/settings" },
]

export function Navbar({}: NavbarProps) {
  const { theme, setTheme } = useTheme()
  const isDark = theme === "dark"
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [activePath, setActivePath] = useState("")

  useEffect(() => {
    setMounted(true)
    if (typeof window !== "undefined") {
      setActivePath(window.location.pathname)
    }
  }, [])

  const handleLogout = async () => {
    try {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      router.push("/login")
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  // Theme toggle buttons (Sun and Moon)
  const themeToggleButton = mounted ? (
    <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-2xl p-1">
      <Button
        size="icon"
        variant="ghost"
        aria-label="Light mode"
        className={`rounded-2xl transition-all duration-200 ${!isDark ? 'bg-yellow-200 dark:bg-yellow-300/20' : ''}`}
        onClick={() => setTheme("light")}
      >
        <Sun className={`h-4 w-4 ${!isDark ? 'text-yellow-500' : 'text-gray-400'}`} />
      </Button>
      <Button
        size="icon"
        variant="ghost"
        aria-label="Dark mode"
        className={`rounded-2xl transition-all duration-200 ${isDark ? 'bg-purple-900/20 dark:bg-purple-900/40' : ''}`}
        onClick={() => setTheme("dark")}
      >
        <Moon className={`h-4 w-4 ${isDark ? 'text-purple-600' : 'text-gray-400'}`} />
      </Button>
    </div>
  ) : (
    <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-2xl p-1">
      <div className="h-4 w-4"></div>
      <div className="w-8 h-4 bg-gray-300 rounded-full"></div>
      <div className="h-4 w-4"></div>
    </div>
  )

  const headerBg = "bg-white/80 dark:bg-[#111111]/80"
  const borderColor = "border-gray-200/50 dark:border-gray-800/50"

  return (
    <>
      <header
        className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50 flex flex-col items-center pl-6 pr-6 py-3 backdrop-blur-sm rounded-full border ${borderColor} ${headerBg} w-[calc(100%-2rem)] sm:w-auto transition-[border-radius] duration-300 ease-in-out`}
      >
        <div className="flex items-center justify-between w-full gap-x-6 sm:gap-x-8">
          {/* Logo */}
          <Link href="/dashboard" className="font-mono text-lg font-bold text-primary">
            &lt;querysure&gt;
          </Link>

          {/* Page Links Bar (Desktop Only) */}
          <nav className="hidden md:flex gap-4 ml-8">
            {PAGES.map((page) => (
              <Link
                key={page.name}
                href={page.href}
                className="px-3 py-1 rounded-xl transition-colors font-medium text-gray-800 hover:text-purple-600 dark:text-gray-200 dark:hover:text-purple-400"
              >
                {page.name}
              </Link>
            ))}
          </nav>

          {/* Right Side Icons */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Desktop: Search, Theme, Logout */}
            <Button
              size="icon"
              variant="ghost"
              className="hidden md:flex rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              aria-label="Search"
            >
              <Search className="h-5 w-5" />
            </Button>

            {/* Desktop: Profile */}
            <Link href="/profile">
              <Button
                size="icon"
                variant="ghost"
                className="hidden md:flex rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                aria-label="Profile"
              >
                <UserIcon className="h-5 w-5" />
              </Button>
            </Link>

            <div className="hidden md:flex">{themeToggleButton}</div>

            <Button
              size="icon"
              variant="ghost"
              className="hidden md:flex rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              aria-label="Sign out"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
            </Button>

            {/* Mobile: Search, Notification, Logout */}
            <Button
              size="icon"
              variant="ghost"
              className="md:hidden rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              aria-label="Search"
            >
              <Search className="h-5 w-5" />
            </Button>

            {/* Mobile: Profile */}
            <Link href="/profile" className="md:hidden">
              <Button
                size="icon"
                variant="ghost"
                className="rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                aria-label="Profile"
              >
                <UserIcon className="h-5 w-5" />
              </Button>
            </Link>

            <Button
              size="icon"
              variant="ghost"
              className="md:hidden rounded-2xl transition-all duration-200 relative text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-purple-600 rounded-full"></span>
            </Button>

            <Button
              size="icon"
              variant="ghost"
              className="md:hidden rounded-2xl transition-all duration-200 text-gray-700 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              aria-label="Sign out"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 bg-white dark:bg-[#111111] border-t border-gray-200 dark:border-gray-800 flex justify-around py-1 shadow-t">
        <Link href="/dashboard" className={`flex flex-col items-center flex-1 py-2 transition-colors duration-200 ${
          activePath === "/dashboard" 
            ? "text-purple-600" 
            : "text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100"
        }`}>
          <Home className="h-6 w-6 mb-0.5" />
          <span className="text-xs">Dashboard</span>
        </Link>
        <Link href="/dashboard/candidates" className={`flex flex-col items-center flex-1 py-2 transition-colors duration-200 ${
          activePath === "/dashboard/candidates" 
            ? "text-purple-600" 
            : "text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100"
        }`}>
          <Users className="h-6 w-6 mb-0.5" />
          <span className="text-xs">Candidates</span>
        </Link>
        <Link href="/profile" className={`flex flex-col items-center flex-1 py-2 transition-colors duration-200 ${
          activePath === "/profile" 
            ? "text-purple-600" 
            : "text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100"
        }`}>
          <UserIcon className="h-6 w-6 mb-0.5" />
          <span className="text-xs">Profile</span>
        </Link>
        <Link href="/dashboard/settings" className={`flex flex-col items-center flex-1 py-2 transition-colors duration-200 ${
          activePath === "/dashboard/settings" 
            ? "text-purple-600" 
            : "text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100"
        }`}>
          <SettingsIcon className="h-6 w-6 mb-0.5" />
          <span className="text-xs">Settings</span>
        </Link>
      </nav>
    </>
  )
}
