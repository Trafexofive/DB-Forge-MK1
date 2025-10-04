"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { 
  Activity, 
  RefreshCw,
  Wifi,
  WifiOff,
  Clock,
  Server,
  Users,
  Database,
  AlertCircle
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface Connection {
  id: string
  database: string
  client_ip: string
  connected_at: string
  duration: number
  status: 'active' | 'idle' | 'disconnected'
  queries_executed: number
}

export function ConnectionsView() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    total_connections: 0,
    active_connections: 0,
    idle_connections: 0,
    total_queries: 0
  })

  // Mock data for demonstration since the backend doesn't have connection tracking yet
  const generateMockConnections = (): Connection[] => {
    const mockData: Connection[] = [
      {
        id: 'conn_001',
        database: 'test-db',
        client_ip: '172.18.0.4',
        connected_at: new Date(Date.now() - 3600000).toISOString(),
        duration: 3600,
        status: 'active',
        queries_executed: 15
      },
      {
        id: 'conn_002',
        database: 'test-db',
        client_ip: '172.18.0.5',
        connected_at: new Date(Date.now() - 1800000).toISOString(),
        duration: 1800,
        status: 'idle',
        queries_executed: 3
      },
      {
        id: 'conn_003',
        database: 'production-db',
        client_ip: '172.18.0.6',
        connected_at: new Date(Date.now() - 300000).toISOString(),
        duration: 300,
        status: 'active',
        queries_executed: 8
      }
    ]
    return mockData
  }

  const fetchConnections = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // For now, use mock data since connection tracking isn't implemented yet
      const mockConnections = generateMockConnections()
      setConnections(mockConnections)
      
      // Calculate stats
      setStats({
        total_connections: mockConnections.length,
        active_connections: mockConnections.filter(c => c.status === 'active').length,
        idle_connections: mockConnections.filter(c => c.status === 'idle').length,
        total_queries: mockConnections.reduce((sum, c) => sum + c.queries_executed, 0)
      })
      
    } catch (err) {
      console.error('Failed to fetch connections:', err)
      setError(err instanceof Error ? err.message : 'Failed to load connections')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
    const interval = setInterval(fetchConnections, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusBadge = (status: Connection['status']) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500"><Wifi className="w-3 h-3 mr-1" />Active</Badge>
      case 'idle':
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Idle</Badge>
      case 'disconnected':
        return <Badge variant="destructive"><WifiOff className="w-3 h-3 mr-1" />Disconnected</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

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
            <Button variant="outline" size="sm" onClick={fetchConnections}>
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
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Connections</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_connections}</div>
            <p className="text-xs text-muted-foreground">
              All database connections
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Connections</CardTitle>
            <Wifi className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.active_connections}</div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Idle Connections</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.idle_connections}</div>
            <p className="text-xs text-muted-foreground">
              Idle connections
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
            <Database className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.total_queries}</div>
            <p className="text-xs text-muted-foreground">
              Queries executed
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="active" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="active">Active Connections</TabsTrigger>
            <TabsTrigger value="all">All Connections</TabsTrigger>
            <TabsTrigger value="pools">Connection Pools</TabsTrigger>
          </TabsList>
          <Button onClick={fetchConnections} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        <TabsContent value="active" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Database Connections</CardTitle>
              <CardDescription>
                Currently active connections to database instances
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Connection ID</TableHead>
                    <TableHead>Database</TableHead>
                    <TableHead>Client IP</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Queries</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {connections.filter(conn => conn.status === 'active').map((connection) => (
                    <TableRow key={connection.id}>
                      <TableCell className="font-mono text-sm">{connection.id}</TableCell>
                      <TableCell>{connection.database}</TableCell>
                      <TableCell className="font-mono">{connection.client_ip}</TableCell>
                      <TableCell>{getStatusBadge(connection.status)}</TableCell>
                      <TableCell>{formatDuration(connection.duration)}</TableCell>
                      <TableCell>{connection.queries_executed}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="all" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Database Connections</CardTitle>
              <CardDescription>
                Complete list of database connections and their status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Connection ID</TableHead>
                    <TableHead>Database</TableHead>
                    <TableHead>Client IP</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Connected At</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Queries</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {connections.map((connection) => (
                    <TableRow key={connection.id}>
                      <TableCell className="font-mono text-sm">{connection.id}</TableCell>
                      <TableCell>{connection.database}</TableCell>
                      <TableCell className="font-mono">{connection.client_ip}</TableCell>
                      <TableCell>{getStatusBadge(connection.status)}</TableCell>
                      <TableCell>{new Date(connection.connected_at).toLocaleString()}</TableCell>
                      <TableCell>{formatDuration(connection.duration)}</TableCell>
                      <TableCell>{connection.queries_executed}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pools" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Connection Pools</CardTitle>
              <CardDescription>
                Connection pool statistics and configuration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <Server className="h-5 w-5 text-blue-500" />
                    <h3 className="font-medium">Connection Pooling</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">
                    Connection pooling is not yet implemented in DB-Forge. Each database connection 
                    is handled directly by the SQLite containers. Future versions will include 
                    connection pooling for improved performance.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Pool Configuration</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Max Pool Size:</span>
                          <span className="font-medium">N/A</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Min Pool Size:</span>
                          <span className="font-medium">N/A</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Connection Timeout:</span>
                          <span className="font-medium">N/A</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Idle Timeout:</span>
                          <span className="font-medium">N/A</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Pool Statistics</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Active Pools:</span>
                          <span className="font-medium">0</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Connections:</span>
                          <span className="font-medium">{stats.total_connections}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Available Connections:</span>
                          <span className="font-medium">N/A</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Borrowed Connections:</span>
                          <span className="font-medium">N/A</span>
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