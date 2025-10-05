"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { 
  Play, 
  Save, 
  History, 
  Download,
  Copy,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  AlertCircle,
  FileText,
  RotateCcw
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface QueryResult {
  success: boolean
  data?: any[]
  error?: string
  rowCount?: number
  executionTime?: number
  columns?: string[]
}

interface QueryHistory {
  id: string
  query: string
  timestamp: Date
  success: boolean
  executionTime?: number
}

interface SQLEditorProps {
  databaseName: string
}

export function SQLEditor({ databaseName }: SQLEditorProps) {
  const [query, setQuery] = useState("")
  const [result, setResult] = useState<QueryResult | null>(null)
  const [history, setHistory] = useState<QueryHistory[]>([])
  const [loading, setLoading] = useState(false)
  const [savedQueries, setSavedQueries] = useState<Array<{id: string, name: string, query: string}>>([])

  // Sample saved queries for demo
  const sampleQueries = [
    {
      id: "1",
      name: "List All Tables",
      query: "SELECT name FROM sqlite_master WHERE type='table';"
    },
    {
      id: "2", 
      name: "Table Schema Info",
      query: "PRAGMA table_info(your_table_name);"
    },
    {
      id: "3",
      name: "Count Records",
      query: "SELECT COUNT(*) as total_records FROM your_table_name;"
    },
    {
      id: "4",
      name: "Database Info",
      query: "PRAGMA database_list;"
    }
  ]

  useEffect(() => {
    setSavedQueries(sampleQueries)
  }, [])

  const executeQuery = async () => {
    if (!query.trim()) return

    try {
      setLoading(true)
      const startTime = Date.now()
      
      const response = await apiClient.executeQuery(databaseName, query)
      const executionTime = Date.now() - startTime

      const queryResult: QueryResult = {
        success: response.success,
        data: response.data,
        error: response.error,
        rowCount: response.data?.length || 0,
        executionTime,
        columns: response.data && response.data.length > 0 ? Object.keys(response.data[0]) : []
      }

      setResult(queryResult)

      // Add to history
      const historyItem: QueryHistory = {
        id: Date.now().toString(),
        query,
        timestamp: new Date(),
        success: response.success,
        executionTime
      }
      setHistory(prev => [historyItem, ...prev.slice(0, 9)]) // Keep last 10

    } catch (err) {
      console.error('Query execution failed:', err)
      setResult({
        success: false,
        error: err instanceof Error ? err.message : 'Query execution failed'
      })
    } finally {
      setLoading(false)
    }
  }

  const formatExecutionTime = (ms?: number) => {
    if (!ms) return 'N/A'
    return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(2)}s`
  }

  const loadSavedQuery = (savedQuery: string) => {
    setQuery(savedQuery)
  }

  const loadFromHistory = (historyQuery: string) => {
    setQuery(historyQuery)
  }

  const exportResults = () => {
    if (!result?.data) return

    const csvContent = [
      result.columns?.join(',') || '',
      ...result.data.map(row => 
        result.columns?.map(col => 
          JSON.stringify(row[col] || '')
        ).join(',') || ''
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${databaseName}_query_results.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const copyResults = async () => {
    if (!result?.data) return

    const textContent = result.data.map(row => 
      result.columns?.map(col => row[col] || '').join('\t') || ''
    ).join('\n')

    try {
      await navigator.clipboard.writeText(textContent)
      // Show success feedback (would need toast notification)
    } catch (err) {
      console.error('Failed to copy results:', err)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="w-5 h-5 mr-2" />
            SQL Query Editor - {databaseName}
          </CardTitle>
          <CardDescription>
            Execute SQL queries and view results in real-time
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">SQL Query</label>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm" onClick={() => setQuery("")}>
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Clear
                </Button>
                <Button 
                  onClick={executeQuery}
                  disabled={loading || !query.trim()}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Execute Query
                    </>
                  )}
                </Button>
              </div>
            </div>
            
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your SQL query here..."
              className="min-h-[120px] font-mono text-sm"
              disabled={loading}
            />
            
            <div className="flex items-center text-xs text-muted-foreground">
              <FileText className="w-3 h-3 mr-1" />
              Press Ctrl+Enter to execute • Use semicolon to separate multiple statements
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="results" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="saved">Saved Queries</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="schema">Schema</TabsTrigger>
        </TabsList>

        <TabsContent value="results" className="space-y-4">
          {result ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center">
                    {result.success ? (
                      <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 mr-2 text-red-600" />
                    )}
                    Query Results
                  </CardTitle>
                  {result.success && result.data && (
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" onClick={copyResults}>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                      <Button variant="outline" size="sm" onClick={exportResults}>
                        <Download className="w-4 h-4 mr-2" />
                        Export CSV
                      </Button>
                    </div>
                  )}
                </div>
                {result.success && (
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>Rows: {result.rowCount}</span>
                    <span>•</span>
                    <span>Time: {formatExecutionTime(result.executionTime)}</span>
                    {result.columns && (
                      <>
                        <span>•</span>
                        <span>Columns: {result.columns.length}</span>
                      </>
                    )}
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {result.success ? (
                  result.data && result.data.length > 0 ? (
                    <div className="border rounded-lg overflow-auto max-h-96">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {result.columns?.map((column) => (
                              <TableHead key={column} className="font-medium">
                                {column}
                              </TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {result.data.map((row, index) => (
                            <TableRow key={index}>
                              {result.columns?.map((column) => (
                                <TableCell key={column} className="font-mono text-sm">
                                  {row[column] !== null && row[column] !== undefined 
                                    ? String(row[column]) 
                                    : <span className="text-muted-foreground italic">NULL</span>
                                  }
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      Query executed successfully but returned no results
                    </div>
                  )
                ) : (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Query Error</AlertTitle>
                    <AlertDescription className="font-mono text-sm">
                      {result.error}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  Execute a query to see results here
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="saved" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Saved Queries</CardTitle>
              <CardDescription>
                Quick access to frequently used queries
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {savedQueries.map((saved) => (
                  <div 
                    key={saved.id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                    onClick={() => loadSavedQuery(saved.query)}
                  >
                    <div>
                      <div className="font-medium">{saved.name}</div>
                      <div className="text-sm text-muted-foreground font-mono">
                        {saved.query.substring(0, 80)}...
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      Load
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <History className="w-5 h-5 mr-2" />
                Query History
              </CardTitle>
              <CardDescription>
                Recent query executions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <div className="space-y-3">
                  {history.map((item) => (
                    <div 
                      key={item.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                      onClick={() => loadFromHistory(item.query)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          {item.success ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-600" />
                          )}
                          <span className="text-sm text-muted-foreground">
                            {item.timestamp.toLocaleString()}
                          </span>
                          {item.executionTime && (
                            <Badge variant="outline" className="text-xs">
                              {formatExecutionTime(item.executionTime)}
                            </Badge>
                          )}
                        </div>
                        <div className="text-sm font-mono mt-1">
                          {item.query.substring(0, 100)}...
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        Load
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No query history yet. Execute some queries to see them here.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schema" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Database Schema</CardTitle>
              <CardDescription>
                Tables, indexes, and database structure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-muted-foreground">
                  Schema explorer is coming soon. For now, you can use these queries:
                </p>
                <div className="mt-3 space-y-1 font-mono text-sm">
                  <div>• <code>SELECT name FROM sqlite_master WHERE type='table';</code></div>
                  <div>• <code>PRAGMA table_info(table_name);</code></div>
                  <div>• <code>SELECT sql FROM sqlite_master WHERE name='table_name';</code></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}