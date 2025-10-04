"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Database, 
  Server, 
  Activity, 
  Plus,
  AlertCircle,
  CheckCircle,
  Clock,
  Trash2,
  RefreshCw
} from "lucide-react"
import { apiClient, DatabaseInstance, SystemStats } from "@/lib/api"

export function DatabaseOverview() {
  const [databases, setDatabases] = useState<DatabaseInstance[]>([])
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newDbName, setNewDbName] = useState("")
  const [creating, setCreating] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [databasesData, statsData] = await Promise.all([
        apiClient.getDatabases(),
        apiClient.getSystemStats()
      ])
      
      setDatabases(databasesData)
      setStats(statsData)
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateDatabase = async () => {
    if (!newDbName.trim()) return
    
    try {
      setCreating(true)
      await apiClient.spawnDatabase(newDbName.trim())
      setNewDbName("")
      // Refresh the list
      await fetchData()
    } catch (err) {
      console.error('Failed to create database:', err)
      setError(err instanceof Error ? err.message : 'Failed to create database')
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteDatabase = async (dbName: string) => {
    if (!confirm(`Are you sure you want to delete database "${dbName}"?`)) return
    
    try {
      await apiClient.pruneDatabase(dbName)
      // Refresh the list
      await fetchData()
    } catch (err) {
      console.error('Failed to delete database:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete database')
    }
  }

  useEffect(() => {
    fetchData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusBadge = (status: string) => {
    const statusLower = status.toLowerCase()
    if (statusLower.includes('running') || statusLower.includes('healthy')) {
      return <Badge className="bg-green-500"><CheckCircle className="w-3 h-3 mr-1" />Running</Badge>
    }
    if (statusLower.includes('created') || statusLower.includes('exited')) {
      return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Stopped</Badge>
    }
    return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Unknown</Badge>
  }

  if (loading && !stats) {
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
            <Button variant="outline" size="sm" onClick={fetchData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const runningDatabases = databases.filter(db => 
    db.status.toLowerCase().includes('running') || db.status.toLowerCase().includes('healthy')
  ).length

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Databases</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{databases.length}</div>
            <p className="text-xs text-muted-foreground">
              {runningDatabases} running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_requests || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.total_errors || 0} errors
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uptime</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats ? Math.floor(stats.uptime_seconds / 3600) : 0}h
            </div>
            <p className="text-xs text-muted-foreground">
              System uptime
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium">Operational</span>
            </div>
            <p className="text-xs text-muted-foreground">
              All systems running
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Create Database Section */}
      <Card>
        <CardHeader>
          <CardTitle>Create New Database</CardTitle>
          <CardDescription>
            Spawn a new isolated database instance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Input
              placeholder="Database name (e.g., my-app-db)"
              value={newDbName}
              onChange={(e) => setNewDbName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCreateDatabase()}
            />
            <Button 
              onClick={handleCreateDatabase}
              disabled={creating || !newDbName.trim()}
            >
              {creating ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Plus className="w-4 h-4 mr-2" />
              )}
              Create
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Databases List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Database Instances</CardTitle>
              <CardDescription>
                Monitor and manage your database instances
              </CardDescription>
            </div>
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {databases.length === 0 ? (
            <div className="text-center py-8">
              <Database className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-2 text-sm font-semibold">No databases</h3>
              <p className="text-sm text-muted-foreground">
                Create your first database to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {databases.map((db) => (
                <div
                  key={db.name}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <Database className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <h3 className="font-medium">{db.name}</h3>
                      <p className="text-sm text-muted-foreground">SQLite Container</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {getStatusBadge(db.status)}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteDatabase(db.name)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}