import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { DatabaseOverview } from "@/components/dashboard/database-overview"
import { SystemMetrics } from "@/components/dashboard/system-metrics"

export default function Home() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">DB-Forge Admin</h1>
          <p className="text-muted-foreground">
            Manage your databases and monitor system health
          </p>
        </div>
        <SystemMetrics />
        <DatabaseOverview />
      </div>
    </DashboardShell>
  )
}
