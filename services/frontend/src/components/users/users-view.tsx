"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { 
  Users, 
  Plus,
  RefreshCw,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Edit,
  Trash2,
  UserPlus,
  Key,
  Settings,
  AlertCircle
} from "lucide-react"

interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user' | 'viewer'
  status: 'active' | 'inactive' | 'pending'
  created_at: string
  last_login: string | null
  permissions: string[]
}

export function UsersView() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)

  // Mock data for demonstration since user management isn't implemented yet
  const generateMockUsers = (): User[] => {
    const mockData: User[] = [
      {
        id: 'user_001',
        email: 'admin@db-forge.local',
        name: 'System Administrator',
        role: 'admin',
        status: 'active',
        created_at: new Date(Date.now() - 86400000 * 30).toISOString(),
        last_login: new Date(Date.now() - 3600000).toISOString(),
        permissions: ['read', 'write', 'admin', 'delete']
      },
      {
        id: 'user_002',
        email: 'alice.johnson@company.com',
        name: 'Alice Johnson',
        role: 'user',
        status: 'active',
        created_at: new Date(Date.now() - 86400000 * 15).toISOString(),
        last_login: new Date(Date.now() - 7200000).toISOString(),
        permissions: ['read', 'write']
      },
      {
        id: 'user_003',
        email: 'bob.smith@company.com',
        name: 'Bob Smith',
        role: 'viewer',
        status: 'active',
        created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
        last_login: new Date(Date.now() - 86400000).toISOString(),
        permissions: ['read']
      },
      {
        id: 'user_004',
        email: 'carol.davis@company.com',
        name: 'Carol Davis',
        role: 'user',
        status: 'pending',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        last_login: null,
        permissions: ['read']
      }
    ]
    return mockData
  }

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // For now, use mock data since user management isn't implemented yet
      const mockUsers = generateMockUsers()
      setUsers(mockUsers)
      
    } catch (err) {
      console.error('Failed to fetch users:', err)
      setError(err instanceof Error ? err.message : 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const getRoleBadge = (role: User['role']) => {
    switch (role) {
      case 'admin':
        return <Badge className="bg-red-500"><ShieldAlert className="w-3 h-3 mr-1" />Admin</Badge>
      case 'user':
        return <Badge className="bg-blue-500"><Shield className="w-3 h-3 mr-1" />User</Badge>
      case 'viewer':
        return <Badge variant="secondary"><ShieldCheck className="w-3 h-3 mr-1" />Viewer</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getStatusBadge = (status: User['status']) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500">Active</Badge>
      case 'inactive':
        return <Badge variant="destructive">Inactive</Badge>
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getUserInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString()
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
            <Button variant="outline" size="sm" onClick={fetchUsers}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalUsers = users.length
  const activeUsers = users.filter(u => u.status === 'active').length
  const adminUsers = users.filter(u => u.role === 'admin').length

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              Registered users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <UserPlus className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{activeUsers}</div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Administrators</CardTitle>
            <Shield className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{adminUsers}</div>
            <p className="text-xs text-muted-foreground">
              Admin privileges
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Invites</CardTitle>
            <Key className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {users.filter(u => u.status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting activation
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="users" className="w-full">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="users">All Users</TabsTrigger>
            <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
            <TabsTrigger value="settings">User Settings</TabsTrigger>
          </TabsList>
          <div className="flex space-x-2">
            <Button onClick={fetchUsers} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Add User
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New User</DialogTitle>
                  <DialogDescription>
                    Add a new user to the DB-Forge platform
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Email</label>
                    <Input placeholder="user@example.com" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Name</label>
                    <Input placeholder="Full Name" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Role</label>
                    <select className="w-full p-2 border rounded-md">
                      <option value="viewer">Viewer</option>
                      <option value="user">User</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={() => setIsCreateDialogOpen(false)}>
                    Create User
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <CardDescription>
                Manage user accounts, roles, and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Last Login</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback>{getUserInitials(user.name)}</AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">{user.email}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{getRoleBadge(user.role)}</TableCell>
                      <TableCell>{getStatusBadge(user.status)}</TableCell>
                      <TableCell>{formatDate(user.created_at)}</TableCell>
                      <TableCell>{formatDate(user.last_login)}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ShieldAlert className="w-5 h-5 mr-2 text-red-500" />
                  Administrator
                </CardTitle>
                <CardDescription>
                  Full system access and user management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Permissions:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Create/Delete databases</li>
                    <li>• Manage users and roles</li>
                    <li>• View system logs</li>
                    <li>• Execute SQL queries</li>
                    <li>• System configuration</li>
                  </ul>
                  <div className="pt-2">
                    <Badge className="bg-red-500">{adminUsers} users</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-blue-500" />
                  User
                </CardTitle>
                <CardDescription>
                  Database access with limited management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Permissions:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Create databases</li>
                    <li>• Execute SQL queries</li>
                    <li>• View own databases</li>
                    <li>• Basic monitoring</li>
                  </ul>
                  <div className="pt-2">
                    <Badge className="bg-blue-500">
                      {users.filter(u => u.role === 'user').length} users
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ShieldCheck className="w-5 h-5 mr-2 text-gray-500" />
                  Viewer
                </CardTitle>
                <CardDescription>
                  Read-only access to databases
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Permissions:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• View databases</li>
                    <li>• Read-only queries</li>
                    <li>• Basic monitoring</li>
                  </ul>
                  <div className="pt-2">
                    <Badge variant="secondary">
                      {users.filter(u => u.role === 'viewer').length} users
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                User Management Settings
              </CardTitle>
              <CardDescription>
                Configure user authentication and access policies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Current Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Authentication Method:</span>
                      <p className="text-muted-foreground">API Key</p>
                    </div>
                    <div>
                      <span className="font-medium">Session Timeout:</span>
                      <p className="text-muted-foreground">24 hours</p>
                    </div>
                    <div>
                      <span className="font-medium">Password Policy:</span>
                      <p className="text-muted-foreground">Not configured</p>
                    </div>
                    <div>
                      <span className="font-medium">Multi-Factor Auth:</span>
                      <p className="text-muted-foreground">Disabled</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Feature Status</h3>
                  <p className="text-sm text-muted-foreground">
                    User management features are currently in development. The system currently 
                    uses API key authentication. Full user authentication, role-based access 
                    control, and user management will be available in future releases.
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