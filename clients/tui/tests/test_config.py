"""
Tests for configuration management
"""

import pytest
from pathlib import Path
import tempfile
import os

from dbforge_tui.config import Config, ServerConfig, UIConfig, EditorConfig, PerformanceConfig


def test_default_config():
    """Test default configuration values."""
    
    config = Config()
    
    # Check server defaults
    assert config.server.url == "http://db.localhost"
    assert config.server.api_key is None
    assert config.server.timeout == 30
    assert config.server.retries == 3
    
    # Check UI defaults
    assert config.ui.theme == "textual-dark"
    assert config.ui.refresh_interval == 5
    assert config.ui.max_rows == 1000
    assert config.ui.vim_mode is False
    
    # Check editor defaults
    assert config.editor.tab_size == 4
    assert config.editor.auto_complete is True
    assert config.editor.syntax_highlight is True
    
    # Check performance defaults
    assert config.performance.query_timeout == 30
    assert config.performance.slow_query_threshold == 1000
    assert config.performance.enable_metrics is True


def test_config_validation():
    """Test configuration validation."""
    
    # Valid configuration
    config = Config()
    assert config.validate() is True
    
    # Invalid URL
    config.server.url = "not-a-url"
    assert config.validate() is False
    
    # Invalid refresh interval
    config.server.url = "http://localhost"
    config.ui.refresh_interval = -1
    assert config.validate() is False
    
    # Valid again
    config.ui.refresh_interval = 5
    assert config.validate() is True


def test_config_from_overrides():
    """Test configuration creation with overrides."""
    
    config = Config.load(
        url="http://custom.localhost",
        api_key="test-key",
        theme="monokai",
        refresh_interval=10,
        vim_mode=True,
        debug=True
    )
    
    assert config.server.url == "http://custom.localhost"
    assert config.server.api_key == "test-key"
    assert config.ui.theme == "monokai"
    assert config.ui.refresh_interval == 10
    assert config.ui.vim_mode is True
    assert config.debug is True


def test_config_from_env():
    """Test configuration from environment variables."""
    
    # Set environment variables
    os.environ["DBFORGE_URL"] = "http://env.localhost"
    os.environ["DBFORGE_API_KEY"] = "env-key"
    os.environ["DBFORGE_TUI_THEME"] = "dark"
    os.environ["DBFORGE_TUI_REFRESH"] = "15"
    
    try:
        config = Config.load()
        
        assert config.server.url == "http://env.localhost"
        assert config.server.api_key == "env-key"
        assert config.ui.theme == "dark"
        assert config.ui.refresh_interval == 15
        
    finally:
        # Clean up environment
        for key in ["DBFORGE_URL", "DBFORGE_API_KEY", "DBFORGE_TUI_THEME", "DBFORGE_TUI_REFRESH"]:
            os.environ.pop(key, None)


def test_config_save_load():
    """Test saving and loading configuration."""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        config_path = Path(f.name)
    
    try:
        # Create config with custom values
        config = Config()
        config.server.url = "http://test.localhost"
        config.server.api_key = "test-key"
        config.ui.theme = "custom"
        config.ui.vim_mode = True
        
        # Save config
        assert config.save(config_path) is True
        assert config_path.exists()
        
        # Load config
        loaded_config = Config.load(config_path=config_path)
        
        assert loaded_config.server.url == "http://test.localhost"
        assert loaded_config.server.api_key == "test-key"
        assert loaded_config.ui.theme == "custom"
        assert loaded_config.ui.vim_mode is True
        
    finally:
        # Cleanup
        if config_path.exists():
            config_path.unlink()


def test_config_file_precedence():
    """Test configuration precedence: CLI > env > file > defaults."""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        config_path = Path(f.name)
        
        # Write config file
        f.write('''
[server]
url = "http://file.localhost"
api_key = "file-key"

[ui]
theme = "file-theme"
refresh_interval = 20
''')
    
    try:
        # Set environment variable
        os.environ["DBFORGE_URL"] = "http://env.localhost"
        
        # Load with CLI override
        config = Config.load(
            config_path=config_path,
            url="http://cli.localhost",
            theme="cli-theme"
        )
        
        # CLI should override env and file
        assert config.server.url == "http://cli.localhost"
        
        # CLI override should win for theme
        assert config.ui.theme == "cli-theme"
        
        # File value should be used where no env/CLI override
        assert config.server.api_key == "file-key"
        assert config.ui.refresh_interval == 20
        
    finally:
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        os.environ.pop("DBFORGE_URL", None)


if __name__ == "__main__":
    pytest.main([__file__])