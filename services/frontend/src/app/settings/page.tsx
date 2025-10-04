import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { SettingsView } from "@/components/settings/settings-view"

export default function SettingsPage() {
  return (
    <DashboardShell>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure system settings and preferences
          </p>
        </div>
        <SettingsView />
      </div>
    </DashboardShell>
  )
}