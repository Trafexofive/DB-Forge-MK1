#include <dbforge/dbforge.hpp>
#include <iostream>
#include <cstdlib>

int main() {
    try {
        std::cout << "=== DB-Forge C++ Client Basic Example ===" << std::endl << std::endl;
        
        // Initialize client
        // These can also be set via environment variables:
        // DBFORGE_BASE_URL, DBFORGE_API_KEY, DBFORGE_TIMEOUT
        dbforge::Client client(
            "http://db.localhost",  // Base URL
            "",                     // API key (optional) 
            30                      // Timeout in seconds
        );
        
        const std::string db_name = "cpp_example_db";
        
        // 1. Health check
        std::cout << "1. Performing health check..." << std::endl;
        auto health = client.health_check();
        std::cout << "   Server status: " << health.message << std::endl;
        
        // 2. Spawn database
        std::cout << "\n2. Spawning database: " << db_name << std::endl;
        auto spawn_result = client.spawn_database(db_name);
        std::cout << "   Result: " << spawn_result.message << std::endl;
        std::cout << "   Container ID: " << spawn_result.container_id << std::endl;
        
        // 3. List databases
        std::cout << "\n3. Listing databases:" << std::endl;
        auto databases = client.list_databases();
        for (const auto& db : databases) {
            std::cout << "   - " << db.name << " (status: " << db.status << ")" << std::endl;
        }
        
        // 4. Get database instance
        std::cout << "\n4. Getting database instance: " << db_name << std::endl;
        auto db = client.get_database(db_name);
        
        // 5. Create table
        std::cout << "\n5. Creating users table..." << std::endl;
        std::vector<dbforge::Column> columns = {
            {"id", "INTEGER", true, false},           // primary_key=true, not_null=false
            {"username", "TEXT", false, true},        // primary_key=false, not_null=true
            {"email", "TEXT", false, true},           // primary_key=false, not_null=true
            {"created_at", "DATETIME", false, false, "CURRENT_TIMESTAMP"},  // with default
            {"is_active", "BOOLEAN", false, false, "1"}
        };
        
        auto create_result = db.create_table("users", columns);
        std::cout << "   Result: " << create_result.message << std::endl;
        
        // 6. Insert data
        std::cout << "\n6. Inserting user data..." << std::endl;
        std::vector<dbforge::Row> users = {
            {{"username", "alice"}, {"email", "alice@example.com"}},
            {{"username", "bob"}, {"email", "bob@example.com"}},
            {{"username", "charlie"}, {"email", "charlie@example.com"}}
        };
        
        auto insert_result = db.insert_rows("users", users);
        std::cout << "   Inserted " << insert_result.rows_affected << " rows" << std::endl;
        
        // 7. Query all users
        std::cout << "\n7. Querying all users:" << std::endl;
        auto all_users = db.select_rows("users");
        for (const auto& user : all_users) {
            std::cout << "   User ID: " << user.at("id") 
                      << ", Username: " << user.at("username") 
                      << ", Email: " << user.at("email") << std::endl;
        }
        
        // 8. Query with filters
        std::cout << "\n8. Querying specific user (alice):" << std::endl;
        auto alice_users = db.select_rows("users", {{"username", "alice"}});
        for (const auto& user : alice_users) {
            std::cout << "   Found: " << user.at("username") 
                      << " (" << user.at("email") << ")" << std::endl;
        }
        
        // 9. Raw SQL query
        std::cout << "\n9. Raw SQL query - counting users:" << std::endl;
        auto count_result = db.execute_query("SELECT COUNT(*) as user_count FROM users");
        if (!count_result.data.empty()) {
            std::cout << "   Total users: " << count_result.data[0].at("user_count") << std::endl;
        }
        
        // 10. Parameterized query
        std::cout << "\n10. Parameterized query - find user by email:" << std::endl;
        auto param_result = db.execute_query(
            "SELECT username FROM users WHERE email = ?",
            {"alice@example.com"}
        );

        if (!param_result.data.empty()) {
            std::cout << "   Found user: " << param_result.data[0].at("username") << std::endl;
        }
        
        // 11. Update data
        std::cout << "\n11. Updating user status..." << std::endl;
        auto update_result = db.update_rows(
            "users",
            {{"is_active", "0"}},           // SET values
            {{"username", "charlie"}}       // WHERE conditions
        );
        std::cout << "   Updated " << update_result.rows_affected << " rows" << std::endl;
        
        // 12. Verify update
        std::cout << "\n12. Verifying update:" << std::endl;
        auto charlie_users = db.select_rows("users", {{"username", "charlie"}});
        if (!charlie_users.empty()) {
            std::cout << "   Charlie's active status: " << charlie_users[0].at("is_active") << std::endl;
        }
        
        // 13. List tables
        std::cout << "\n13. Listing tables:" << std::endl;
        auto tables = db.list_tables();
        for (const auto& table : tables) {
            std::cout << "   - " << table << std::endl;
        }
        
        // 14. Get table schema
        std::cout << "\n14. Getting users table schema:" << std::endl;
        auto schema = db.get_table_schema("users");
        for (const auto& column : schema) {
            std::cout << "   Column: " << column.name 
                      << " (" << column.type << ")"
                      << (column.primary_key ? " PRIMARY KEY" : "")
                      << (column.not_null ? " NOT NULL" : "") << std::endl;
        }
        
        // 15. Delete some data
        std::cout << "\n15. Deleting inactive users..." << std::endl;
        auto delete_result = db.delete_rows("users", {{"is_active", "0"}});
        std::cout << "   Deleted " << delete_result.rows_affected << " rows" << std::endl;
        
        // 16. Final count
        std::cout << "\n16. Final user count:" << std::endl;
        auto final_count = db.execute_query("SELECT COUNT(*) as user_count FROM users");
        if (!final_count.data.empty()) {
            std::cout << "   Remaining users: " << final_count.data[0].at("user_count") << std::endl;
        }
        
        // Cleanup
        std::cout << "\n=== Cleanup ===" << std::endl;
        std::cout << "17. Pruning database: " << db_name << std::endl;
        auto prune_result = client.prune_database(db_name);
        std::cout << "   Result: " << prune_result.message << std::endl;
        
        std::cout << "\n✅ Basic example completed successfully!" << std::endl;
        
        return 0;
        
    } catch (const dbforge::Exception& e) {
        std::cerr << "❌ DB-Forge error: " << e.what() << std::endl;
        std::cerr << "   Status code: " << e.status_code() << std::endl;
        std::cerr << "   Error code: " << e.error_code() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "❌ Unexpected error: " << e.what() << std::endl;
        return 1;
    }
}
