# DB-Forge C++ Client

A modern C++17 client library for Praetorian DB-Forge that provides an easy-to-use interface for database operations.

## Features

- **Modern C++17**: Clean, type-safe API with RAII and smart pointers
- **Exception Safety**: Comprehensive error handling with custom exception types  
- **Easy Integration**: Single header include with CMake support
- **Cross Platform**: Works on Linux, macOS, and Windows
- **HTTP Client**: Built-in HTTP client using libcurl
- **JSON Support**: Seamless JSON integration using jsoncpp
- **Thread Safe**: Can be used safely from multiple threads

## Dependencies

- **C++17** compiler (GCC 7+, Clang 5+, MSVC 2017+)
- **libcurl** - HTTP client library
- **jsoncpp** - JSON parsing and generation
- **CMake 3.15+** - Build system

## Installation

### Ubuntu/Debian

```bash
sudo apt-get install build-essential cmake libcurl4-openssl-dev libjsoncpp-dev
```

### CentOS/RHEL/Fedora

```bash
sudo yum install gcc-c++ cmake libcurl-devel jsoncpp-devel
# or for newer versions:
sudo dnf install gcc-c++ cmake libcurl-devel jsoncpp-devel
```

### macOS

```bash
brew install cmake curl jsoncpp
```

### Build and Install

```bash
git clone <repository>
cd clients/cpp
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

## Quick Start

```cpp
#include <dbforge/client.hpp>
#include <iostream>

int main() {
    try {
        // Initialize client
        dbforge::Client client("http://db.localhost", "your-api-key");
        
        // Spawn database
        auto spawn_result = client.spawn_database("my_app_db");
        std::cout << "Database spawned: " << spawn_result.database_name << std::endl;
        
        // Get database instance
        auto db = client.get_database("my_app_db");
        
        // Create table
        std::vector<dbforge::Column> columns = {
            {"id", "INTEGER", true, false},      // primary_key, not_null
            {"username", "TEXT", false, true},   // not primary, but not_null
            {"email", "TEXT", false, true},
            {"created_at", "DATETIME", false, false, "CURRENT_TIMESTAMP"}
        };
        db.create_table("users", columns);
        
        // Insert data
        std::vector<dbforge::Row> users = {
            {{"username", "alice"}, {"email", "alice@example.com"}},
            {{"username", "bob"}, {"email", "bob@example.com"}}
        };
        auto insert_result = db.insert_rows("users", users);
        std::cout << "Inserted " << insert_result.rows_affected << " rows" << std::endl;
        
        // Query data
        auto query_result = db.execute_query("SELECT * FROM users WHERE username = ?", {"alice"});
        for (const auto& row : query_result.data) {
            std::cout << "User: " << row.at("username") << " (" << row.at("email") << ")" << std::endl;
        }
        
        // Select with filters
        auto filtered_users = db.select_rows("users", {{"username", "alice"}});
        std::cout << "Found " << filtered_users.size() << " users named Alice" << std::endl;
        
        // Cleanup
        client.prune_database("my_app_db");
        
    } catch (const dbforge::Exception& e) {
        std::cerr << "DB-Forge error: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
```

## CMake Integration

Add to your `CMakeLists.txt`:

```cmake
find_package(DBForgeClient REQUIRED)
target_link_libraries(your_target DBForge::dbforge_client)
```

Or use FetchContent:

```cmake
include(FetchContent)
FetchContent_Declare(
  DBForgeClient
  GIT_REPOSITORY https://github.com/praetorian/db-forge-mk1.git
  GIT_TAG        main
  SOURCE_SUBDIR  clients/cpp
)
FetchContent_MakeAvailable(DBForgeClient)
target_link_libraries(your_target dbforge_client)
```

## API Reference

### Client Class

```cpp
namespace dbforge {
    class Client {
    public:
        Client(const std::string& base_url, const std::string& api_key = "");
        
        // Admin operations
        SpawnResult spawn_database(const std::string& name);
        PruneResult prune_database(const std::string& name);
        std::vector<DatabaseInfo> list_databases();
        
        // Get database instance
        Database get_database(const std::string& name);
        
        // Health check
        HealthResult health_check();
    };
}
```

### Database Class

```cpp
namespace dbforge {
    class Database {
    public:
        // Table operations
        CreateTableResult create_table(const std::string& name, 
                                     const std::vector<Column>& columns);
        
        InsertResult insert_rows(const std::string& table, 
                               const std::vector<Row>& rows);
        
        std::vector<Row> select_rows(const std::string& table, 
                                   const Row& filters = {});
        
        // Query operations  
        QueryResult execute_query(const std::string& sql, 
                                const std::vector<std::string>& params = {});
        
        // Utility operations
        std::vector<std::string> list_tables();
        std::vector<ColumnInfo> get_table_schema(const std::string& table);
        DropResult drop_table(const std::string& table);
    };
}
```

### Data Types

```cpp
namespace dbforge {
    // Column definition
    struct Column {
        std::string name;
        std::string type;
        bool primary_key = false;
        bool not_null = false;
        std::string default_value = "";
        bool unique = false;
    };
    
    // Row data (key-value pairs)
    using Row = std::map<std::string, std::string>;
    
    // Query results
    struct QueryResult {
        std::vector<Row> data;
        int rows_affected;
        std::string message;
    };
    
    // Database info
    struct DatabaseInfo {
        std::string name;
        std::string container_id;
        std::string status;
    };
}
```

## Error Handling

```cpp
#include <dbforge/exceptions.hpp>

try {
    // DB-Forge operations
} catch (const dbforge::DatabaseNotFound& e) {
    // Handle database not found
} catch (const dbforge::InvalidRequest& e) {
    // Handle bad request (400)  
} catch (const dbforge::AuthenticationError& e) {
    // Handle auth errors (401)
} catch (const dbforge::ServerError& e) {
    // Handle server errors (5xx)
} catch (const dbforge::Exception& e) {
    // Handle other DB-Forge errors
    std::cerr << "Error: " << e.what() << std::endl;
    std::cerr << "Status: " << e.status_code() << std::endl;
    std::cerr << "Code: " << e.error_code() << std::endl;
}
```

## Configuration

### Environment Variables

- `DBFORGE_BASE_URL`: Default base URL
- `DBFORGE_API_KEY`: Default API key  
- `DBFORGE_TIMEOUT`: Request timeout in seconds

### Client Configuration

```cpp
dbforge::Client client(
    "http://db.localhost",  // base_url
    "your-api-key",         // api_key (optional)
    30                      // timeout_seconds (optional)
);
```

## Thread Safety

The client is thread-safe for concurrent operations on different database instances. However, individual `Database` objects should not be shared between threads without proper synchronization.

```cpp
// Safe: Different databases
std::thread t1([&]() { client.get_database("db1").execute_query("SELECT 1"); });
std::thread t2([&]() { client.get_database("db2").execute_query("SELECT 1"); });

// Unsafe: Same database instance without synchronization
auto db = client.get_database("shared_db");
std::thread t3([&]() { db.execute_query("SELECT 1"); });  // Race condition!
std::thread t4([&]() { db.execute_query("SELECT 2"); });  // Race condition!
```

## Building Examples

```bash
cd build
make examples
./examples/basic_example
./examples/advanced_example
```

## Building Tests

```bash
cd build
make tests
ctest --verbose
```

## License

MIT License - see LICENSE file for details.