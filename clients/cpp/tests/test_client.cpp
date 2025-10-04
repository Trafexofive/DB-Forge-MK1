#include <gtest/gtest.h>
#include <dbforge/dbforge.hpp>

class DBForgeClientTest : public ::testing::Test {
protected:
    void SetUp() override {
        // These tests require a running DB-Forge instance
        // Skip tests if server is not available
    }
    
    void TearDown() override {
        // Cleanup any test databases
    }
};

TEST_F(DBForgeClientTest, ClientConstruction) {
    EXPECT_NO_THROW({
        dbforge::Client client("http://test.localhost", "test-key", 30);
        EXPECT_EQ(client.base_url(), "http://test.localhost");
        EXPECT_EQ(client.api_key(), "test-key");
    });
}

TEST_F(DBForgeClientTest, ColumnConstruction) {
    dbforge::Column col1("id", "INTEGER");
    EXPECT_EQ(col1.name, "id");
    EXPECT_EQ(col1.type, "INTEGER");
    EXPECT_FALSE(col1.primary_key);
    EXPECT_FALSE(col1.not_null);
    
    dbforge::Column col2("username", "TEXT", true, true, "default_user");
    EXPECT_EQ(col2.name, "username");
    EXPECT_EQ(col2.type, "TEXT");
    EXPECT_TRUE(col2.primary_key);
    EXPECT_TRUE(col2.not_null);
    EXPECT_EQ(col2.default_value, "default_user");
}

TEST_F(DBForgeClientTest, ExceptionHierarchy) {
    try {
        throw dbforge::DatabaseNotFound("Test message", 404, "NOT_FOUND");
    } catch (const dbforge::DatabaseNotFound& e) {
        EXPECT_EQ(e.status_code(), 404);
        EXPECT_EQ(e.error_code(), "NOT_FOUND");
        EXPECT_STREQ(e.what(), "Test message");
    } catch (...) {
        FAIL() << "Wrong exception type caught";
    }
    
    try {
        throw dbforge::InvalidRequest("Bad request");
    } catch (const dbforge::Exception& e) {
        EXPECT_EQ(e.status_code(), 400);
        EXPECT_EQ(e.error_code(), "BAD_REQUEST");
    } catch (...) {
        FAIL() << "Exception not caught as base type";
    }
}

// Integration tests (require running server)
class DBForgeIntegrationTest : public ::testing::Test {
protected:
    void SetUp() override {
        try {
            client = std::make_unique<dbforge::Client>("http://db.localhost");
            // Try to connect to server
            client->health_check();
            server_available = true;
        } catch (...) {
            server_available = false;
            GTEST_SKIP() << "DB-Forge server not available, skipping integration tests";
        }
    }
    
    void TearDown() override {
        if (server_available && client) {
            // Cleanup test database if it exists
            try {
                client->prune_database("test_db");
            } catch (...) {
                // Ignore cleanup errors
            }
        }
    }
    
    std::unique_ptr<dbforge::Client> client;
    bool server_available = false;
};

TEST_F(DBForgeIntegrationTest, DatabaseLifecycle) {
    if (!server_available) return;
    
    // Spawn database
    auto spawn_result = client->spawn_database("test_db");
    EXPECT_FALSE(spawn_result.message.empty());
    EXPECT_EQ(spawn_result.database_name, "test_db");
    
    // List databases
    auto databases = client->list_databases();
    bool found = false;
    for (const auto& db : databases) {
        if (db.name == "test_db") {
            found = true;
            break;
        }
    }
    EXPECT_TRUE(found);
    
    // Get database instance
    auto db = client->get_database("test_db");
    EXPECT_EQ(db.name(), "test_db");
    
    // Prune database
    auto prune_result = client->prune_database("test_db");
    EXPECT_FALSE(prune_result.message.empty());
}

TEST_F(DBForgeIntegrationTest, TableOperations) {
    if (!server_available) return;
    
    client->spawn_database("test_db");
    auto db = client->get_database("test_db");
    
    // Create table
    std::vector<dbforge::Column> columns = {
        {"id", "INTEGER", true, false},
        {"name", "TEXT", false, true}
    };
    
    auto create_result = db.create_table("test_table", columns);
    EXPECT_FALSE(create_result.message.empty());
    
    // List tables
    auto tables = db.list_tables();
    EXPECT_EQ(tables.size(), 1);
    EXPECT_EQ(tables[0], "test_table");
    
    // Get schema
    auto schema = db.get_table_schema("test_table");
    EXPECT_EQ(schema.size(), 2);
    
    // Insert data
    std::vector<dbforge::Row> rows = {
        {{"name", "Alice"}},
        {{"name", "Bob"}}
    };
    
    auto insert_result = db.insert_rows("test_table", rows);
    EXPECT_EQ(insert_result.rows_affected, 2);
    
    // Select data
    auto selected = db.select_rows("test_table");
    EXPECT_EQ(selected.size(), 2);
    
    // Query with filter
    auto filtered = db.select_rows("test_table", {{"name", "Alice"}});
    EXPECT_EQ(filtered.size(), 1);
    EXPECT_EQ(filtered[0].at("name"), "Alice");
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}