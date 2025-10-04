import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { DatabasesView } from "@/components/databases/databases-view"

export default function DatabasesPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Databases</h1>
          <p className="text-muted-foreground">
            Manage your database instances and their configurations
          </p>
        </div>
        <DatabasesView />
      </div>
    </DashboardShell>
  )
}