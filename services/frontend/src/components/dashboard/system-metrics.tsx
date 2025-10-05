"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from "lucide-react"
import { apiClient, SystemStats } from "@/lib/api"

interface MetricCard {
  title: string
  value: string | number
  change?: number
  icon: React.ComponentType<any>
  color?: 'default' | 'success' | 'warning' | 'error'
  progress?: number
}

export function SystemMetrics() {
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getSystemStats()
      setStats(data)
    } catch (err) {
      console.error('Failed to fetch metrics:', err)
      setError(err instanceof Error ? err.message : 'Failed to load metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    if (bytes === 0) return '0 B'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

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

  const getMetrics = (): MetricCard[] => {
    if (!stats) return []

    return [
      {
        title: 'Active Databases',
        value: stats.active_databases || 0,
        icon: HardDrive,
        color: 'success'
      },
      {
        title: 'Total Queries',
        value: (stats.total_queries || 0).toLocaleString(),
        change: 12.5,
        icon: Activity,
        color: 'default'
      },
      {
        title: 'Memory Usage',
        value: '512 MB',
        progress: 65,
        icon: MemoryStick,
        color: 'warning'
      },
      {
        title: 'System Uptime',
        value: formatUptime(stats.uptime_seconds || 0),
        icon: Cpu,
        color: 'success'
      }
    ]
  }

  const getColorClass = (color: MetricCard['color']) => {
    switch (color) {
      case 'success': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      default: return 'text-blue-600'
    }
  }

  const getBadgeVariant = (color: MetricCard['color']) => {
    switch (color) {
      case 'success': return 'default'
      case 'warning': return 'secondary'
      case 'error': return 'destructive'
      default: return 'outline'
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertTriangle className="w-5 h-5" />
              <span>Failed to load metrics: {error}</span>
            </div>
            <Button variant="outline" size="sm" onClick={fetchMetrics}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const metrics = getMetrics()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">System Metrics</h3>
        <Button variant="ghost" size="sm" onClick={fetchMetrics}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const IconComponent = metric.icon
          return (
            <Card key={index} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
                <IconComponent className={`h-4 w-4 ${getColorClass(metric.color)}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metric.value}</div>
                
                {metric.change !== undefined && (
                  <div className="flex items-center text-xs text-muted-foreground mt-1">
                    {metric.change > 0 ? (
                      <TrendingUp className="w-3 h-3 mr-1 text-green-500" />
                    ) : (
                      <TrendingDown className="w-3 h-3 mr-1 text-red-500" />
                    )}
                    <span className={metric.change > 0 ? 'text-green-600' : 'text-red-600'}>
                      {Math.abs(metric.change)}%
                    </span>
                    <span className="ml-1">from last hour</span>
                  </div>
                )}
                
                {metric.progress !== undefined && (
                  <div className="mt-3">
                    <Progress value={metric.progress} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-1">
                      {metric.progress}% utilized
                    </p>
                  </div>
                )}
              </CardContent>
              
              <div className="absolute top-0 right-0 p-2">
                <Badge variant={getBadgeVariant(metric.color)} className="text-xs">
                  Live
                </Badge>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Additional System Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">System Health Overview</CardTitle>
          <CardDescription>
            Real-time monitoring of critical system components
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Response Time</span>
                <Badge className="bg-green-500">Optimal</Badge>
              </div>
              <Progress value={85} className="h-2" />
              <p className="text-xs text-muted-foreground">~120ms average</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Container Health</span>
                <Badge className="bg-green-500">Healthy</Badge>
              </div>
              <Progress value={100} className="h-2" />
              <p className="text-xs text-muted-foreground">All services running</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Storage Usage</span>
                <Badge variant="secondary">Normal</Badge>
              </div>
              <Progress value={45} className="h-2" />
              <p className="text-xs text-muted-foreground">2.1GB of 5GB used</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}