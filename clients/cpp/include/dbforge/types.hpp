#pragma once

#include <string>
#include <vector>
#include <map>

namespace dbforge {

// Type aliases
using Row = std::map<std::string, std::string>;
using Params = std::vector<std::string>;

/**
 * Column definition for table creation.
 */
struct Column {
    std::string name;
    std::string type;
    bool primary_key = false;
    bool not_null = false;
    std::string default_value = "";
    bool unique = false;

    Column(const std::string& name, const std::string& type)
        : name(name), type(type) {}
    
    Column(const std::string& name, const std::string& type, bool primary_key, bool not_null)
        : name(name), type(type), primary_key(primary_key), not_null(not_null) {}
    
    Column(const std::string& name, const std::string& type, bool primary_key, bool not_null, const std::string& default_value)
        : name(name), type(type), primary_key(primary_key), not_null(not_null), default_value(default_value) {}
};

/**
 * Result of spawning a database.
 */
struct SpawnResult {
    std::string message;
    std::string database_name;
    std::string container_id;
};

/**
 * Result of pruning a database.
 */
struct PruneResult {
    std::string message;
    std::string database_name;
};

/**
 * Database information.
 */
struct DatabaseInfo {
    std::string name;
    std::string container_id;
    std::string status;
};

/**
 * Health check result.
 */
struct HealthResult {
    std::string message;
    std::string status;
    std::string version;
};

/**
 * Query execution result.
 */
struct QueryResult {
    std::vector<Row> data;
    int rows_affected = 0;
    std::string message;
};

/**
 * Table creation result.
 */
struct CreateTableResult {
    std::string message;
    std::string table_name;
};

/**
 * Row insertion result.
 */
struct InsertResult {
    std::string message;
    int rows_affected = 0;
};

/**
 * Table drop result.
 */
struct DropResult {
    std::string message;
    std::string table_name;
};

/**
 * Column information from schema.
 */
struct ColumnInfo {
    int cid;
    std::string name;
    std::string type;
    bool not_null;
    std::string default_value;
    bool primary_key;
};

} // namespace dbforge