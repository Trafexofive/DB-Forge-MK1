"""
Main DB-Forge TUI Application

Built with Textual for a modern, responsive terminal interface.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button, DataTable, Footer, Header, Input, Label, 
    Log, Placeholder, Static, TabbedContent, TabPane,
    Tree
)
from textual.screen import Screen
from textual.binding import Binding

from .config import Config
from .api.client import DBForgeAPIClient
from .widgets.dashboard import DashboardWidget
from .widgets.query_editor import QueryEditorWidget
from .widgets.database_manager import DatabaseManagerWidget
from .widgets.table_browser import TableBrowserWidget


class DBForgeTUI(App):
    """Main DB-Forge TUI application."""
    
    CSS_PATH = "tui.tcss"
    TITLE = "DB-Forge TUI"
    SUB_TITLE = "Interactive Database Management"
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("f1", "help", "Help"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+n", "new_database", "New Database"),
        Binding("ctrl+d", "toggle_dark", "Toggle Dark Mode"),
        Binding("ctrl+s", "settings", "Settings"),
    ]
    
    # Reactive attributes
    show_sidebar = reactive(True)
    current_database = reactive(None)
    connection_status = reactive("disconnected")
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.api_client = DBForgeAPIClient(config)
        
        # Application state
        self.databases: List[Dict[str, Any]] = []
        self.query_history: List[Dict[str, Any]] = []
        self.metrics = {
            "total_queries": 0,
            "avg_response_time": 0,
            "active_connections": 0
        }
    
    def compose(self) -> ComposeResult:
        """Compose the main UI layout."""
        
        yield Header()
        
        with Container(id="main-container"):
            
            # Sidebar with database list and navigation
            with Vertical(id="sidebar", classes="sidebar"):
                yield Static("🗄️ Databases", id="sidebar-title")
                yield Tree("Databases", id="database-tree")
                
                with Vertical(id="sidebar-actions"):
                    yield Button("➕ New", id="new-db-btn", classes="sidebar-btn")
                    yield Button("🔄 Refresh", id="refresh-btn", classes="sidebar-btn")
                    yield Button("⚙️ Settings", id="settings-btn", classes="sidebar-btn")
            
            # Main content area with tabs
            with TabbedContent(id="main-content"):
                
                # Dashboard tab
                with TabPane("📊 Dashboard", id="dashboard-tab"):
                    yield DashboardWidget(id="dashboard")
                
                # Query Editor tab  
                with TabPane("⚡ Query", id="query-tab"):
                    yield QueryEditorWidget(id="query-editor")
                
                # Database Manager tab
                with TabPane("🗃️ Manage", id="manage-tab"):
                    yield DatabaseManagerWidget(id="database-manager")
                
                # Table Browser tab
                with TabPane("📋 Browse", id="browse-tab"):
                    yield TableBrowserWidget(id="table-browser")
        
        # Status bar
        with Horizontal(id="status-bar"):
            yield Static("", id="connection-status")
            yield Static("", id="database-info")
            yield Static("", id="query-info")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the application after mounting."""
        
        # Set theme
        if self.config.ui.theme != "textual-dark":
            self.theme = self.config.ui.theme
        
        # Test connection to DB-Forge server
        await self.test_connection()
        
        # Load initial data
        await self.load_databases()
        
        # Start auto-refresh if enabled
        if self.config.ui.refresh_interval > 0:
            self.set_interval(self.config.ui.refresh_interval, self.refresh_data)
        
        # Update UI
        self.update_status_bar()
    
    @work(exclusive=True)
    async def test_connection(self) -> None:
        """Test connection to DB-Forge server."""
        try:
            health = await self.api_client.health_check()
            
            if health.get("status") == "healthy":
                self.connection_status = "connected"
                self.notify("✅ Connected to DB-Forge server", severity="information")
            else:
                self.connection_status = "error"
                self.notify(f"❌ Server error: {health.get('message', 'Unknown')}", severity="error")
                
        except Exception as e:
            self.connection_status = "disconnected"
            self.notify(f"❌ Connection failed: {str(e)}", severity="error")
    
    @work(exclusive=True)
    async def load_databases(self) -> None:
        """Load list of databases from server."""
        try:
            if self.connection_status == "connected":
                self.databases = await self.api_client.list_databases()
                self.update_database_tree()
                
                # Update dashboard
                dashboard = self.query_one("#dashboard", DashboardWidget)
                dashboard.update_data(self.databases, self.metrics)
                
        except Exception as e:
            self.notify(f"Failed to load databases: {str(e)}", severity="error")
    
    def update_database_tree(self) -> None:
        """Update the database tree in sidebar."""
        tree = self.query_one("#database-tree", Tree)
        tree.clear()
        
        databases_node = tree.root
        
        for db in self.databases:
            status_icon = "🟢" if db.get("status") == "running" else "🔴"
            db_node = databases_node.add(f"{status_icon} {db['name']}")
            db_node.data = db
    
    def update_status_bar(self) -> None:
        """Update the status bar with current information."""
        
        # Connection status
        status_widget = self.query_one("#connection-status", Static)
        if self.connection_status == "connected":
            status_widget.update("🟢 Connected")
        elif self.connection_status == "disconnected":
            status_widget.update("🔴 Disconnected")
        else:
            status_widget.update("⚠️ Error")
        
        # Database info
        db_info = self.query_one("#database-info", Static)
        db_count = len(self.databases)
        db_info.update(f"🗄️ {db_count} databases")
        
        # Query info
        query_info = self.query_one("#query-info", Static)
        if self.metrics["total_queries"] > 0:
            query_info.update(f"⚡ {self.metrics['total_queries']} queries, avg {self.metrics['avg_response_time']}ms")
        else:
            query_info.update("⚡ No queries yet")
    
    @work(exclusive=True)
    async def refresh_data(self) -> None:
        """Refresh all data from server."""
        await self.load_databases()
        self.update_status_bar()
    
    # Event handlers
    
    @on(Tree.NodeSelected, "#database-tree")
    async def on_database_selected(self, event: Tree.NodeSelected) -> None:
        """Handle database selection in tree."""
        if event.node.data:
            database = event.node.data
            self.current_database = database
            
            # Update database manager
            db_manager = self.query_one("#database-manager", DatabaseManagerWidget)
            await db_manager.set_database(database)
            
            # Update query editor
            query_editor = self.query_one("#query-editor", QueryEditorWidget)
            await query_editor.set_database(database)
            
            # Update table browser
            table_browser = self.query_one("#table-browser", TableBrowserWidget)
            await table_browser.set_database(database)
            
            self.notify(f"Selected database: {database['name']}", severity="information")
    
    @on(Button.Pressed, "#new-db-btn")
    async def on_new_database(self) -> None:
        """Handle new database button."""
        await self.action_new_database()
    
    @on(Button.Pressed, "#refresh-btn") 
    async def on_refresh_button(self) -> None:
        """Handle refresh button."""
        await self.action_refresh()
    
    @on(Button.Pressed, "#settings-btn")
    async def on_settings_button(self) -> None:
        """Handle settings button."""
        await self.action_settings()
    
    # Actions
    
    async def action_quit(self) -> None:
        """Quit the application."""
        # Save configuration
        self.config.save()
        self.exit()
    
    async def action_help(self) -> None:
        """Show help screen."""
        self.notify("Help: F1=Help, Ctrl+Q=Quit, Ctrl+R=Refresh, Ctrl+N=New DB", severity="information")
    
    async def action_refresh(self) -> None:
        """Refresh all data."""
        await self.refresh_data()
        self.notify("Data refreshed", severity="information")
    
    async def action_new_database(self) -> None:
        """Create a new database."""
        self.push_screen(NewDatabaseScreen(self.api_client))
    
    async def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark
        theme = "textual-dark" if self.dark else "textual-light"
        self.config.ui.theme = theme
        self.notify(f"Switched to {theme} theme", severity="information")
    
    async def action_settings(self) -> None:
        """Show settings screen."""
        self.push_screen(SettingsScreen(self.config))
    
    def watch_show_sidebar(self, show: bool) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar")
        sidebar.display = show


