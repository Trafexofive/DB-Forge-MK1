"""
Configuration management for DB-Forge TUI
"""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

from rich.console import Console


@dataclass
class ServerConfig:
    """Server connection configuration."""
    url: str = "http://db.localhost"
    api_key: Optional[str] = None
    timeout: int = 30
    retries: int = 3


@dataclass  
class UIConfig:
    """UI appearance and behavior configuration."""
    theme: str = "textual-dark"
    refresh_interval: int = 5
    max_rows: int = 1000
    vim_mode: bool = False
    show_line_numbers: bool = True
    word_wrap: bool = False


@dataclass
class EditorConfig:
    """Query editor configuration."""
    tab_size: int = 4
    auto_complete: bool = True
    syntax_highlight: bool = True
    auto_format: bool = False
    save_history: bool = True
    history_limit: int = 100


@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration."""
    query_timeout: int = 30
    slow_query_threshold: int = 1000  # milliseconds
    enable_metrics: bool = True
    max_result_rows: int = 10000
    cache_schemas: bool = True


@dataclass
class Config:
    """Main configuration class."""
    
    server: ServerConfig = field(default_factory=ServerConfig)
    ui: UIConfig = field(default_factory=UIConfig) 
    editor: EditorConfig = field(default_factory=EditorConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Runtime options
    debug: bool = False
    dev_mode: bool = False
    
    @classmethod
    def load(
        cls,
        config_path: Optional[Path] = None,
        **overrides
    ) -> "Config":
        """Load configuration from file and apply overrides."""
        
        # Start with defaults
        config = cls()
        
        # Try to load from config file
        if config_path is None:
            # Look for config in standard locations
            config_path = cls._find_config_file()
        
        if config_path and config_path.exists():
            try:
                config._load_from_file(config_path)
            except Exception as e:
                console = Console()
                console.print(f"[yellow]Warning: Could not load config from {config_path}: {e}[/yellow]")
        
        # Apply environment variables
        config._load_from_env()
        
        # Apply CLI overrides
        config._apply_overrides(overrides)
        
        return config
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """Find configuration file in standard locations."""
        locations = [
            Path.cwd() / ".dbforge-tui.toml",
            Path.home() / ".dbforge-tui.toml",
            Path.home() / ".config" / "dbforge-tui" / "config.toml",
        ]
        
        for path in locations:
            if path.exists():
                return path
        
        return None
    
    def _load_from_file(self, config_path: Path) -> None:
        """Load configuration from TOML file."""
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        
        # Update server config
        if "server" in data:
            server_data = data["server"]
            self.server.url = server_data.get("url", self.server.url)
            self.server.api_key = server_data.get("api_key", self.server.api_key)
            self.server.timeout = server_data.get("timeout", self.server.timeout)
            self.server.retries = server_data.get("retries", self.server.retries)
        
        # Update UI config  
        if "ui" in data:
            ui_data = data["ui"]
            self.ui.theme = ui_data.get("theme", self.ui.theme)
            self.ui.refresh_interval = ui_data.get("refresh_interval", self.ui.refresh_interval)
            self.ui.max_rows = ui_data.get("max_rows", self.ui.max_rows)
            self.ui.vim_mode = ui_data.get("vim_mode", self.ui.vim_mode)
            self.ui.show_line_numbers = ui_data.get("show_line_numbers", self.ui.show_line_numbers)
            self.ui.word_wrap = ui_data.get("word_wrap", self.ui.word_wrap)
        
        # Update editor config
        if "editor" in data:
            editor_data = data["editor"]
            self.editor.tab_size = editor_data.get("tab_size", self.editor.tab_size)
            self.editor.auto_complete = editor_data.get("auto_complete", self.editor.auto_complete)
            self.editor.syntax_highlight = editor_data.get("syntax_highlight", self.editor.syntax_highlight)
            self.editor.auto_format = editor_data.get("auto_format", self.editor.auto_format)
            self.editor.save_history = editor_data.get("save_history", self.editor.save_history)
            self.editor.history_limit = editor_data.get("history_limit", self.editor.history_limit)
        
        # Update performance config
        if "performance" in data:
            perf_data = data["performance"]
            self.performance.query_timeout = perf_data.get("query_timeout", self.performance.query_timeout)
            self.performance.slow_query_threshold = perf_data.get("slow_query_threshold", self.performance.slow_query_threshold)
            self.performance.enable_metrics = perf_data.get("enable_metrics", self.performance.enable_metrics)
            self.performance.max_result_rows = perf_data.get("max_result_rows", self.performance.max_result_rows)
            self.performance.cache_schemas = perf_data.get("cache_schemas", self.performance.cache_schemas)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        
        # Server config from env
        if os.getenv("DBFORGE_URL"):
            self.server.url = os.getenv("DBFORGE_URL")
        if os.getenv("DBFORGE_API_KEY"):
            self.server.api_key = os.getenv("DBFORGE_API_KEY")
        if os.getenv("DBFORGE_TIMEOUT"):
            try:
                self.server.timeout = int(os.getenv("DBFORGE_TIMEOUT"))
            except ValueError:
                pass
        
        # UI config from env
        if os.getenv("DBFORGE_TUI_THEME"):
            self.ui.theme = os.getenv("DBFORGE_TUI_THEME")
        if os.getenv("DBFORGE_TUI_REFRESH"):
            try:
                self.ui.refresh_interval = int(os.getenv("DBFORGE_TUI_REFRESH"))
            except ValueError:
                pass
        if os.getenv("DBFORGE_TUI_VIM_MODE"):
            self.ui.vim_mode = os.getenv("DBFORGE_TUI_VIM_MODE").lower() in ("true", "1", "yes")
    
    def _apply_overrides(self, overrides: Dict[str, any]) -> None:
        """Apply CLI overrides to configuration."""
        
        # Server overrides
        if "url" in overrides and overrides["url"]:
            self.server.url = overrides["url"]
        if "api_key" in overrides and overrides["api_key"]:
            self.server.api_key = overrides["api_key"]
        
        # UI overrides
        if "theme" in overrides and overrides["theme"]:
            self.ui.theme = overrides["theme"]
        if "refresh_interval" in overrides and overrides["refresh_interval"]:
            self.ui.refresh_interval = overrides["refresh_interval"]
        if "max_rows" in overrides and overrides["max_rows"]:
            self.ui.max_rows = overrides["max_rows"]
        if "vim_mode" in overrides:
            self.ui.vim_mode = overrides["vim_mode"]
        
        # Runtime overrides
        if "debug" in overrides:
            self.debug = overrides["debug"]
        if "dev_mode" in overrides:
            self.dev_mode = overrides["dev_mode"]
    
    def validate(self) -> bool:
        """Validate configuration values."""
        try:
            # Validate server URL
            parsed = urlparse(self.server.url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Validate numeric values
            if self.server.timeout <= 0:
                return False
            if self.ui.refresh_interval <= 0:
                return False
            if self.ui.max_rows <= 0:
                return False
            if self.editor.tab_size <= 0:
                return False
            if self.performance.query_timeout <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def save(self, config_path: Optional[Path] = None) -> bool:
        """Save configuration to file."""
        if config_path is None:
            config_path = Path.home() / ".dbforge-tui.toml"
        
        try:
            # Convert to TOML format
            data = {
                "server": {
                    "url": self.server.url,
                    "api_key": self.server.api_key,
                    "timeout": self.server.timeout,
                    "retries": self.server.retries,
                },
                "ui": {
                    "theme": self.ui.theme,
                    "refresh_interval": self.ui.refresh_interval,
                    "max_rows": self.ui.max_rows,
                    "vim_mode": self.ui.vim_mode,
                    "show_line_numbers": self.ui.show_line_numbers,
                    "word_wrap": self.ui.word_wrap,
                },
                "editor": {
                    "tab_size": self.editor.tab_size,
                    "auto_complete": self.editor.auto_complete,
                    "syntax_highlight": self.editor.syntax_highlight,
                    "auto_format": self.editor.auto_format,
                    "save_history": self.editor.save_history,
                    "history_limit": self.editor.history_limit,
                },
                "performance": {
                    "query_timeout": self.performance.query_timeout,
                    "slow_query_threshold": self.performance.slow_query_threshold,
                    "enable_metrics": self.performance.enable_metrics,
                    "max_result_rows": self.performance.max_result_rows,
                    "cache_schemas": self.performance.cache_schemas,
                }
            }
            
            # Write TOML file (basic implementation)
            with open(config_path, "w") as f:
                for section, values in data.items():
                    f.write(f"[{section}]\n")
                    for key, value in values.items():
                        if isinstance(value, str):
                            f.write(f'{key} = "{value}"\n')
                        elif isinstance(value, bool):
                            f.write(f'{key} = {str(value).lower()}\n')
                        else:
                            f.write(f'{key} = {value}\n')
                    f.write("\n")
            
            return True
            
        except Exception:
            return False


# Available themes
THEMES = {
    "textual-dark": "Default dark theme",
    "textual-light": "Clean light theme", 
    "monokai": "Monokai color scheme",
    "dracula": "Dracula theme",
    "nord": "Nord theme",
    "solarized-dark": "Solarized dark",
    "solarized-light": "Solarized light", 
    "gruvbox": "Gruvbox theme",
    "one-dark": "One Dark theme",
    "material": "Material Design theme",
}