import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { ConnectionsView } from "@/components/connections/connections-view"

export default function ConnectionsPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Connections</h1>
          <p className="text-muted-foreground">
            Monitor active connections and connection pools
          </p>
        </div>
        <ConnectionsView />
      </div>
    </DashboardShell>
  )
}