class NewDatabaseScreen(Screen):
    """Screen for creating a new database."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "save", "Create"),
    ]
    
    def __init__(self, api_client: DBForgeAPIClient):
        super().__init__()
        self.api_client = api_client
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Create New Database", id="dialog-title")
            yield Input(placeholder="Database name...", id="db-name-input")
            
            with Horizontal(id="dialog-buttons"):
                yield Button("Create", variant="primary", id="create-btn")
                yield Button("Cancel", id="cancel-btn")
    
    @on(Button.Pressed, "#create-btn")
    @on(Input.Submitted, "#db-name-input")
    async def on_create_database(self) -> None:
        """Create the database."""
        name_input = self.query_one("#db-name-input", Input)
        db_name = name_input.value.strip()
        
        if not db_name:
            self.notify("Please enter a database name", severity="error")
            return
        
        try:
            await self.api_client.spawn_database(db_name)
            self.app.notify(f"✅ Database '{db_name}' created successfully", severity="information")
            
            # Refresh main app data
            await self.app.refresh_data()
            self.dismiss()
            
        except Exception as e:
            self.notify(f"Failed to create database: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#cancel-btn")
    async def on_cancel(self) -> None:
        """Cancel database creation."""
        self.dismiss()


class SettingsScreen(Screen):
    """Settings configuration screen."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
    
    def compose(self) -> ComposeResult:
        with Container(id="settings-dialog"):
            yield Static("Settings", id="settings-title")
            
            with TabbedContent():
                with TabPane("Server"):
                    yield Input(value=self.config.server.url, id="server-url")
                    yield Input(value=self.config.server.api_key or "", password=True, id="api-key")
                
                with TabPane("UI"):
                    yield Input(value=self.config.ui.theme, id="theme")
                    yield Input(value=str(self.config.ui.refresh_interval), id="refresh-interval")
                
                with TabPane("Editor"):
                    yield Input(value=str(self.config.editor.tab_size), id="tab-size")
            
            with Horizontal(id="settings-buttons"):
                yield Button("Save", variant="primary", id="save-btn")
                yield Button("Cancel", id="cancel-btn")
    
    @on(Button.Pressed, "#save-btn")
    async def on_save_settings(self) -> None:
        """Save settings."""
        try:
            # Update config from inputs
            self.config.server.url = self.query_one("#server-url", Input).value
            self.config.server.api_key = self.query_one("#api-key", Input).value
            self.config.ui.theme = self.query_one("#theme", Input).value
            self.config.ui.refresh_interval = int(self.query_one("#refresh-interval", Input).value)
            self.config.editor.tab_size = int(self.query_one("#tab-size", Input).value)
            
            # Validate and save
            if self.config.validate():
                self.config.save()
                self.app.notify("Settings saved successfully", severity="information")
                self.dismiss()
            else:
                self.notify("Invalid configuration values", severity="error")
                
        except ValueError as e:
            self.notify(f"Invalid input: {str(e)}", severity="error")
        except Exception as e:
            self.notify(f"Failed to save settings: {str(e)}", severity="error")
    
    @on(Button.Pressed, "#cancel-btn")
    async def on_cancel_settings(self) -> None:
        """Cancel settings."""
        self.dismiss()