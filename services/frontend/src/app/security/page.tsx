import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { SecurityView } from "@/components/security/security-view"

export default function SecurityPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security</h1>
          <p className="text-muted-foreground">
            Monitor security events and manage access controls
          </p>
        </div>
        <SecurityView />
      </div>
    </DashboardShell>
  )
}