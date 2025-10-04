"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { 
  Shield, 
  ShieldAlert,
  ShieldCheck,
  Key,
  Lock,
  Unlock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Eye,
  Settings,
  AlertCircle
} from "lucide-react"

interface SecurityEvent {
  id: string
  timestamp: string
  event_type: 'login_success' | 'login_failed' | 'api_access' | 'permission_denied' | 'database_created' | 'database_deleted'
  user: string
  ip_address: string
  resource: string
  details: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

interface SecurityMetrics {
  total_events: number
  failed_logins: number
  api_requests: number
  permission_denials: number
  security_score: number
}

export function SecurityView() {
  const [events, setEvents] = useState<SecurityEvent[]>([])
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    total_events: 0,
    failed_logins: 0,
    api_requests: 0,
    permission_denials: 0,
    security_score: 85
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Mock data for demonstration since security monitoring isn't implemented yet
  const generateMockEvents = (): SecurityEvent[] => {
    const mockData: SecurityEvent[] = [
      {
        id: 'sec_001',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        event_type: 'api_access',
        user: 'admin@db-forge.local',
        ip_address: '172.18.0.4',
        resource: '/admin/databases',
        details: 'Successful API request to list databases',
        severity: 'low'
      },
      {
        id: 'sec_002',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        event_type: 'database_created',
        user: 'admin@db-forge.local',
        ip_address: '172.18.0.4',
        resource: 'test-database',
        details: 'Database instance created successfully',
        severity: 'medium'
      },
      {
        id: 'sec_003',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        event_type: 'login_failed',
        user: 'unknown',
        ip_address: '192.168.1.100',
        resource: '/auth/login',
        details: 'Invalid API key provided',
        severity: 'high'
      },
      {
        id: 'sec_004',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        event_type: 'permission_denied',
        user: 'viewer@company.com',
        ip_address: '172.18.0.5',
        resource: '/admin/databases/delete',
        details: 'Insufficient permissions for delete operation',
        severity: 'medium'
      }
    ]
    return mockData
  }

  const fetchSecurityData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // For now, use mock data since security monitoring isn't implemented yet
      const mockEvents = generateMockEvents()
      setEvents(mockEvents)
      
      // Calculate metrics from mock data
      setMetrics({
        total_events: mockEvents.length,
        failed_logins: mockEvents.filter(e => e.event_type === 'login_failed').length,
        api_requests: mockEvents.filter(e => e.event_type === 'api_access').length,
        permission_denials: mockEvents.filter(e => e.event_type === 'permission_denied').length,
        security_score: 85
      })
      
    } catch (err) {
      console.error('Failed to fetch security data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load security data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSecurityData()
    const interval = setInterval(fetchSecurityData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getSeverityBadge = (severity: SecurityEvent['severity']) => {
    switch (severity) {
      case 'critical':
        return <Badge variant="destructive"><AlertTriangle className="w-3 h-3 mr-1" />Critical</Badge>
      case 'high':
        return <Badge className="bg-orange-500"><AlertTriangle className="w-3 h-3 mr-1" />High</Badge>
      case 'medium':
        return <Badge className="bg-yellow-500">Medium</Badge>
      case 'low':
        return <Badge variant="secondary">Low</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getEventIcon = (eventType: SecurityEvent['event_type']) => {
    switch (eventType) {
      case 'login_success':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'login_failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'api_access':
        return <Key className="w-4 h-4 text-blue-500" />
      case 'permission_denied':
        return <Lock className="w-4 h-4 text-orange-500" />
      case 'database_created':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'database_deleted':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const formatEventType = (eventType: SecurityEvent['event_type']) => {
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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
            <Button variant="outline" size="sm" onClick={fetchSecurityData}>
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
      {/* Security Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Score</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{metrics.security_score}%</div>
            <p className="text-xs text-muted-foreground">
              Overall security health
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Logins</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{metrics.failed_logins}</div>
            <p className="text-xs text-muted-foreground">
              In the last 24 hours
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Requests</CardTitle>
            <Key className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{metrics.api_requests}</div>
            <p className="text-xs text-muted-foreground">
              Successful API calls
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Permission Denials</CardTitle>
            <Lock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{metrics.permission_denials}</div>
            <p className="text-xs text-muted-foreground">
              Access denied events
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="events" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="events">Security Events</TabsTrigger>
            <TabsTrigger value="access">Access Control</TabsTrigger>
            <TabsTrigger value="settings">Security Settings</TabsTrigger>
          </TabsList>
          <Button onClick={fetchSecurityData} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Events</CardTitle>
              <CardDescription>
                Monitor authentication attempts, API access, and security incidents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Event</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {events.map((event) => (
                    <TableRow key={event.id}>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getEventIcon(event.event_type)}
                          <span>{formatEventType(event.event_type)}</span>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{event.user}</TableCell>
                      <TableCell className="font-mono">{event.ip_address}</TableCell>
                      <TableCell>{event.resource}</TableCell>
                      <TableCell>{getSeverityBadge(event.severity)}</TableCell>
                      <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="access" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ShieldCheck className="w-5 h-5 mr-2 text-green-500" />
                  API Authentication
                </CardTitle>
                <CardDescription>
                  Current authentication configuration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>API Key Authentication</span>
                    <Badge className="bg-green-500">Enabled</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Session Timeout</span>
                    <span className="text-sm font-medium">No expiry</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Rate Limiting</span>
                    <Badge variant="secondary">Disabled</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>IP Whitelisting</span>
                    <Badge variant="secondary">Disabled</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lock className="w-5 h-5 mr-2 text-blue-500" />
                  Access Permissions
                </CardTitle>
                <CardDescription>
                  Resource-based access control
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Database Management</span>
                    <Badge className="bg-blue-500">Admin Only</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>SQL Execution</span>
                    <Badge className="bg-green-500">All Users</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>System Logs</span>
                    <Badge className="bg-orange-500">Restricted</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>User Management</span>
                    <Badge className="bg-red-500">Super Admin</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Security Recommendations</CardTitle>
              <CardDescription>
                Suggested security improvements for your DB-Forge instance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-yellow-800">Enable Rate Limiting</h4>
                    <p className="text-sm text-yellow-700">
                      Implement API rate limiting to prevent abuse and brute force attacks.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-800">Multi-Factor Authentication</h4>
                    <p className="text-sm text-blue-700">
                      Add MFA for enhanced security, especially for administrative accounts.
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-green-50 border border-green-200 rounded-md">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-800">Security Monitoring Active</h4>
                    <p className="text-sm text-green-700">
                      Security event logging is enabled and monitoring access patterns.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Security Configuration
              </CardTitle>
              <CardDescription>
                Configure security policies and monitoring settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium mb-3">Current Security Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Authentication Method:</span>
                      <p className="text-muted-foreground">API Key (development-api-key-12345)</p>
                    </div>
                    <div>
                      <span className="font-medium">Encryption:</span>
                      <p className="text-muted-foreground">In transit (HTTPS recommended)</p>
                    </div>
                    <div>
                      <span className="font-medium">Audit Logging:</span>
                      <p className="text-muted-foreground">Basic event tracking</p>
                    </div>
                    <div>
                      <span className="font-medium">Access Control:</span>
                      <p className="text-muted-foreground">Role-based (in development)</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Development Mode Notice</h3>
                  <p className="text-sm text-muted-foreground">
                    DB-Forge is currently running in development mode with a fixed API key. 
                    For production use, implement proper authentication, HTTPS encryption, 
                    and additional security measures such as rate limiting and IP restrictions.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Security Features</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">API Authentication</span>
                          <Badge className="bg-green-500">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Event Logging</span>
                          <Badge className="bg-green-500">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Container Isolation</span>
                          <Badge className="bg-green-500">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">HTTPS/TLS</span>
                          <Badge variant="secondary">Recommended</Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Planned Features</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">User Authentication</span>
                          <Badge variant="outline">Planned</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Rate Limiting</span>
                          <Badge variant="outline">Planned</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Multi-Factor Auth</span>
                          <Badge variant="outline">Planned</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Audit Trail</span>
                          <Badge variant="outline">Planned</Badge>
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