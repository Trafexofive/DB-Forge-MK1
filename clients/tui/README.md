# DB-Forge TUI

A beautiful, modern Terminal User Interface for Praetorian DB-Forge built with Python and Textual.

![DB-Forge TUI](https://raw.githubusercontent.com/praetorian/db-forge-mk1/main/assets/tui-demo.gif)

## ✨ Features

- 🚀 **Fast & Responsive** - Built with Textual for smooth 60fps terminal UI
- 📊 **Interactive Dashboard** - Real-time overview of databases and metrics  
- 🗃️ **Database Manager** - Create, delete, and manage database instances
- 📋 **Table Browser** - Browse table data with sorting and filtering
- ⚡ **Query Editor** - Syntax-highlighted SQL editor with autocomplete
- 📈 **Live Metrics** - Real-time performance monitoring and query analytics
- 🎨 **Multiple Themes** - Dark, light, and custom color schemes
- ⌨️ **Vim-like Keys** - Efficient keyboard navigation
- 🔍 **Search & Filter** - Quick search across databases and tables
- 📱 **Responsive Layout** - Adapts to any terminal size

## 🏗️ Architecture

```
┌─ Dashboard ─────────────────────────────────────────────────┐
│  ┌─ Database List ─┐  ┌─ Metrics ──────┐  ┌─ Activity ──┐  │
│  │ ● user_db      │  │ 📊 Queries: 1.2K│  │ 14:23 SELECT│  │
│  │ ● analytics_db │  │ ⚡ Avg: 45ms   │  │ 14:22 INSERT│  │
│  │ ● session_db   │  │ 💾 Memory: 45MB │  │ 14:21 CREATE│  │
│  └────────────────┘  └────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
│
├─ Query Editor ──────────────────────────────────────────────┐
│  ┌─ SQL Editor ────────────────────┐  ┌─ Results ────────┐  │
│  │ SELECT u.username,             │  │ │username│email  ││  │
│  │        u.email,                │  │ ├────────┼──────┤│  │
│  │        COUNT(s.id) as sessions │  │ │alice   │a@x.co││  │
│  │ FROM users u                   │  │ │bob     │b@x.co││  │
│  │ WHERE u.active = 1█            │  │ └────────┴──────┘│  │
│  └────────────────────────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Installation

### From PyPI (coming soon)
```bash
pip install dbforge-tui
```

### From Source
```bash
git clone https://github.com/praetorian/db-forge-mk1.git
cd db-forge-mk1/clients/tui
pip install -e .
```

### With Development Dependencies
```bash
pip install -e ".[dev]"
```

## 💻 Usage

### Basic Usage
```bash
# Start TUI with default settings
dbforge-tui

# Connect to specific DB-Forge instance  
dbforge-tui --url http://db.localhost:8080

# With API key authentication
dbforge-tui --url http://db.localhost:8080 --api-key your-key

# Use specific theme
dbforge-tui --theme monokai

# Help
dbforge-tui --help
```

### Configuration File
Create `~/.dbforge-tui.toml`:

```toml
[server]
url = "http://db.localhost:8080"
api_key = "your-api-key"
timeout = 30

[ui]
theme = "monokai"
refresh_interval = 5
max_rows = 1000
vim_mode = true

[editor]  
tab_size = 4
auto_complete = true
syntax_highlight = true
word_wrap = false

[performance]
query_timeout = 30
slow_query_threshold = 1000
enable_metrics = true
```

## ⌨️ Keyboard Shortcuts

### Global Navigation
- **Ctrl+Q** - Quit application
- **F1** - Help screen  
- **Ctrl+R** - Refresh current view
- **/** - Search/Filter
- **Tab** - Cycle through panels
- **Esc** - Go back/Cancel

### Dashboard
- **Enter** - Open selected database
- **n** - Create new database  
- **d** - Delete selected database
- **r** - Restart database container

### Query Editor  
- **F5** - Execute query
- **Ctrl+S** - Save query
- **Ctrl+F** - Format SQL
- **Ctrl+L** - Clear editor
- **Ctrl+Z** - Undo
- **Ctrl+Y** - Redo

### Table Browser
- **↑/↓** - Navigate rows
- **←/→** - Navigate columns  
- **Page Up/Down** - Scroll pages
- **Home/End** - First/Last row
- **f** - Toggle filter
- **s** - Sort options

## 🎨 Themes

Built-in themes:
- **textual-dark** - Default dark theme
- **textual-light** - Clean light theme
- **monokai** - Monokai color scheme
- **dracula** - Dracula theme
- **nord** - Nord theme
- **solarized-dark** - Solarized dark
- **gruvbox** - Gruvbox theme

Switch themes:
```bash
dbforge-tui --theme monokai
```

Or in the settings (press `s`).

## 🔧 Features Deep Dive

### Interactive Dashboard
```python
# Real-time metrics
- Database count and status
- Memory usage across all databases  
- Query performance analytics
- Recent query activity log
- Connection health monitoring
```

### Advanced Query Editor
```python
# Features
- SQL syntax highlighting
- Auto-completion for tables/columns
- Query history with search
- Result pagination
- Export results (CSV, JSON)
- Query performance analysis
- Error highlighting with suggestions
```

### Smart Table Browser
```python
# Capabilities  
- Paginated data browsing
- Column sorting (click headers)
- Row filtering with conditions
- Cell value search
- Foreign key navigation
- Schema information display
```

### Performance Monitoring
```python
# Metrics tracked
- Query execution time
- Memory usage per database
- Connection count  
- Slow query identification
- Query frequency analysis
- Error rate monitoring
```

## 📊 Screenshots

### Main Dashboard
```
┌─ DB-Forge TUI ─────────────────────────────────────────────────────────┐
│                                                                         │
│ 🟢 CONNECTED  │  🗄️ 3 databases  │  💾 45.2MB  │  ⚡ 1,247 queries      │
│                                                                         │
├─ Databases ──────────────────┬─ Performance ──────────────────────────┤
│                              │                                        │
│ ● user_db        [RUNNING]   │     Query Response Time (ms)          │
│ ● analytics_db   [RUNNING]   │  60 ┤                                 │
│ ● session_db     [RUNNING]   │  50 ┤     █                           │
│                              │  40 ┤   ███                           │
│ [↑↓] Navigate [Enter] Open   │  30 ┤ █████                           │
│ [n] New [d] Delete           │  20 ┤███████ █                        │
│                              │  10 ┤████████████                     │
├─ Recent Activity ────────────┴─────────────────────────────────────────┤
│                                                                         │
│ 14:23:45  ✅ SELECT * FROM users WHERE active=1        [47ms] 3 rows   │
│ 14:23:42  ✅ INSERT INTO analytics VALUES (...)         [12ms] 1 row    │
│ 14:23:40  ✅ CREATE TABLE sessions (id, data)          [8ms]           │
│ 14:23:38  ❌ SELECT * FROM nonexistent                 [5ms] ERROR     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ F1 Help │ / Search │ Ctrl+R Refresh │ s Settings │ Ctrl+Q Quit          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Query Editor
```
┌─ Query Editor: user_db ────────────────────────────────────────────────┐
│                                                                         │
│ ┌─ SQL ──────────────────────────────┐ ┌─ Results ─────────────────────┐ │
│ │ SELECT u.username,                 │ │ ┌─────────┬─────────────────┐ │ │
│ │        u.email,                    │ │ │username │ email           │ │ │
│ │        COUNT(s.id) as sessions     │ │ ├─────────┼─────────────────┤ │ │
│ │ FROM users u                       │ │ │ alice   │ alice@example   │ │ │
│ │ LEFT JOIN sessions s ON u.id=s.uid │ │ │ bob     │ bob@example     │ │ │
│ │ WHERE u.active = 1                 │ │ │ charlie │ charlie@example │ │ │
│ │ GROUP BY u.id                      │ │ └─────────┴─────────────────┘ │ │
│ │ ORDER BY sessions DESC;█           │ │                               │ │
│ └────────────────────────────────────┘ │ 📊 3 rows in 23ms           │ │
│                                        └───────────────────────────────┘ │
│ ┌─ History ─────────────────┐ ┌─ Schema ──────────────────────────────┐ │
│ │ SELECT * FROM users       │ │ 📋 users                              │ │
│ │ SHOW TABLES              │ │ ├─ id (INTEGER PRIMARY KEY)            │ │
│ │ SELECT COUNT(*) FROM...   │ │ ├─ username (TEXT NOT NULL)           │ │
│ └───────────────────────────┘ │ ├─ email (TEXT NOT NULL)              │ │
│                               │ └─ active (BOOLEAN DEFAULT 1)          │ │
│                               └───────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ F5 Execute │ Ctrl+S Save │ Ctrl+F Format │ / Search │ Esc Back           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🐍 Development

### Setup Development Environment
```bash
git clone https://github.com/praetorian/db-forge-mk1.git
cd db-forge-mk1/clients/tui

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running in Development Mode  
```bash
# Run with hot reload
textual run --dev src/dbforge_tui/main.py

# Run with debugging
textual console &
python -m dbforge_tui.main --debug

# Run tests
pytest tests/

# Code formatting
black src/ tests/
isort src/ tests/

# Type checking  
mypy src/
```

### Project Structure
```
src/dbforge_tui/
├── __init__.py
├── main.py              # Entry point and CLI
├── app.py               # Main TUI application  
├── config.py            # Configuration management
├── api/
│   ├── __init__.py
│   └── client.py        # DB-Forge API client
├── widgets/
│   ├── __init__.py
│   ├── dashboard.py     # Dashboard view
│   ├── database_manager.py
│   ├── query_editor.py  
│   ├── table_browser.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   ├── formatting.py    # Data formatting utilities
│   └── sql_parser.py    # SQL parsing and highlighting
└── themes/
    ├── __init__.py
    └── themes.py        # Custom theme definitions
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/awesome-feature`
3. Install development dependencies: `pip install -e ".[dev]"`  
4. Make your changes
5. Add tests: `pytest tests/`
6. Format code: `black . && isort .`
7. Type check: `mypy src/`
8. Commit: `git commit -m 'Add awesome feature'`
9. Push: `git push origin feature/awesome-feature`
10. Create Pull Request

## 📄 License

MIT License - see [LICENSE](../../LICENSE) for details.

## 🔗 Related Projects

- [DB-Forge Main](../../README.md) - Core DB-Forge server
- [Python Client](../python/) - Python API client
- [C++ Client](../cpp/) - C++ API client