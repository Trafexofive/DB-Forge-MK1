#pragma once

#include "types.hpp"
#include <string>
#include <vector>

namespace dbforge {

class Client;
class HttpClient;

/**
 * Database instance for performing operations on a specific database.
 */
class Database {
public:
    /**
     * Construct database instance.
     * 
     * @param client Reference to the DB-Forge client
     * @param name Database name
     */
    Database(Client& client, const std::string& name);

    /**
     * Get the database name.
     * 
     * @return Database name
     */
    const std::string& name() const;

    // Table operations

    /**
     * Create a new table.
     * 
     * @param table_name Name of the table to create
     * @param columns Vector of column definitions
     * @return CreateTableResult with operation status
     * @throws Exception on error
     */
    CreateTableResult create_table(const std::string& table_name, const std::vector<Column>& columns);

    /**
     * Insert rows into a table.
     * 
     * @param table_name Name of the table
     * @param rows Vector of row data
     * @return InsertResult with rows affected count
     * @throws Exception on error
     */
    InsertResult insert_rows(const std::string& table_name, const std::vector<Row>& rows);

    /**
     * Select rows from a table with optional filters.
     * 
     * @param table_name Name of the table
     * @param filters Optional filter conditions (column=value pairs)
     * @return Vector of selected rows
     * @throws Exception on error
     */
    std::vector<Row> select_rows(const std::string& table_name, const Row& filters = {});

    // Query operations

    /**
     * Execute a raw SQL query.
     * 
     * @param sql SQL query string
     * @param params Optional parameters for parameterized queries
     * @return QueryResult containing data and metadata
     * @throws Exception on error
     */
    QueryResult execute_query(const std::string& sql, const Params& params = {});

    // Utility operations

    /**
     * List all tables in the database.
     * 
     * @return Vector of table names
     * @throws Exception on error
     */
    std::vector<std::string> list_tables();

    /**
     * Get schema information for a table.
     * 
     * @param table_name Name of the table
     * @return Vector of column information
     * @throws Exception on error
     */
    std::vector<ColumnInfo> get_table_schema(const std::string& table_name);

    /**
     * Drop a table from the database.
     * 
     * @param table_name Name of the table to drop
     * @return DropResult with operation status
     * @throws Exception on error
     */
    DropResult drop_table(const std::string& table_name);

    // Convenience methods

    /**
     * Update rows in a table.
     * 
     * @param table_name Name of the table
     * @param set_values Column=value pairs to update
     * @param where_conditions Column=value pairs for WHERE clause
     * @return QueryResult with rows affected count
     * @throws Exception on error
     */
    QueryResult update_rows(const std::string& table_name, 
                           const Row& set_values, 
                           const Row& where_conditions);

    /**
     * Delete rows from a table.
     * 
     * @param table_name Name of the table
     * @param where_conditions Column=value pairs for WHERE clause
     * @return QueryResult with rows affected count
     * @throws Exception on error
     */
    QueryResult delete_rows(const std::string& table_name, const Row& where_conditions);

private:
    Client& client_;
    std::string name_;
    HttpClient& http_client_;
};

} // namespace dbforge