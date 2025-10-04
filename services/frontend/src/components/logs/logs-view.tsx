"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  FileText, 
  RefreshCw,
  Search,
  Download,
  Filter,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  AlertCircle
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface LogEntry {
  id: string
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL'
  service: string
  message: string
  source: string
  details?: unknown
}

export function LogsView() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedLevel, setSelectedLevel] = useState<string>("all")
  const [selectedService, setSelectedService] = useState<string>("all")

  // Mock data for demonstration since centralized logging isn't implemented yet
  const generateMockLogs = (): LogEntry[] => {
    const mockData: LogEntry[] = [
      {
        id: 'log_001',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        level: 'INFO',
        service: 'db-gateway',
        source: 'main.py',
        message: 'Database instance spawned successfully',
        details: { database: 'test-db', container_id: 'b827ca03c04e' }
      },
      {
        id: 'log_002',
        timestamp: new Date(Date.now() - 600000).toISOString(),
        level: 'DEBUG',
        service: 'db-gateway',
        source: 'auth.py',
        message: 'API key verification successful',
        details: { endpoint: '/admin/databases', method: 'GET' }
      },
      {
        id: 'log_003',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        level: 'WARN',
        service: 'traefik',
        source: 'router',
        message: 'Route resolution took longer than expected',
        details: { route: 'db.localhost', duration: '2.5s' }
      },
      {
        id: 'log_004',
        timestamp: new Date(Date.now() - 1200000).toISOString(),
        level: 'ERROR',
        service: 'frontend',
        source: 'api-client',
        message: 'Failed to connect to backend API',
        details: { url: 'http://db-gateway:8000', error: 'Connection refused' }
      },
      {
        id: 'log_005',
        timestamp: new Date(Date.now() - 1500000).toISOString(),
        level: 'INFO',
        service: 'db-gateway',
        source: 'startup',
        message: 'DB-Gateway service started successfully',
        details: { version: '1.0.0', port: 8000 }
      },
      {
        id: 'log_006',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        level: 'INFO',
        service: 'db-worker',
        source: 'sqlite',
        message: 'Database query executed',
        details: { database: 'test-db', query: 'SELECT * FROM users', duration: '0.003s' }
      }
    ]
    return mockData.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  }

  const fetchLogs = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // For now, use mock data since centralized logging isn't implemented yet
      const mockLogs = generateMockLogs()
      setLogs(mockLogs)
      setFilteredLogs(mockLogs)
      
    } catch (err) {
      console.error('Failed to fetch logs:', err)
      setError(err instanceof Error ? err.message : 'Failed to load logs')
    } finally {
      setLoading(false)
    }
  }

  const filterLogs = () => {
    let filtered = logs

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.source.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by log level
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(log => log.level === selectedLevel)
    }

    // Filter by service
    if (selectedService !== 'all') {
      filtered = filtered.filter(log => log.service === selectedService)
    }

    setFilteredLogs(filtered)
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    filterLogs()
  }, [logs, searchTerm, selectedLevel, selectedService])

  const getLevelBadge = (level: LogEntry['level']) => {
    switch (level) {
      case 'DEBUG':
        return <Badge variant="secondary"><Info className="w-3 h-3 mr-1" />Debug</Badge>
      case 'INFO':
        return <Badge className="bg-blue-500"><CheckCircle className="w-3 h-3 mr-1" />Info</Badge>
      case 'WARN':
        return <Badge className="bg-yellow-500"><AlertTriangle className="w-3 h-3 mr-1" />Warning</Badge>
      case 'ERROR':
        return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Error</Badge>
      case 'FATAL':
        return <Badge className="bg-red-800"><XCircle className="w-3 h-3 mr-1" />Fatal</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getLogCounts = () => {
    return {
      total: logs.length,
      errors: logs.filter(l => l.level === 'ERROR' || l.level === 'FATAL').length,
      warnings: logs.filter(l => l.level === 'WARN').length,
      info: logs.filter(l => l.level === 'INFO').length,
      debug: logs.filter(l => l.level === 'DEBUG').length
    }
  }

  const uniqueServices = Array.from(new Set(logs.map(l => l.service)))
  const logCounts = getLogCounts()

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
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
            <Button variant="outline" size="sm" onClick={fetchLogs}>
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
      {/* Log Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Logs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{logCounts.total}</div>
            <p className="text-xs text-muted-foreground">
              All log entries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Errors</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{logCounts.errors}</div>
            <p className="text-xs text-muted-foreground">
              Error & Fatal logs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Warnings</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{logCounts.warnings}</div>
            <p className="text-xs text-muted-foreground">
              Warning logs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Info</CardTitle>
            <CheckCircle className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{logCounts.info}</div>
            <p className="text-xs text-muted-foreground">
              Information logs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Debug</CardTitle>
            <Info className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{logCounts.debug}</div>
            <p className="text-xs text-muted-foreground">
              Debug logs
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="live" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="live">Live Logs</TabsTrigger>
            <TabsTrigger value="search">Search & Filter</TabsTrigger>
            <TabsTrigger value="export">Export & Archive</TabsTrigger>
          </TabsList>
          <Button onClick={fetchLogs} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        <TabsContent value="live" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Real-time System Logs
              </CardTitle>
              <CardDescription>
                Live stream of application logs from all services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-auto">
                {filteredLogs.slice(0, 50).map((log) => (
                  <div key={log.id} className="flex items-start space-x-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex-shrink-0">
                      {getLevelBadge(log.level)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="font-medium">{log.service}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{log.source}</span>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-muted-foreground">{formatTimestamp(log.timestamp)}</span>
                      </div>
                      <p className="text-sm mt-1">{log.message}</p>
                      {log.details && (
                        <pre className="text-xs text-muted-foreground mt-2 bg-gray-100 p-2 rounded overflow-auto">
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
                {filteredLogs.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No logs match the current filters
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Search className="w-5 h-5 mr-2" />
                Search and Filter Logs
              </CardTitle>
              <CardDescription>
                Find specific log entries using search and filters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Search</label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                      <Input
                        placeholder="Search logs..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Log Level</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={selectedLevel}
                      onChange={(e) => setSelectedLevel(e.target.value)}
                    >
                      <option value="all">All Levels</option>
                      <option value="DEBUG">Debug</option>
                      <option value="INFO">Info</option>
                      <option value="WARN">Warning</option>
                      <option value="ERROR">Error</option>
                      <option value="FATAL">Fatal</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Service</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={selectedService}
                      onChange={(e) => setSelectedService(e.target.value)}
                    >
                      <option value="all">All Services</option>
                      {uniqueServices.map(service => (
                        <option key={service} value={service}>{service}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">Filter Results</h4>
                      <p className="text-sm text-muted-foreground">
                        Showing {filteredLogs.length} of {logs.length} log entries
                      </p>
                    </div>
                    <Button 
                      variant="outline" 
                      onClick={() => {
                        setSearchTerm("")
                        setSelectedLevel("all")
                        setSelectedService("all")
                      }}
                    >
                      Clear Filters
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="export" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Download className="w-5 h-5 mr-2" />
                Export and Archive Logs
              </CardTitle>
              <CardDescription>
                Export logs for analysis or long-term storage
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Quick Export</h3>
                    <div className="space-y-2">
                      <Button className="w-full justify-start">
                        <Download className="w-4 h-4 mr-2" />
                        Export Last 100 Logs (JSON)
                      </Button>
                      <Button variant="outline" className="w-full justify-start">
                        <Download className="w-4 h-4 mr-2" />
                        Export Errors Only (CSV)
                      </Button>
                      <Button variant="outline" className="w-full justify-start">
                        <Download className="w-4 h-4 mr-2" />
                        Export All Today's Logs
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Archive Management</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Log Retention:</span>
                        <span className="font-medium">7 days</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Archive Size:</span>
                        <span className="font-medium">245 MB</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Oldest Log:</span>
                        <span className="font-medium">6 days ago</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Log Management Notice</h3>
                  <p className="text-sm text-muted-foreground">
                    Centralized logging and archival features are currently in development. 
                    Logs are currently stored in individual container volumes. Implement 
                    a centralized logging solution like ELK Stack or Loki for production use.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}