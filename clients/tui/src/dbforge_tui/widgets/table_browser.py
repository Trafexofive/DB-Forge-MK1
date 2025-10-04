"""
Table Browser Widget - Browse and manipulate table data
"""

from typing import Any, Dict, List, Optional

from textual import on, work
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button, DataTable, Input, Label, Static, 
    Select, Checkbox
)
from textual.widget import Widget

from ..api.client import DBForgeAPIClient


class TableBrowserWidget(Widget):
    """Table data browser with filtering and pagination."""
    
    DEFAULT_CSS = """
    TableBrowserWidget {
        layout: vertical;
    }
    
    .browser-toolbar {
        height: 5;
        dock: top;
        border: round $primary;
        padding: 1;
    }
    
    .data-table {
        border: round $primary;
    }
    
    .browser-status {
        height: 3;
        dock: bottom;
        border: round $primary;
        padding: 1;
    }
    
    .filter-controls {
        layout: horizontal;
    }
    
    .pagination-controls {
        layout: horizontal;
        align: center;
    }
    """
    
    current_database = reactive(None)
    current_table = reactive(None)
    current_page = reactive(1)
    rows_per_page = reactive(100)
    total_rows = reactive(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client: Optional[DBForgeAPIClient] = None
        self.filters = {}
        
    def compose(self):
        """Compose the table browser layout."""
        
        # Toolbar
        with Container(classes="browser-toolbar"):
            with Horizontal():
                yield Select(
                    options=[("Select table...", "")],
                    id="table-select",
                    allow_blank=False
                )
                yield Button("🔄 Refresh", id="refresh-data-btn")
                yield Button("➕ Add Row", id="add-row-btn")
                yield Button("📄 Export", id="export-btn")
            
            # Filter controls
            with Horizontal(classes="filter-controls"):
                yield Label("Filter:")
                yield Input(placeholder="Column name...", id="filter-column")
                yield Input(placeholder="Value...", id="filter-value")
                yield Button("🔍 Apply", id="apply-filter-btn")
                yield Button("🧹 Clear", id="clear-filter-btn")
        
        # Main data table
        yield DataTable(id="data-table", classes="data-table")
        
        # Status and pagination
        with Container(classes="browser-status"):
            with Horizontal():
                # Status info
                yield Static("No data", id="status-info")
                
                # Pagination controls
                with Horizontal(classes="pagination-controls"):
                    yield Button("⏮️", id="first-page-btn")
                    yield Button("◀️", id="prev-page-btn")
                    yield Static("Page 1", id="page-info")
                    yield Button("▶️", id="next-page-btn")
                    yield Button("⏭️", id="last-page-btn")
                
                # Rows per page
                yield Label("Rows:")
                yield Select(
                    options=[("50", 50), ("100", 100), ("250", 250), ("500", 500)],
                    value=100,
                    id="rows-per-page-select"
                )
    
    def on_mount(self) -> None:
        """Initialize table browser."""
        
        # Setup data table
        data_table = self.query_one("#data-table", DataTable)
        data_table.cursor_type = "row"
        data_table.zebra_stripes = True
        
        self._update_status()
    
    async def set_database(self, database: Dict[str, Any]) -> None:
        """Set the current database and load tables."""
        
        self.current_database = database
        await self._load_table_list()
    
    def set_api_client(self, client: DBForgeAPIClient) -> None:
        """Set the API client."""
        self.api_client = client
    
    @work(exclusive=True)
    async def _load_table_list(self) -> None:
        """Load list of tables for the database."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            result = await self.api_client.execute_query(
                self.current_database["name"],
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            
            tables = result.get("data", [])
            
            # Update table select options
            options = [("Select table...", "")]
            for table in tables:
                table_name = table["name"]
                options.append((table_name, table_name))
            
            table_select = self.query_one("#table-select", Select)
            table_select.set_options(options)
            
        except Exception as e:
            self.app.notify(f"Failed to load tables: {str(e)}", severity="error")
    
    @work(exclusive=True)
    async def _load_table_data(self, offset: int = 0) -> None:
        """Load data for the current table."""
        
        if not self.api_client or not self.current_database or not self.current_table:
            return
        
        try:
            # Build query with filters and pagination
            query = f"SELECT * FROM {self.current_table}"
            params = []
            
            # Add filters
            if self.filters:
                where_conditions = []
                for column, value in self.filters.items():
                    where_conditions.append(f"{column} LIKE ?")
                    params.append(f"%{value}%")
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            # Add pagination
            query += f" LIMIT ? OFFSET ?"
            params.extend([self.rows_per_page, offset])
            
            # Execute query
            result = await self.api_client.execute_query(
                self.current_database["name"],
                query,
                params
            )
            
            data = result.get("data", [])
            
            # Also get total count
            count_query = f"SELECT COUNT(*) as count FROM {self.current_table}"
            count_params = []
            
            if self.filters:
                where_conditions = []
                for column, value in self.filters.items():
                    where_conditions.append(f"{column} LIKE ?")
                    count_params.append(f"%{value}%")
                
                if where_conditions:
                    count_query += " WHERE " + " AND ".join(where_conditions)
            
            count_result = await self.api_client.execute_query(
                self.current_database["name"],
                count_query,
                count_params
            )
            
            self.total_rows = count_result.get("data", [{}])[0].get("count", 0)
            
            # Display data
            self._display_data(data)
            self._update_status()
            
        except Exception as e:
            self.app.notify(f"Failed to load table data: {str(e)}", severity="error")
    
    def _display_data(self, data: List[Dict[str, Any]]) -> None:
        """Display data in the table."""
        
        data_table = self.query_one("#data-table", DataTable)
        data_table.clear()
        
        if not data:
            # No data to display
            return
        
        # Add columns based on first row
        first_row = data[0]
        columns = list(first_row.keys())
        data_table.add_columns(*columns)
        
        # Add data rows
        for row in data:
            values = [str(row.get(col, "")) for col in columns]
            data_table.add_row(*values)
    
    def _update_status(self) -> None:
        """Update status information."""
        
        status_info = self.query_one("#status-info", Static)
        
        if self.current_table:
            start_row = ((self.current_page - 1) * self.rows_per_page) + 1
            end_row = min(self.current_page * self.rows_per_page, self.total_rows)
            
            status_text = f"Table: {self.current_table} | Rows {start_row}-{end_row} of {self.total_rows}"
            
            if self.filters:
                status_text += f" | Filtered"
        else:
            status_text = "No table selected"
        
        status_info.update(status_text)
        
        # Update page info
        total_pages = max(1, (self.total_rows + self.rows_per_page - 1) // self.rows_per_page)
        page_info = self.query_one("#page-info", Static)
        page_info.update(f"Page {self.current_page} of {total_pages}")
        
        # Update button states
        first_btn = self.query_one("#first-page-btn", Button)
        prev_btn = self.query_one("#prev-page-btn", Button)
        next_btn = self.query_one("#next-page-btn", Button)
        last_btn = self.query_one("#last-page-btn", Button)
        
        first_btn.disabled = self.current_page <= 1
        prev_btn.disabled = self.current_page <= 1
        next_btn.disabled = self.current_page >= total_pages
        last_btn.disabled = self.current_page >= total_pages
    
    # Event handlers
    
    @on(Select.Changed, "#table-select")
    async def on_table_selected(self, event) -> None:
        """Handle table selection."""
        
        if event.value:
            self.current_table = event.value
            self.current_page = 1
            self.filters = {}
            
            # Clear existing filters
            self.query_one("#filter-column", Input).value = ""
            self.query_one("#filter-value", Input).value = ""
            
            await self._load_table_data()
    
    @on(Button.Pressed, "#refresh-data-btn")
    async def on_refresh_data(self) -> None:
        """Refresh table data."""
        
        if self.current_table:
            await self._load_table_data((self.current_page - 1) * self.rows_per_page)
            self.app.notify("Data refreshed", severity="information")
    
    @on(Button.Pressed, "#apply-filter-btn")
    async def on_apply_filter(self) -> None:
        """Apply data filter."""
        
        column = self.query_one("#filter-column", Input).value.strip()
        value = self.query_one("#filter-value", Input).value.strip()
        
        if column and value:
            self.filters[column] = value
            self.current_page = 1
            await self._load_table_data()
            self.app.notify(f"Filter applied: {column} = {value}", severity="information")
        else:
            self.app.notify("Please enter both column and value", severity="warning")
    
    @on(Button.Pressed, "#clear-filter-btn")
    async def on_clear_filter(self) -> None:
        """Clear all filters."""
        
        self.filters = {}
        self.current_page = 1
        
        # Clear filter inputs
        self.query_one("#filter-column", Input).value = ""
        self.query_one("#filter-value", Input).value = ""
        
        if self.current_table:
            await self._load_table_data()
            self.app.notify("Filters cleared", severity="information")
    
    # Pagination handlers
    
    @on(Button.Pressed, "#first-page-btn")
    async def on_first_page(self) -> None:
        """Go to first page."""
        
        if self.current_page > 1:
            self.current_page = 1
            await self._load_table_data()
    
    @on(Button.Pressed, "#prev-page-btn")
    async def on_prev_page(self) -> None:
        """Go to previous page."""
        
        if self.current_page > 1:
            self.current_page -= 1
            await self._load_table_data((self.current_page - 1) * self.rows_per_page)
    
    @on(Button.Pressed, "#next-page-btn")
    async def on_next_page(self) -> None:
        """Go to next page."""
        
        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            await self._load_table_data((self.current_page - 1) * self.rows_per_page)
    
    @on(Button.Pressed, "#last-page-btn")
    async def on_last_page(self) -> None:
        """Go to last page."""
        
        total_pages = max(1, (self.total_rows + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page = total_pages
            await self._load_table_data((self.current_page - 1) * self.rows_per_page)
    
    @on(Select.Changed, "#rows-per-page-select")
    async def on_rows_per_page_changed(self, event) -> None:
        """Handle rows per page change."""
        
        if event.value and event.value != self.rows_per_page:
            self.rows_per_page = event.value
            self.current_page = 1
            
            if self.current_table:
                await self._load_table_data()
    
    @on(Button.Pressed, "#add-row-btn")
    async def on_add_row(self) -> None:
        """Add new row to table."""
        
        if not self.current_table:
            self.app.notify("No table selected", severity="error")
            return
        
        self.app.notify("Add row functionality not implemented yet", severity="warning")
    
    @on(Button.Pressed, "#export-btn")
    async def on_export_data(self) -> None:
        """Export table data."""
        
        if not self.current_table:
            self.app.notify("No table selected", severity="error")
            return
        
        self.app.notify("Export functionality not implemented yet", severity="warning")