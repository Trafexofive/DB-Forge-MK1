"""
Query Editor Widget - SQL editing and execution
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from textual import on, work
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button, DataTable, Input, Label, Static, TextArea, 
    ListView, ListItem, TabbedContent, TabPane
)
from textual.widget import Widget

from ..api.client import DBForgeAPIClient, QueryMetrics


class QueryEditorWidget(Widget):
    """SQL query editor with syntax highlighting and execution."""
    
    DEFAULT_CSS = """
    QueryEditorWidget {
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .sql-editor {
        border: round $primary;
        padding: 1;
    }
    
    .results-panel {
        border: round $primary;  
        padding: 1;
    }
    
    .query-history {
        border: round $primary;
        padding: 1;
    }
    
    .schema-panel {
        border: round $primary;
        padding: 1;
    }
    
    .editor-toolbar {
        height: 3;
        dock: top;
    }
    """
    
    current_database = reactive(None)
    query_metrics = reactive(QueryMetrics())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_client: Optional[DBForgeAPIClient] = None
        
    def compose(self):
        """Compose the query editor layout."""
        
        # SQL Editor panel
        with Container(classes="sql-editor"):
            # Toolbar
            with Horizontal(classes="editor-toolbar"):
                yield Button("▶️ Execute", id="execute-btn", variant="primary")
                yield Button("💾 Save", id="save-btn") 
                yield Button("🗂️ Format", id="format-btn")
                yield Button("🔄 Clear", id="clear-btn")
            
            # Editor
            yield TextArea(
                "",
                language="sql",
                id="sql-editor",
                show_line_numbers=True
            )
        
        # Results panel
        with Container(classes="results-panel"):
            yield Label("📊 Query Results")
            
            with TabbedContent():
                with TabPane("Data", id="data-tab"):
                    yield DataTable(id="results-table")
                
                with TabPane("Messages", id="messages-tab"):
                    yield Static("", id="query-messages")
                
                with TabPane("Explain", id="explain-tab"):
                    yield DataTable(id="explain-table")
        
        # Query history panel
        with Container(classes="query-history"):
            yield Label("🕐 Query History")
            yield ListView(id="history-list")
        
        # Schema panel
        with Container(classes="schema-panel"):
            yield Label("🗂️ Database Schema")
            yield ListView(id="schema-list")
    
    def on_mount(self) -> None:
        """Initialize editor components."""
        
        # Setup results table
        results_table = self.query_one("#results-table", DataTable)
        results_table.cursor_type = "row"
        
        # Setup explain table
        explain_table = self.query_one("#explain-table", DataTable)
        explain_table.add_columns("Detail", "selectid", "order", "from", "detail")
        
        # Focus on SQL editor
        sql_editor = self.query_one("#sql-editor", TextArea)
        sql_editor.focus()
    
    async def set_database(self, database: Dict[str, Any]) -> None:
        """Set the current database and load schema."""
        
        self.current_database = database
        
        if self.api_client:
            await self._load_schema()
    
    def set_api_client(self, client: DBForgeAPIClient) -> None:
        """Set the API client for executing queries."""
        self.api_client = client
    
    @work(exclusive=True)
    async def _load_schema(self) -> None:
        """Load database schema information."""
        
        if not self.api_client or not self.current_database:
            return
        
        try:
            schema = await self.api_client.get_database_schema(
                self.current_database["name"]
            )
            
            self._update_schema_list(schema)
            
        except Exception as e:
            self.app.notify(f"Failed to load schema: {str(e)}", severity="error")
    
    def _update_schema_list(self, schema: Dict[str, List[Dict[str, Any]]]) -> None:
        """Update schema list with table and column information."""
        
        schema_list = self.query_one("#schema-list", ListView)
        schema_list.clear()
        
        for table_name, columns in schema.items():
            # Add table header
            table_item = ListItem(Label(f"📋 {table_name}"))
            schema_list.append(table_item)
            
            # Add columns
            for column in columns:
                col_name = column.get("name", "")
                col_type = column.get("type", "")
                
                # Format column info
                col_info = f"  ├─ {col_name} ({col_type})"
                
                if column.get("pk"):  # Primary key
                    col_info += " 🔑"
                if column.get("notnull"):  # Not null
                    col_info += " ⚠️"
                
                col_item = ListItem(Label(col_info))
                schema_list.append(col_item)
    
    @on(Button.Pressed, "#execute-btn")
    async def on_execute_query(self) -> None:
        """Execute the current SQL query."""
        await self._execute_current_query()
    
    @on(Button.Pressed, "#save-btn") 
    async def on_save_query(self) -> None:
        """Save the current query."""
        sql_editor = self.query_one("#sql-editor", TextArea)
        query = sql_editor.text.strip()
        
        if query:
            # Add to history
            self._add_to_history(query)
            self.app.notify("Query saved to history", severity="information")
    
    @on(Button.Pressed, "#format-btn")
    async def on_format_query(self) -> None:
        """Format the current SQL query."""
        sql_editor = self.query_one("#sql-editor", TextArea)
        query = sql_editor.text.strip()
        
        if query:
            # Basic SQL formatting (simplified)
            formatted = self._format_sql(query)
            sql_editor.text = formatted
            self.app.notify("Query formatted", severity="information")
    
    @on(Button.Pressed, "#clear-btn")
    async def on_clear_query(self) -> None:
        """Clear the query editor."""
        sql_editor = self.query_one("#sql-editor", TextArea)
        sql_editor.text = ""
        
        # Clear results
        results_table = self.query_one("#results-table", DataTable)
        results_table.clear()
        
        messages = self.query_one("#query-messages", Static)
        messages.update("")
    
    @work(exclusive=True)
    async def _execute_current_query(self) -> None:
        """Execute the current query in the editor."""
        
        if not self.api_client or not self.current_database:
            self.app.notify("No database selected", severity="error")
            return
        
        sql_editor = self.query_one("#sql-editor", TextArea)
        query = sql_editor.text.strip()
        
        if not query:
            self.app.notify("Please enter a SQL query", severity="warning")
            return
        
        # Record start time
        start_time = datetime.now()
        
        try:
            # Execute query
            result = await self.api_client.execute_query(
                self.current_database["name"], 
                query
            )
            
            # Calculate duration
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update metrics
            self.query_metrics.add_query(query, duration_ms, True)
            
            # Display results
            self._display_results(result, duration_ms)
            
            # Add to history
            self._add_to_history(query, duration_ms, True)
            
            self.app.notify(f"Query executed in {duration_ms}ms", severity="information")
            
        except Exception as e:
            # Calculate duration
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update metrics
            self.query_metrics.add_query(query, duration_ms, False, str(e))
            
            # Display error
            self._display_error(str(e))
            
            # Add to history
            self._add_to_history(query, duration_ms, False, str(e))
            
            self.app.notify(f"Query failed: {str(e)}", severity="error")
    
    def _display_results(self, result: Dict[str, Any], duration_ms: int) -> None:
        """Display query results in the results table."""
        
        results_table = self.query_one("#results-table", DataTable)
        results_table.clear()
        
        data = result.get("data", [])
        rows_affected = result.get("rows_affected", 0)
        
        if data and isinstance(data, list) and len(data) > 0:
            # Add columns based on first row
            first_row = data[0]
            if isinstance(first_row, dict):
                columns = list(first_row.keys())
                results_table.add_columns(*columns)
                
                # Add data rows
                for row in data:
                    values = [str(row.get(col, "")) for col in columns]
                    results_table.add_row(*values)
        
        # Update messages
        messages = self.query_one("#query-messages", Static)
        if data:
            messages.update(f"✅ Query completed successfully\n📊 {len(data)} rows returned\n⏱️ Duration: {duration_ms}ms")
        else:
            messages.update(f"✅ Query completed successfully\n📝 {rows_affected} rows affected\n⏱️ Duration: {duration_ms}ms")
    
    def _display_error(self, error: str) -> None:
        """Display query error."""
        
        # Clear results table
        results_table = self.query_one("#results-table", DataTable)
        results_table.clear()
        
        # Show error message
        messages = self.query_one("#query-messages", Static)
        messages.update(f"❌ Query failed\n🚫 Error: {error}")
    
    def _add_to_history(
        self, 
        query: str, 
        duration_ms: Optional[int] = None, 
        success: Optional[bool] = None,
        error: Optional[str] = None
    ) -> None:
        """Add query to history list."""
        
        history_list = self.query_one("#history-list", ListView)
        
        # Format history item
        timestamp = datetime.now().strftime("%H:%M:%S")
        truncated_query = query[:50] + "..." if len(query) > 50 else query
        
        if success is not None:
            status_icon = "✅" if success else "❌"
            duration_text = f" ({duration_ms}ms)" if duration_ms else ""
            item_text = f"{timestamp} {status_icon} {truncated_query}{duration_text}"
        else:
            item_text = f"{timestamp} 💾 {truncated_query}"
        
        history_item = ListItem(Label(item_text))
        history_item.query = query  # Store full query
        
        # Insert at top
        history_list.insert(0, history_item)
        
        # Keep only last 50 items
        while len(history_list.children) > 50:
            history_list.pop()
    
    @on(ListView.Selected, "#history-list")
    async def on_history_selected(self, event: ListView.Selected) -> None:
        """Load selected query from history."""
        
        if hasattr(event.item, "query"):
            sql_editor = self.query_one("#sql-editor", TextArea)
            sql_editor.text = event.item.query
    
    def _format_sql(self, sql: str) -> str:
        """Basic SQL formatting."""
        
        # Simple SQL formatting - just add line breaks and indentation
        keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN"]
        
        lines = []
        current_line = ""
        
        for word in sql.split():
            upper_word = word.upper()
            
            if any(upper_word.startswith(kw) for kw in keywords):
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line += word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return "\n".join(lines)