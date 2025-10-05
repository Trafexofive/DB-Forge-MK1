"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { SQLEditor } from "./sql-editor"
import { 
  Database, 
  Plus,
  AlertCircle,
  CheckCircle,
  Clock,
  Trash2,
  RefreshCw,
  Play,
  Square,
  Settings,
  Terminal,
  Table,
  Code
} from "lucide-react"
import { apiClient, DatabaseInstance } from "@/lib/api"

export function DatabasesView() {
  const [databases, setDatabases] = useState<DatabaseInstance[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDb, setSelectedDb] = useState<string | null>(null)
  const [sqlQuery, setSqlQuery] = useState("")
  const [queryResult, setQueryResult] = useState<unknown>(null)
  const [queryLoading, setQueryLoading] = useState(false)

  const fetchDatabases = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getDatabases()
      setDatabases(data)
    } catch (err) {
      console.error('Failed to fetch databases:', err)
      setError(err instanceof Error ? err.message : 'Failed to load databases')
    } finally {
      setLoading(false)
    }
  }

  const executeQuery = async () => {
    if (!selectedDb || !sqlQuery.trim()) return
    
    try {
      setQueryLoading(true)
      const result = await apiClient.executeQuery(selectedDb, sqlQuery.trim())
      setQueryResult(result)
    } catch (err) {
      console.error('Query failed:', err)
      setQueryResult({
        error: err instanceof Error ? err.message : 'Query failed'
      })
    } finally {
      setQueryLoading(false)
    }
  }

  const handleDeleteDatabase = async (dbName: string) => {
    if (!confirm(`Are you sure you want to delete database "${dbName}"?`)) return
    
    try {
      await apiClient.pruneDatabase(dbName)
      await fetchDatabases()
    } catch (err) {
      console.error('Failed to delete database:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete database')
    }
  }

  useEffect(() => {
    fetchDatabases()
    const interval = setInterval(fetchDatabases, 30000)
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
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
            <Button variant="outline" size="sm" onClick={fetchDatabases}>
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
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="query">Query Console</TabsTrigger>
          <TabsTrigger value="management">Management</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Database Instances</h2>
            <Button onClick={fetchDatabases} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>

          {databases.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8">
                  <Database className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-2 text-sm font-semibold">No databases</h3>
                  <p className="text-sm text-muted-foreground">
                    Get started by creating your first database instance.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {databases.map((db) => (
                <Card key={db.name} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Database className="h-8 w-8 text-blue-500" />
                      {getStatusBadge(db.status)}
                    </div>
                    <CardTitle className="text-xl">{db.name}</CardTitle>
                    <CardDescription>
                      SQLite Database Container
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-sm">
                        <p><strong>Container ID:</strong> {db.container_id?.substring(0, 12)}...</p>
                        <p><strong>Status:</strong> {db.status}</p>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedDb(db.name)}
                        >
                          <Terminal className="w-4 h-4 mr-2" />
                          Query
                        </Button>
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
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="query" className="space-y-6">
          {selectedDb ? (
            <SQLEditor databaseName={selectedDb} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Code className="w-5 h-5 mr-2" />
                  SQL Query Editor
                </CardTitle>
                <CardDescription>
                  Select a running database to execute SQL queries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Select Database</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={selectedDb || ''}
                      onChange={(e) => setSelectedDb(e.target.value)}
                    >
                      <option value="">Choose a database...</option>
                      {databases.filter(db => db.status.toLowerCase().includes('running')).map(db => (
                        <option key={db.name} value={db.name}>{db.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  {databases.filter(db => db.status.toLowerCase().includes('running')).length === 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2 text-yellow-700">
                        <AlertCircle className="w-5 h-5" />
                        <span>No running databases available. Create and start a database first.</span>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="management" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Database Management
              </CardTitle>
              <CardDescription>
                Advanced database operations and maintenance tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Quick Actions</h3>
                  <div className="space-y-2">
                    <Button className="w-full justify-start">
                      <Plus className="w-4 h-4 mr-2" />
                      Create New Database
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Refresh All Status
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Table className="w-4 h-4 mr-2" />
                      Bulk Operations
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Statistics</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Total Databases:</span>
                      <span className="font-medium">{databases.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Running:</span>
                      <span className="font-medium text-green-600">
                        {databases.filter(db => db.status.toLowerCase().includes('running')).length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Stopped:</span>
                      <span className="font-medium text-yellow-600">
                        {databases.filter(db => !db.status.toLowerCase().includes('running')).length}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}