# DB-Forge Client Libraries

This directory contains client libraries for Praetorian DB-Forge in multiple programming languages, designed to make integration with your applications as easy as possible.

## Available Clients

### 🐍 Python Client (`python/`)

A comprehensive Python client library with both synchronous and asynchronous support.

**Features:**
- Simple, intuitive API design
- Full type hints for better IDE support
- Async/await support with `AsyncDBForgeClient`
- Comprehensive error handling
- Command-line interface
- pip installable package

**Quick Start:**
```bash
cd python
pip install -e .

# Basic usage
python examples/basic_usage.py

# Async usage  
python examples/async_usage.py

# CLI usage
dbforge spawn my-db
dbforge query my-db "SELECT 1"
```

### 🔧 C++ Client (`cpp/`)

A modern C++17 client library with RAII and exception safety.

**Features:**
- Modern C++17 design
- Exception-safe RAII patterns
- Thread-safe for concurrent operations
- CMake integration support
- Cross-platform (Linux, macOS, Windows)
- Comprehensive examples and tests

**Quick Start:**
```bash
cd cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Run examples
./examples/basic_example
./examples/advanced_example

# Run tests
make test
```

## Common Features

Both client libraries provide:

✅ **Complete API Coverage** - All DB-Forge endpoints supported  
✅ **Admin Operations** - Spawn, prune, and list databases  
✅ **Database Operations** - Create tables, insert/select/update/delete data  
✅ **Raw SQL Support** - Execute arbitrary SQL queries  
✅ **Error Handling** - Comprehensive exception handling with detailed error info  
✅ **Configuration** - Environment variable support for easy deployment  
✅ **Documentation** - Extensive examples and API documentation  
✅ **Testing** - Unit and integration tests included  

## Getting Started

1. **Start DB-Forge Server**
   ```bash
   # From the project root
   make up
   ```

2. **Choose Your Language**
   - For Python: `cd python && pip install -e .`  
   - For C++: `cd cpp && mkdir build && cd build && cmake .. && make`

3. **Run Examples**
   - Python: `python examples/basic_usage.py`
   - C++: `./examples/basic_example`

4. **Integration**
   - Python: `from dbforge_client import DBForgeClient`
   - C++: `#include <dbforge/dbforge.hpp>`

## Configuration

Both clients support configuration via environment variables:

```bash
export DBFORGE_BASE_URL="http://db.localhost"
export DBFORGE_API_KEY="your-api-key"      # Optional
export DBFORGE_TIMEOUT="30"                # Timeout in seconds
```

## API Examples

### Basic Database Operations

**Python:**
```python
from dbforge_client import DBForgeClient

client = DBForgeClient()
client.spawn_database("my-app")

db = client.get_database("my-app")
db.create_table("users", [
    {"name": "id", "type": "INTEGER", "primary_key": True},
    {"name": "username", "type": "TEXT", "not_null": True}
])

db.insert_rows("users", [{"username": "alice"}])
users = db.select_rows("users", {"username": "alice"})
```

**C++:**
```cpp
#include <dbforge/dbforge.hpp>

dbforge::Client client;
client.spawn_database("my-app");

auto db = client.get_database("my-app");
db.create_table("users", {
    {"id", "INTEGER", true, false},      // primary_key, not_null
    {"username", "TEXT", false, true}    // not primary, but not_null
});

db.insert_rows("users", {{{"username", "alice"}}});
auto users = db.select_rows("users", {{"username", "alice"}});
```

### Raw SQL Queries

**Python:**
```python
result = db.execute_query(
    "SELECT COUNT(*) as count FROM users WHERE created_at > ?",
    ["2023-01-01"]
)
print(f"Count: {result['data'][0]['count']}")
```

**C++:**
```cpp
auto result = db.execute_query(
    "SELECT COUNT(*) as count FROM users WHERE created_at > ?",
    {"2023-01-01"}
);
std::cout << "Count: " << result.data[0].at("count") << std::endl;
```

## Error Handling

**Python:**
```python
from dbforge_client import DBForgeClient, DatabaseNotFound, DBForgeError

try:
    client = DBForgeClient()
    client.prune_database("nonexistent")
except DatabaseNotFound as e:
    print(f"Database not found: {e}")
except DBForgeError as e:
    print(f"Error {e.status_code}: {e}")
```

**C++:**
```cpp
#include <dbforge/exceptions.hpp>

try {
    dbforge::Client client;
    client.prune_database("nonexistent");
} catch (const dbforge::DatabaseNotFound& e) {
    std::cerr << "Database not found: " << e.what() << std::endl;
} catch (const dbforge::Exception& e) {
    std::cerr << "Error " << e.status_code() << ": " << e.what() << std::endl;
}
```

## Contributing

1. **Adding Features**: Implement in both Python and C++ clients for consistency
2. **Testing**: Add unit tests and integration tests 
3. **Documentation**: Update README and code examples
4. **Code Style**: Follow language-specific conventions (PEP 8 for Python, Google Style for C++)

## Performance Notes

- **Python**: Use `AsyncDBForgeClient` for high-concurrency scenarios
- **C++**: Thread-safe for different database instances, use connection pooling for high load
- **Both**: Batch operations when possible (e.g., `insert_rows` with multiple rows)

## Troubleshooting

### Connection Issues
```bash
# Check if DB-Forge server is running
curl http://db.localhost/

# Check environment variables
echo $DBFORGE_BASE_URL
```

### Build Issues (C++)
```bash
# Install dependencies on Ubuntu/Debian
sudo apt-get install libcurl4-openssl-dev libjsoncpp-dev

# Install dependencies on macOS
brew install curl jsoncpp
```

### Import Issues (Python)
```bash
# Install in development mode
pip install -e .

# Check installation
python -c "import dbforge_client; print('OK')"
```

## License

MIT License - see individual client directories for detailed license information.

---

For language-specific documentation, see:
- [Python Client Documentation](python/README.md)
- [C++ Client Documentation](cpp/README.md)