"""
Database Manager Widget - Database administration and management
"""

from typing import Any, Dict, List, Optional

from textual import on, work
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button, DataTable, Input, Label, Static, 
    ListView, ListItem, Collapsible
)
from textual.widget import Widget

from ..api.client import DBForgeAPIClient


class DatabaseManagerWidget(Widget):
    """Database management and administration interface."""
    
    DEFAULT_CSS = """
    DatabaseManagerWidget {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .db-info {
        border: round $primary;
        padding: 1;
    }
    
    .table-list {
        border: round $primary;
        padding: 1;
    }
    
    .db-actions {
        border: round $primary;
        padding: 1;
    }
    
    .db-stats {
        border: round $primary;
        padding: 1;
    }
    
    .action-button {
        width: 100%;
        margin: 1 0;
    }
    """
    
    current_database = reactive(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client: Optional[DBForgeAPIClient] = None
        
    def compose(self):
        """Compose the database manager layout."""
        
        # Database info panel
        with Container(classes="db-info"):
            yield Label("🗄️ Database Information")
            yield Static("No database selected", id="db-name")
            yield Static("Status: Unknown", id="db-status")
            yield Static("Container: None", id="db-container")
            yield Static("Created: Unknown", id="db-created")
        
        # Database actions panel
        with Container(classes="db-actions"):
            yield Label("⚙️ Database Actions")
            
            yield Button("🔄 Restart Database", id="restart-db-btn", classes="action-button")
            yield Button("📊 View Statistics", id="stats-btn", classes="action-button")
            yield Button("🔧 Optimize Database", id="optimize-btn", classes="action-button")
            yield Button("💾 Backup Database", id="backup-btn", classes="action-button")
            yield Button("🗑️ Delete Database", id="delete-btn", classes="action-button", variant="error")
        
        # Table list panel
        with Container(classes="table-list"):
            yield Label("📋 Tables")
            
            with Horizontal():
                yield Button("➕ New Table", id="new-table-btn")
                yield Button("🔄 Refresh", id="refresh-tables-btn")
            
            yield ListView(id="tables-list")
        
        # Database statistics panel
        with Container(classes="db-stats"):
            yield Label("📊 Database Statistics")
            yield DataTable(id="stats-table")
    
    def on_mount(self) -> None:
        """Initialize database manager components."""
        
        # Setup stats table
        stats_table = self.query_one("#stats-table", DataTable)
        stats_table.add_columns("Metric", "Value")
        stats_table.cursor_type = "row"
        
        # Initial state
        self._update_display()
    
    async def set_database(self, database: Dict[str, Any]) -> None:
        """Set the current database."""
        
        self.current_database = database
        await self._load_database_info()
        await self._load_tables()
        await self._load_statistics()
        
        self._update_display()
    
    def set_api_client(self, client: DBForgeAPIClient) -> None:
        """Set the API client."""
        self.api_client = client
    
    def _update_display(self) -> None:
        """Update the display with current database info."""
        
        if self.current_database:
            db = self.current_database
            
            # Update info panel
            self.query_one("#db-name", Static).update(f"Name: {db.get('name', 'Unknown')}")
            
            status = db.get('status', 'unknown')
            status_icon = "🟢" if status == "running" else "🔴"
            self.query_one("#db-status", Static).update(f"Status: {status_icon} {status.upper()}")
            
            self.query_one("#db-container", Static).update(f"Container: {db.get('container_id', 'None')[:12]}...")
            
        else:
            # No database selected
            self.query_one("#db-name", Static).update("No database selected")
            self.query_one("#db-status", Static).update("Status: Unknown")
            self.query_one("#db-container", Static).update("Container: None")
    
    @work(exclusive=True)
    async def _load_database_info(self) -> None:
        """Load detailed database information."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            # Get additional database info if needed
            pass
            
        except Exception as e:
            self.app.notify(f"Failed to load database info: {str(e)}", severity="error")
    
    @work(exclusive=True)
    async def _load_tables(self) -> None:
        """Load list of tables in the database."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            # Get table list
            result = await self.api_client.execute_query(
                self.current_database["name"],
                "SELECT name, type FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            
            tables = result.get("data", [])
            self._update_tables_list(tables)
            
        except Exception as e:
            self.app.notify(f"Failed to load tables: {str(e)}", severity="error")
    
    def _update_tables_list(self, tables: List[Dict[str, Any]]) -> None:
        """Update the tables list."""
        
        tables_list = self.query_one("#tables-list", ListView)
        tables_list.clear()
        
        if not tables:
            tables_list.append(ListItem(Label("No tables found")))
            return
        
        for table in tables:
            table_name = table.get("name", "Unknown")
            table_type = table.get("type", "table")
            
            # Add table item
            icon = "📋" if table_type == "table" else "👁️"
            item_text = f"{icon} {table_name}"
            
            table_item = ListItem(Label(item_text))
            table_item.table_name = table_name
            tables_list.append(table_item)
    
    @work(exclusive=True)
    async def _load_statistics(self) -> None:
        """Load database statistics."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            stats = await self.api_client.get_database_stats(self.current_database["name"])
            self._update_stats_display(stats)
            
        except Exception as e:
            self.app.notify(f"Failed to load statistics: {str(e)}", severity="error")
    
    def _update_stats_display(self, stats: Dict[str, Any]) -> None:
        """Update statistics display."""
        
        stats_table = self.query_one("#stats-table", DataTable)
        stats_table.clear()
        
        # Add statistics rows
        stats_table.add_row("Tables", str(stats.get("table_count", 0)))
        stats_table.add_row("Size (MB)", f"{stats.get('size_mb', 0):.2f}")
        stats_table.add_row("Size (Bytes)", str(stats.get("size_bytes", 0)))
        
        # Add more detailed stats if available
        if "error" in stats:
            stats_table.add_row("Error", stats["error"])
    
    # Event handlers
    
    @on(Button.Pressed, "#restart-db-btn")
    async def on_restart_database(self) -> None:
        """Restart the database."""
        
        if not self.api_client or not self.current_database:
            return
        
        self.app.notify("Database restart not implemented yet", severity="warning")
    
    @on(Button.Pressed, "#stats-btn")
    async def on_view_statistics(self) -> None:
        """View detailed database statistics."""
        await self._load_statistics()
        self.app.notify("Statistics refreshed", severity="information")
    
    @on(Button.Pressed, "#optimize-btn")
    async def on_optimize_database(self) -> None:
        """Optimize the database."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            await self.api_client.execute_query(
                self.current_database["name"],
                "VACUUM"
            )
            
            self.app.notify("Database optimized successfully", severity="information")
            await self._load_statistics()  # Refresh stats
            
        except Exception as e:
            self.app.notify(f"Failed to optimize database: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#backup-btn")
    async def on_backup_database(self) -> None:
        """Backup the database."""
        self.app.notify("Database backup not implemented yet", severity="warning")
    
    @on(Button.Pressed, "#delete-btn")
    async def on_delete_database(self) -> None:
        """Delete the database."""
        
        if not self.api_client or not self.current_database:
            return
        
        # Show confirmation dialog
        self.app.push_screen(DeleteDatabaseConfirmation(
            self.current_database["name"],
            self._confirm_delete
        ))
    
    async def _confirm_delete(self, confirmed: bool) -> None:
        """Handle delete confirmation."""
        
        if not confirmed or not self.api_client or not self.current_database:
            return
        
        try:
            await self.api_client.prune_database(self.current_database["name"])
            
            self.app.notify(f"Database '{self.current_database['name']}' deleted successfully", severity="information")
            
            # Clear current database
            self.current_database = None
            self._update_display()
            
            # Refresh main app
            if hasattr(self.app, 'refresh_data'):
                await self.app.refresh_data()
            
        except Exception as e:
            self.app.notify(f"Failed to delete database: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#new-table-btn")
    async def on_new_table(self) -> None:
        """Create a new table."""
        
        if not self.current_database:
            self.app.notify("No database selected", severity="error")
            return
        
        self.app.push_screen(CreateTableDialog(self.api_client, self.current_database["name"]))
    
    @on(Button.Pressed, "#refresh-tables-btn")
    async def on_refresh_tables(self) -> None:
        """Refresh tables list."""
        await self._load_tables()
        self.app.notify("Tables list refreshed", severity="information")
    
    @on(ListView.Selected, "#tables-list")
    async def on_table_selected(self, event) -> None:
        """Handle table selection."""
        
        if hasattr(event.item, 'table_name'):
            table_name = event.item.table_name
            
            # Show table info or switch to table browser
            self.app.notify(f"Selected table: {table_name}", severity="information")


class DeleteDatabaseConfirmation:
    """Confirmation dialog for database deletion."""
    
    def __init__(self, db_name: str, callback):
        self.db_name = db_name
        self.callback = callback
    
    # Implementation would go here - simplified for now


class CreateTableDialog:
    """Dialog for creating a new table."""
    
    def __init__(self, api_client: DBForgeAPIClient, db_name: str):
        self.api_client = api_client
        self.db_name = db_name
    
    # Implementation would go here - simplified for now