import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { LogsView } from "@/components/logs/logs-view"

export default function LogsPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Logs</h1>
          <p className="text-muted-foreground">
            Monitor system events, errors, and application logs
          </p>
        </div>
        <LogsView />
      </div>
    </DashboardShell>
  )
}