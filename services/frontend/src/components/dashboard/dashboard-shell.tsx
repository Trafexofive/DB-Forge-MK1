"use client"

import { ReactNode, useState } from "react"
import { 
  Database, 
  Menu, 
  Settings, 
  Activity, 
  Users,
  Shield,
  BarChart3,
  FileText
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"

interface DashboardShellProps {
  children: ReactNode
}

const navigation = [
  { name: "Overview", href: "/", icon: BarChart3, current: true },
  { name: "Databases", href: "/databases", icon: Database, current: false },
  { name: "Connections", href: "/connections", icon: Activity, current: false },
  { name: "Users", href: "/users", icon: Users, current: false },
  { name: "Security", href: "/security", icon: Shield, current: false },
  { name: "Logs", href: "/logs", icon: FileText, current: false },
  { name: "Settings", href: "/settings", icon: Settings, current: false },
]

export function DashboardShell({ children }: DashboardShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      <div className="flex h-screen">
        {/* Desktop Sidebar */}
        <div className="hidden md:flex md:w-64 md:flex-col">
          <div className="flex flex-col flex-1 min-h-0 border-r border-border">
            <div className="flex items-center h-16 px-6 border-b border-border">
              <Database className="w-8 h-8 text-primary" />
              <span className="ml-3 text-xl font-bold">DB-Forge</span>
            </div>
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <nav className="mt-5 flex-1 px-4 space-y-1">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      item.current
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    }`}
                  >
                    <item.icon
                      className={`mr-3 h-5 w-5 ${
                        item.current
                          ? "text-primary-foreground"
                          : "text-muted-foreground group-hover:text-accent-foreground"
                      }`}
                    />
                    {item.name}
                  </a>
                ))}
              </nav>
            </div>
          </div>
        </div>

        {/* Mobile Sidebar */}
        <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <SheetTrigger asChild>
            <Button
              variant="outline"
              size="icon"
              className="md:hidden fixed top-4 left-4 z-50"
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-64">
            <div className="flex flex-col h-full">
              <div className="flex items-center h-16 px-6 border-b border-border">
                <Database className="w-8 h-8 text-primary" />
                <span className="ml-3 text-xl font-bold">DB-Forge</span>
              </div>
              <nav className="flex-1 px-4 pt-5 space-y-1">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      item.current
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    }`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon
                      className={`mr-3 h-5 w-5 ${
                        item.current
                          ? "text-primary-foreground"
                          : "text-muted-foreground group-hover:text-accent-foreground"
                      }`}
                    />
                    {item.name}
                  </a>
                ))}
              </nav>
            </div>
          </SheetContent>
        </Sheet>

        {/* Main Content */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Top Bar */}
          <header className="h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center h-full px-6">
              <div className="flex items-center space-x-4 ml-auto">
                <Badge variant="secondary" className="text-xs">
                  System Healthy
                </Badge>
                <Button variant="ghost" size="sm">
                  Admin Panel
                </Button>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 overflow-auto">
            <div className="p-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}