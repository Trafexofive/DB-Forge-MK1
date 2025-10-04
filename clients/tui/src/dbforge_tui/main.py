#!/usr/bin/env python3
"""
DB-Forge TUI - Main Entry Point

Command-line interface and application startup.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from textual.app import App

from .app import DBForgeTUI
from .config import Config


@click.command()
@click.option(
    "--url", 
    "-u", 
    default="http://db.localhost",
    help="DB-Forge server URL",
    envvar="DBFORGE_URL"
)
@click.option(
    "--api-key", 
    "-k", 
    help="API key for authentication",
    envvar="DBFORGE_API_KEY"
)
@click.option(
    "--theme", 
    "-t", 
    default="textual-dark",
    help="UI theme (textual-dark, textual-light, monokai, dracula, nord, etc.)",
    envvar="DBFORGE_TUI_THEME"
)
@click.option(
    "--config", 
    "-c", 
    type=click.Path(exists=False, path_type=Path),
    help="Configuration file path"
)
@click.option(
    "--refresh-interval", 
    "-r", 
    default=5,
    type=int,
    help="Auto-refresh interval in seconds"
)
@click.option(
    "--max-rows", 
    default=1000,
    type=int,
    help="Maximum rows to display in tables"
)
@click.option(
    "--vim-mode/--no-vim-mode",
    default=False,
    help="Enable vim-like key bindings"
)
@click.option(
    "--debug", 
    is_flag=True,
    help="Enable debug mode"
)
@click.option(
    "--dev", 
    is_flag=True,
    help="Enable development mode with hot reload"
)
@click.version_option(version="1.0.0", prog_name="DB-Forge TUI")
@click.help_option("--help", "-h")
def main(
    url: str,
    api_key: Optional[str],
    theme: str,
    config: Optional[Path],
    refresh_interval: int,
    max_rows: int,
    vim_mode: bool,
    debug: bool,
    dev: bool,
) -> None:
    """
    🗄️ DB-Forge TUI - Beautiful terminal interface for DB-Forge
    
    A modern, interactive terminal user interface for managing
    Praetorian DB-Forge databases with real-time monitoring,
    SQL editing, and comprehensive database management.
    
    Examples:
    
      # Connect to local DB-Forge instance
      dbforge-tui
      
      # Connect with API key
      dbforge-tui --url http://db.localhost:8080 --api-key my-key
      
      # Use monokai theme with vim bindings  
      dbforge-tui --theme monokai --vim-mode
      
      # Development mode with debugging
      dbforge-tui --dev --debug
    """
    try:
        # Load configuration
        cfg = Config.load(
            config_path=config,
            url=url,
            api_key=api_key,
            theme=theme,
            refresh_interval=refresh_interval,
            max_rows=max_rows,
            vim_mode=vim_mode,
            debug=debug,
            dev_mode=dev,
        )
        
        # Validate configuration
        if not cfg.validate():
            console = Console()
            console.print("[red]❌ Invalid configuration. Please check your settings.[/red]")
            sys.exit(1)
        
        # Create and run the TUI application
        app = DBForgeTUI(cfg)
        
        if dev:
            # Development mode with hot reload
            app.run(debug=True, dev=True)
        else:
            # Normal mode
            app.run(debug=debug)
            
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
        
    except Exception as e:
        console = Console()
        console.print(f"[red]❌ Failed to start DB-Forge TUI: {e}[/red]")
        
        if debug:
            console.print_exception()
            
        sys.exit(1)


def run_app() -> None:
    """Alternative entry point for programmatic usage."""
    main()


if __name__ == "__main__":
    main()