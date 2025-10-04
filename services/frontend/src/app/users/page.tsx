import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { UsersView } from "@/components/users/users-view"

export default function UsersPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Users</h1>
          <p className="text-muted-foreground">
            Manage user accounts and access permissions
          </p>
        </div>
        <UsersView />
      </div>
    </DashboardShell>
  )
}