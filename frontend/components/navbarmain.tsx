"use client"

import React, { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Bell, Search, TrendingUp, Users, FileText, Calendar, Sun, Moon, Settings, ChevronDown, LogOut, Home, Menu, X } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Switch } from "@/components/ui/switch"
import { useTheme } from "@/components/ui/theme-provider"

// Animated link component for the navbar
const AnimatedNavLink = ({ href, children, active = false }: { href: string; children: React.ReactNode; active?: boolean }) => {
  const defaultTextColor = active ? 'text-foreground' : 'text-muted-foreground'
  const hoverTextColor = 'text-foreground'
  const textSizeClass = 'text-sm'

  return (
    <Link href={href} className={`group relative inline-block overflow-hidden h-5 flex items-center ${textSizeClass}`}>
      <div className="flex flex-col transition-transform duration-400 ease-out transform group-hover:-translate-y-1/2">
        <span className={defaultTextColor}>{children}</span>
        <span className={hoverTextColor}>{children}</span>
      </div>
    </Link>
  )
}

interface NavbarProps {
  searchQuery: string
  setSearchQuery: (query: string) => void
}

export function Navbar({ searchQuery, setSearchQuery }: NavbarProps) {
  const { theme, setTheme } = useTheme()
  const isDark = theme === "dark"
  const [isOpen, setIsOpen] = useState(false)
  const [headerShapeClass, setHeaderShapeClass] = useState('rounded-full')
  const shapeTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  // Ensure client-side only rendering for hydration-sensitive parts
  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogout = async () => {
    try {
      // Add your logout logic here
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  useEffect(() => {
    if (shapeTimeoutRef.current) {
      clearTimeout(shapeTimeoutRef.current)
    }

    if (isOpen) {
      setHeaderShapeClass('rounded-xl')
    } else {
      shapeTimeoutRef.current = setTimeout(() => {
        setHeaderShapeClass('rounded-full')
      }, 300)
    }

    return () => {
      if (shapeTimeoutRef.current) {
        clearTimeout(shapeTimeoutRef.current)
      }
    }
  }, [isOpen])

  // Close menu when clicking outside on mobile
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as HTMLElement
      if (isOpen && !target.closest('.mobile-menu') && !target.closest('.menu-button')) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  const themeToggleButton = mounted ? (
    <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-2xl p-1">
      <Sun className="h-4 w-4 text-gray-600 dark:text-gray-400" />
      <Switch 
        checked={isDark} 
        onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")} 
        className="data-[state=checked]:bg-purple-600" 
      />
      <Moon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
    </div>
  ) : (
    <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-2xl p-1">
      <div className="h-4 w-4"></div>
      <div className="w-8 h-4 bg-gray-300 rounded-full"></div>
      <div className="h-4 w-4"></div>
    </div>
  )

  const navLinksData = [
    { label: 'Dashboard', href: '/dashboard', icon: TrendingUp, active: true },
    { label: 'Candidates', href: '/candidates', icon: Users, active: false },
    { label: 'Vault', href: '/vault', icon: FileText, active: false },
    { label: 'Schedule', href: '/schedule', icon: Calendar, active: false },
  ]

  return (
    <header className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50
                       flex flex-col items-center
                       pl-6 pr-6 py-3 backdrop-blur-sm
                       ${headerShapeClass}
                       border border-border bg-card/60
                       w-[calc(100%-2rem)] sm:w-auto
                       transition-[border-radius] duration-300 ease-in-out`}>

      <div className="flex items-center justify-between w-full gap-x-6 sm:gap-x-8">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="font-mono text-lg font-bold text-primary">
            &lt;querysure&gt;
          </Link>
        </div>

        <nav className="hidden lg:flex items-center space-x-4 sm:space-x-6 text-sm">
          {navLinksData.map((link) => (
            <AnimatedNavLink key={link.href} href={link.href} active={link.active}>
              <div className="flex items-center gap-2">
                <link.icon className="h-4 w-4" />
                {link.label}
              </div>
            </AnimatedNavLink>
          ))}
        </nav>

        {/* Desktop Search */}
        <div className="relative hidden md:block">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500 dark:text-gray-400"
          />
          <Input
            placeholder="Search candidates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 w-60 lg:w-80 border-0 rounded-2xl transition-all duration-200 bg-gray-100 text-gray-900 placeholder:text-gray-500 focus-visible:ring-purple-500 focus-visible:ring-2 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-400"
          />
        </div>

        <div className="hidden sm:flex items-center gap-2 sm:gap-3">
          {themeToggleButton}
          
          {/* Notifications */}
          <Button
            size="icon"
            variant="ghost"
            className="rounded-2xl transition-all duration-200 relative text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-purple-600 rounded-full"></span>
          </Button>

          {/* Profile Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2 px-2 md:px-3 rounded-2xl">
                <Avatar className="h-7 w-7">
                  <AvatarImage src="/placeholder.svg?height=28&width=28" />
                  <AvatarFallback className="bg-purple-600 text-white text-xs">HR</AvatarFallback>
                </Avatar>
                <ChevronDown className="h-4 w-4 hidden md:block" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="rounded-2xl bg-white border-gray-200 dark:bg-gray-900 dark:border-gray-800"
            >
              <DropdownMenuItem
                className="rounded-xl text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={handleLogout}
                className="rounded-xl text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="sm:hidden flex items-center gap-2">
          {themeToggleButton}
          
          {/* Mobile Notifications */}
          <Button
            size="icon"
            variant="ghost"
            className="rounded-2xl transition-all duration-200 relative text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-purple-600 rounded-full"></span>
          </Button>

          {/* Mobile Profile */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2 px-2 rounded-2xl">
                <Avatar className="h-7 w-7">
                  <AvatarImage src="/placeholder.svg?height=28&width=28" />
                  <AvatarFallback className="bg-purple-600 text-white text-xs">HR</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="rounded-2xl bg-white border-gray-200 dark:bg-gray-900 dark:border-gray-800"
            >
              <DropdownMenuItem
                className="rounded-xl text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={handleLogout}
                className="rounded-xl text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <button 
            className="menu-button flex items-center justify-center w-8 h-8 text-muted-foreground focus:outline-none" 
            onClick={toggleMenu} 
            aria-label={isOpen ? 'Close Menu' : 'Open Menu'}
          >
            {isOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      <div className={`mobile-menu sm:hidden flex flex-col items-center w-full transition-all ease-in-out duration-300 overflow-hidden
                       ${isOpen ? 'max-h-[1000px] opacity-100 pt-4' : 'max-h-0 opacity-0 pt-0 pointer-events-none'}`}>
        
        {/* Mobile Search */}
        <div className="relative w-full mb-4">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500 dark:text-gray-400"
          />
          <Input
            placeholder="Search candidates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 w-full border-0 rounded-2xl transition-all duration-200 bg-gray-100 text-gray-900 placeholder:text-gray-500 focus-visible:ring-purple-500 focus-visible:ring-2 dark:bg-gray-800 dark:text-white dark:placeholder:text-gray-400"
          />
        </div>

        <nav className="flex flex-col items-center space-y-4 text-base w-full">
          {navLinksData.map((link) => (
            <Link 
              key={link.href} 
              href={link.href} 
              className={`flex items-center gap-3 transition-colors w-full text-center py-2 ${
                link.active 
                  ? "text-foreground" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
              onClick={() => setIsOpen(false)}
            >
              <link.icon className="h-5 w-5" />
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
