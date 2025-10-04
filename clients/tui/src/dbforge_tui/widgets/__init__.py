"""UI widgets package for DB-Forge TUI."""

from .dashboard import DashboardWidget
from .query_editor import QueryEditorWidget
from .database_manager import DatabaseManagerWidget
from .table_browser import TableBrowserWidget

__all__ = [
    "DashboardWidget",
    "QueryEditorWidget", 
    "DatabaseManagerWidget",
    "TableBrowserWidget",
]