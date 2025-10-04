#!/usr/bin/env python3
"""
Basic usage example for DB-Forge TUI
"""

import asyncio
from dbforge_tui.config import Config
from dbforge_tui.app import DBForgeTUI


async def main():
    """Run the TUI with example configuration."""
    
    # Create configuration
    config = Config.load(
        url="http://db.localhost",
        theme="textual-dark",
        refresh_interval=5,
        vim_mode=False,
        debug=True
    )
    
    # Validate configuration
    if not config.validate():
        print("❌ Invalid configuration")
        return 1
    
    print("🚀 Starting DB-Forge TUI...")
    print(f"📡 Connecting to: {config.server.url}")
    print(f"🎨 Theme: {config.ui.theme}")
    print(f"🔄 Refresh interval: {config.ui.refresh_interval}s")
    print()
    
    # Create and run TUI application
    app = DBForgeTUI(config)
    
    try:
        await app.run_async(debug=config.debug)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)