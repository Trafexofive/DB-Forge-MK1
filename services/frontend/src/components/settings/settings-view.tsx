"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Settings, 
  RefreshCw,
  Save,
  Server,
  Database,
  Shield,
  Bell,
  Palette,
  Info,
  AlertTriangle,
  CheckCircle,
  AlertCircle
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface SystemSettings {
  system_name: string
  version: string
  uptime: number
  api_key: string
  max_databases: number
  auto_cleanup: boolean
  backup_enabled: boolean
  log_level: string
  theme: string
}

export function SettingsView() {
  const [settings, setSettings] = useState<SystemSettings>({
    system_name: 'DB-Forge MK1',
    version: '1.0.0',
    uptime: 0,
    api_key: 'development-api-key-12345',
    max_databases: 10,
    auto_cleanup: false,
    backup_enabled: false,
    log_level: 'INFO',
    theme: 'light'
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Get system stats for uptime
      const stats = await apiClient.getSystemStats()
      
      // Update settings with real data where available
      setSettings(prev => ({
        ...prev,
        uptime: Math.floor(stats.uptime_seconds || 0)
      }))
      
    } catch (err) {
      console.error('Failed to fetch settings:', err)
      setError(err instanceof Error ? err.message : 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    try {
      setSaveStatus('saving')
      
      // In a real implementation, this would call an API endpoint to save settings
      // For now, we'll simulate a save operation
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
      
    } catch (err) {
      console.error('Failed to save settings:', err)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    }
  }

  useEffect(() => {
    fetchSettings()
    const interval = setInterval(fetchSettings, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const getSaveStatusButton = () => {
    switch (saveStatus) {
      case 'saving':
        return (
          <Button disabled>
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            Saving...
          </Button>
        )
      case 'saved':
        return (
          <Button className="bg-green-600 hover:bg-green-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            Saved!
          </Button>
        )
      case 'error':
        return (
          <Button variant="destructive">
            <AlertCircle className="w-4 h-4 mr-2" />
            Error
          </Button>
        )
      default:
        return (
          <Button onClick={saveSettings}>
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        )
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span>Error: {error}</span>
            <Button variant="outline" size="sm" onClick={fetchSettings}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <Server className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Online</div>
            <p className="text-xs text-muted-foreground">
              Uptime: {formatUptime(settings.uptime)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Version</CardTitle>
            <Info className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{settings.version}</div>
            <p className="text-xs text-muted-foreground">
              {settings.system_name}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configuration</CardTitle>
            <Settings className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Development</div>
            <p className="text-xs text-muted-foreground">
              Mode & Environment
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="database">Database</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>
          <div className="flex space-x-2">
            <Button onClick={fetchSettings} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            {getSaveStatusButton()}
          </div>
        </div>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Basic system configuration and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">System Name</label>
                  <Input
                    value={settings.system_name}
                    onChange={(e) => setSettings(prev => ({ ...prev, system_name: e.target.value }))}
                    placeholder="DB-Forge MK1"
                  />
                  <p className="text-xs text-muted-foreground">
                    Display name for your DB-Forge instance
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Theme</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={settings.theme}
                    onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value }))}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="auto">Auto (System)</option>
                  </select>
                  <p className="text-xs text-muted-foreground">
                    Interface color scheme
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Log Level</label>
                  <select 
                    className="w-full p-2 border rounded-md"
                    value={settings.log_level}
                    onChange={(e) => setSettings(prev => ({ ...prev, log_level: e.target.value }))}
                  >
                    <option value="DEBUG">Debug</option>
                    <option value="INFO">Info</option>
                    <option value="WARN">Warning</option>
                    <option value="ERROR">Error</option>
                  </select>
                  <p className="text-xs text-muted-foreground">
                    Minimum log level to record
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Max Databases</label>
                  <Input
                    type="number"
                    value={settings.max_databases}
                    onChange={(e) => setSettings(prev => ({ ...prev, max_databases: parseInt(e.target.value) || 10 }))}
                    min="1"
                    max="100"
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum concurrent database instances
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="database" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Database className="w-5 h-5 mr-2" />
                Database Configuration
              </CardTitle>
              <CardDescription>
                Configure database management and storage settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Automatic Cleanup</h4>
                    <p className="text-sm text-muted-foreground">
                      Automatically remove stopped database containers
                    </p>
                  </div>
                  <Badge variant={settings.auto_cleanup ? "default" : "secondary"}>
                    {settings.auto_cleanup ? "Enabled" : "Disabled"}
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Backup Service</h4>
                    <p className="text-sm text-muted-foreground">
                      Enable automated database backups
                    </p>
                  </div>
                  <Badge variant={settings.backup_enabled ? "default" : "secondary"}>
                    {settings.backup_enabled ? "Enabled" : "Disabled"}
                  </Badge>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium mb-2">Database Storage</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Storage Path:</span>
                      <p className="text-muted-foreground font-mono">/data/databases</p>
                    </div>
                    <div>
                      <span className="font-medium">Backup Path:</span>
                      <p className="text-muted-foreground font-mono">/data/backups</p>
                    </div>
                    <div>
                      <span className="font-medium">Container Network:</span>
                      <p className="text-muted-foreground">db-forge-net</p>
                    </div>
                    <div>
                      <span className="font-medium">Worker Image:</span>
                      <p className="text-muted-foreground">db-worker-base:latest</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Performance Settings</CardTitle>
              <CardDescription>
                Configure performance and resource limits
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Memory Limit (MB)</label>
                  <Input
                    type="number"
                    defaultValue="512"
                    placeholder="512"
                  />
                  <p className="text-xs text-muted-foreground">
                    Memory limit per database container
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">CPU Limit (%)</label>
                  <Input
                    type="number"
                    defaultValue="50"
                    placeholder="50"
                    min="1"
                    max="100"
                  />
                  <p className="text-xs text-muted-foreground">
                    CPU usage limit per container
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Security Configuration
              </CardTitle>
              <CardDescription>
                Manage authentication and security settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">API Key (Development)</label>
                  <Input
                    value={settings.api_key}
                    onChange={(e) => setSettings(prev => ({ ...prev, api_key: e.target.value }))}
                    className="font-mono"
                    placeholder="API Key"
                  />
                  <p className="text-xs text-muted-foreground">
                    Fixed API key for development (not recommended for production)
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-yellow-800">Security Notice</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        This system is running in development mode with a fixed API key. 
                        For production deployment, implement proper authentication, HTTPS, 
                        and additional security measures.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Security Features</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">API Authentication</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Container Isolation</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">HTTPS/TLS</span>
                      <Badge variant="secondary">Manual Setup</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Rate Limiting</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                Notification Settings
              </CardTitle>
              <CardDescription>
                Configure alerts and notification preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium mb-2">Notification System</h4>
                <p className="text-sm text-muted-foreground">
                  Notification features are planned for future releases. This will include 
                  email alerts, webhook notifications, and real-time dashboard updates 
                  for system events, errors, and performance metrics.
                </p>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Planned Notification Types</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">System Errors</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Database Events</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Performance Alerts</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Security Events</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Backup Status</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">System Health</span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Advanced Configuration</CardTitle>
              <CardDescription>
                Advanced system settings and development options
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-red-800">Danger Zone</h4>
                      <p className="text-sm text-red-700 mt-1">
                        These actions are irreversible and may cause data loss.
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <Button variant="outline" className="text-red-600 border-red-300">
                      Reset All Settings
                    </Button>
                    <Button variant="destructive">
                      Factory Reset System
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">System Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Platform:</span>
                          <span className="font-medium">Docker</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Network:</span>
                          <span className="font-medium">db-forge-net</span>
                        </div>
                        <div className="flex justify-between">
                          <span>API Version:</span>
                          <span className="font-medium">v1</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Build:</span>
                          <span className="font-medium">Development</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Development Mode</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Debug Logging</span>
                          <Badge className="bg-orange-500">Enabled</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Hot Reload</span>
                          <Badge className="bg-green-500">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">CORS</span>
                          <Badge className="bg-yellow-500">Permissive</Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}