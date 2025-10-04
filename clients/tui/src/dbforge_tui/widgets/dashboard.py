"""
Dashboard Widget - Overview of databases and metrics
"""

from datetime import datetime
from typing import Any, Dict, List

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, Static, Label, Sparkline
from textual.widget import Widget


class DashboardWidget(Widget):
    """Main dashboard showing database overview and metrics."""
    
    DEFAULT_CSS = """
    DashboardWidget {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
    }
    
    .metric-box {
        border: round $primary;
        height: 8;
        padding: 1;
    }
    
    .database-list {
        border: round $primary;
        padding: 1;
    }
    
    .activity-log {
        border: round $primary;
        padding: 1;
    }
    
    .metric-value {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    
    .metric-label {
        text-align: center;
        color: $text-muted;
    }
    """
    
    databases = reactive([])
    metrics = reactive({})
    
    def compose(self):
        """Compose the dashboard layout."""
        
        # Metrics boxes
        with Container(classes="metric-box"):
            yield Static("📊", classes="metric-icon")
            yield Label("0", id="total-databases", classes="metric-value")
            yield Label("Databases", classes="metric-label")
        
        with Container(classes="metric-box"):
            yield Static("⚡", classes="metric-icon") 
            yield Label("0", id="total-queries", classes="metric-value")
            yield Label("Queries", classes="metric-label")
        
        with Container(classes="metric-box"):
            yield Static("💾", classes="metric-icon")
            yield Label("0MB", id="total-memory", classes="metric-value")  
            yield Label("Memory", classes="metric-label")
        
        with Container(classes="metric-box"):
            yield Static("⏱️", classes="metric-icon")
            yield Label("0ms", id="avg-response", classes="metric-value")
            yield Label("Avg Response", classes="metric-label")
        
        # Database list
        with Container(classes="database-list"):
            yield Label("🗄️ Active Databases")
            yield DataTable(id="database-table")
        
        # Activity log
        with Container(classes="activity-log"):
            yield Label("⚡ Recent Activity")
            yield DataTable(id="activity-table")
    
    def on_mount(self) -> None:
        """Initialize dashboard components."""
        
        # Setup database table
        db_table = self.query_one("#database-table", DataTable)
        db_table.add_columns("Name", "Status", "Tables", "Size")
        db_table.cursor_type = "row"
        
        # Setup activity table
        activity_table = self.query_one("#activity-table", DataTable)
        activity_table.add_columns("Time", "Query", "Duration", "Status")
        activity_table.cursor_type = "row"
    
    def update_data(self, databases: List[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
        """Update dashboard with new data."""
        
        self.databases = databases
        self.metrics = metrics
        
        # Update metric displays
        self._update_metrics(databases, metrics)
        
        # Update database table
        self._update_database_table(databases)
    
    def _update_metrics(self, databases: List[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
        """Update metric displays."""
        
        # Total databases
        total_db_label = self.query_one("#total-databases", Label)
        total_db_label.update(str(len(databases)))
        
        # Total queries
        total_queries_label = self.query_one("#total-queries", Label)
        total_queries_label.update(str(metrics.get("total_queries", 0)))
        
        # Total memory usage
        total_memory = sum(
            db.get("stats", {}).get("size_mb", 0) 
            for db in databases
        )
        memory_label = self.query_one("#total-memory", Label)
        memory_label.update(f"{total_memory:.1f}MB")
        
        # Average response time
        avg_response_label = self.query_one("#avg-response", Label)
        avg_response_label.update(f"{metrics.get('avg_response_time', 0)}ms")
    
    def _update_database_table(self, databases: List[Dict[str, Any]]) -> None:
        """Update database table with current data."""
        
        db_table = self.query_one("#database-table", DataTable)
        db_table.clear()
        
        for db in databases:
            status_icon = "🟢" if db.get("status") == "running" else "🔴"
            status = f"{status_icon} {db.get('status', 'unknown').upper()}"
            
            stats = db.get("stats", {})
            table_count = str(stats.get("table_count", "?"))
            size = f"{stats.get('size_mb', 0):.1f}MB"
            
            db_table.add_row(
                db.get("name", "Unknown"),
                status,
                table_count,
                size
            )
    
    def add_activity(self, timestamp: datetime, query: str, duration_ms: int, success: bool) -> None:
        """Add activity to the activity log."""
        
        activity_table = self.query_one("#activity-table", DataTable)
        
        # Format timestamp
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Truncate long queries
        query_display = query[:50] + "..." if len(query) > 50 else query
        
        # Format status
        status_icon = "✅" if success else "❌"
        status = f"{status_icon} {'SUCCESS' if success else 'ERROR'}"
        
        # Add to table (insert at top)
        activity_table.add_row(
            time_str,
            query_display, 
            f"{duration_ms}ms",
            status,
            key=str(timestamp.timestamp())  # Unique key
        )
        
        # Keep only last 20 entries
        if activity_table.row_count > 20:
            # Remove oldest rows
            rows_to_remove = activity_table.row_count - 20
            for _ in range(rows_to_remove):
                try:
                    activity_table.remove_row(activity_table.get_row_at(activity_table.row_count - 1))
                except:
                    break


class MetricCard(Widget):
    """Individual metric display card."""
    
    DEFAULT_CSS = """
    MetricCard {
        width: 100%;
        height: 6;
        border: round $primary;
        padding: 1;
    }
    
    .metric-icon {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    
    .metric-value {
        text-align: center; 
        text-style: bold;
        color: $success;
        content-align: center middle;
    }
    
    .metric-label {
        text-align: center;
        color: $text-muted;
    }
    """
    
    def __init__(self, icon: str, label: str, value: str = "0", **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.label = label
        self.value = value
    
    def compose(self):
        yield Static(self.icon, classes="metric-icon")
        yield Label(self.value, classes="metric-value") 
        yield Label(self.label, classes="metric-label")
    
    def update_value(self, new_value: str) -> None:
        """Update the metric value."""
        value_label = self.query_one(Label)
        value_label.update(new_value)