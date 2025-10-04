"""
DB-Forge TUI - Terminal User Interface for DB-Forge

A beautiful, interactive terminal interface for Praetorian DB-Forge 
built with Python and Textual.
"""

__version__ = "1.0.0"
__author__ = "Praetorian DB-Forge Team"
__email__ = "contact@dbforge.dev"

from .app import DBForgeTUI
from .config import Config

__all__ = ["DBForgeTUI", "Config"]