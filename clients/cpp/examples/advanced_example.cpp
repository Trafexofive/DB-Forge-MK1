#include <dbforge/dbforge.hpp>
#include <iostream>
#include <thread>
#include <future>
#include <vector>
#include <chrono>
#include <random>

int main() {
    try {
        std::cout << "=== DB-Forge C++ Client Advanced Example ===" << std::endl << std::endl;
        
        dbforge::Client client("http://db.localhost");
        const std::string db_name = "advanced_cpp_db";
        
        // 1. Setup database with multiple tables
        std::cout << "1. Setting up database with multiple tables..." << std::endl;
        client.spawn_database(db_name);
        auto db = client.get_database(db_name);
        
        // Create users table
        db.create_table("users", {
            {"id", "INTEGER", true, false},
            {"name", "TEXT", false, true},
            {"email", "TEXT", false, true},
            {"created_at", "DATETIME", false, false, "CURRENT_TIMESTAMP"}
        });
        
        // Create products table
        db.create_table("products", {
            {"id", "INTEGER", true, false},
            {"name", "TEXT", false, true},
            {"price", "REAL", false, true},
            {"category", "TEXT", false, false, "general"}
        });
        
        // Create orders table
        db.create_table("orders", {
            {"id", "INTEGER", true, false},
            {"user_id", "INTEGER", false, true},
            {"product_id", "INTEGER", false, true},
            {"quantity", "INTEGER", false, false, "1"},
            {"order_date", "DATETIME", false, false, "CURRENT_TIMESTAMP"}
        });
        
        std::cout << "   Created tables: users, products, orders" << std::endl;
        
        // 2. Bulk insert data
        std::cout << "\n2. Bulk inserting sample data..." << std::endl;
        
        // Insert users
        std::vector<dbforge::Row> users = {
            {{"name", "Alice Johnson"}, {"email", "alice@example.com"}},
            {{"name", "Bob Smith"}, {"email", "bob@example.com"}},
            {{"name", "Charlie Brown"}, {"email", "charlie@example.com"}},
            {{"name", "Diana Prince"}, {"email", "diana@example.com"}},
            {{"name", "Eve Wilson"}, {"email", "eve@example.com"}}
        };
        auto user_result = db.insert_rows("users", users);
        std::cout << "   Inserted " << user_result.rows_affected << " users" << std::endl;
        
        // Insert products
        std::vector<dbforge::Row> products = {
            {{"name", "Laptop"}, {"price", "999.99"}, {"category", "electronics"}},
            {{"name", "Mouse"}, {"price", "29.99"}, {"category", "electronics"}},
            {{"name", "Keyboard"}, {"price", "79.99"}, {"category", "electronics"}},
            {{"name", "Monitor"}, {"price", "299.99"}, {"category", "electronics"}},
            {{"name", "Desk Chair"}, {"price", "199.99"}, {"category", "furniture"}},
            {{"name", "Coffee Mug"}, {"price", "12.99"}, {"category", "accessories"}}
        };
        auto product_result = db.insert_rows("products", products);
        std::cout << "   Inserted " << product_result.rows_affected << " products" << std::endl;
        
        // Insert orders
        std::vector<dbforge::Row> orders = {
            {{"user_id", "1"}, {"product_id", "1"}, {"quantity", "1"}},   // Alice buys laptop
            {{"user_id", "1"}, {"product_id", "2"}, {"quantity", "2"}},   // Alice buys 2 mice
            {{"user_id", "2"}, {"product_id", "3"}, {"quantity", "1"}},   // Bob buys keyboard
            {{"user_id", "2"}, {"product_id", "5"}, {"quantity", "1"}},   // Bob buys chair
            {{"user_id", "3"}, {"product_id", "4"}, {"quantity", "1"}},   // Charlie buys monitor
            {{"user_id", "4"}, {"product_id", "6"}, {"quantity", "3"}},   // Diana buys 3 mugs
            {{"user_id", "5"}, {"product_id", "1"}, {"quantity", "1"}},   // Eve buys laptop
            {{"user_id", "5"}, {"product_id", "4"}, {"quantity", "2"}}    // Eve buys 2 monitors
        };
        auto order_result = db.insert_rows("orders", orders);
        std::cout << "   Inserted " << order_result.rows_affected << " orders" << std::endl;
        
        // 3. Complex analytics queries
        std::cout << "\n3. Running analytics queries..." << std::endl;
        
        // Customer spending analysis
        auto spending_analysis = db.execute_query(R"(
            SELECT 
                u.name as customer,
                u.email,
                COUNT(o.id) as order_count,
                SUM(p.price * o.quantity) as total_spent,
                AVG(p.price * o.quantity) as avg_order_value
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            LEFT JOIN products p ON o.product_id = p.id
            GROUP BY u.id, u.name, u.email
            HAVING total_spent > 0
            ORDER BY total_spent DESC
        )");
        
        std::cout << "   Customer Spending Analysis:" << std::endl;
        for (const auto& row : spending_analysis.data) {
            std::cout << "     " << row.at("customer") 
                      << " - Orders: " << row.at("order_count")
                      << ", Total: $" << row.at("total_spent")
                      << ", Avg: $" << row.at("avg_order_value") << std::endl;
        }
        
        // Product popularity
        auto product_popularity = db.execute_query(R"(
            SELECT 
                p.name,
                p.category,
                COUNT(o.id) as times_ordered,
                SUM(o.quantity) as total_quantity,
                SUM(p.price * o.quantity) as total_revenue
            FROM products p
            LEFT JOIN orders o ON p.id = o.product_id
            GROUP BY p.id, p.name, p.category
            ORDER BY total_revenue DESC
        )");
        
        std::cout << "\n   Product Popularity:" << std::endl;
        for (const auto& row : product_popularity.data) {
            std::cout << "     " << row.at("name") 
                      << " (" << row.at("category") << ")"
                      << " - Ordered: " << row.at("times_ordered") << " times"
                      << ", Revenue: $" << row.at("total_revenue") << std::endl;
        }
        
        // 4. Data manipulation examples
        std::cout << "\n4. Data manipulation examples..." << std::endl;
        
        // Add discount column to products
        db.execute_query("ALTER TABLE products ADD COLUMN discount REAL DEFAULT 0.0");
        
        // Apply discounts to electronics
        auto discount_update = db.update_rows(
            "products",
            {{"discount", "0.10"}},     // 10% discount
            {{"category", "electronics"}}
        );
        std::cout << "   Applied 10% discount to " << discount_update.rows_affected << " electronics" << std::endl;
        
        // Calculate discounted prices
        auto discounted_products = db.execute_query(R"(
            SELECT 
                name,
                price as original_price,
                (price * (1 - discount)) as discounted_price,
                (discount * 100) as discount_percent
            FROM products
            WHERE discount > 0
        )");
        
        std::cout << "   Discounted Products:" << std::endl;
        for (const auto& row : discounted_products.data) {
            std::cout << "     " << row.at("name")
                      << " - Original: $" << row.at("original_price")
                      << ", Discounted: $" << row.at("discounted_price")
                      << " (" << row.at("discount_percent") << "% off)" << std::endl;
        }
        
        // 5. Transaction simulation
        std::cout << "\n5. Simulating transactions..." << std::endl;
        
        // Create a transaction log table
        db.create_table("transaction_log", {
            {"id", "INTEGER", true, false},
            {"operation", "TEXT", false, true},
            {"table_name", "TEXT", false, true},
            {"record_id", "TEXT", false, false},
            {"timestamp", "DATETIME", false, false, "CURRENT_TIMESTAMP"}
        });
        
        // Simulate adding a new user and their first order
        std::string new_user_email = "frank@example.com";
        
        // Insert user
        db.insert_rows("users", {{{"name", "Frank Miller"}, {"email", new_user_email}}});
        
        // Get the new user ID
        auto new_user = db.execute_query("SELECT id FROM users WHERE email = ?", {new_user_email});
        std::string user_id = new_user.data[0].at("id");
        
        // Log the user creation
        db.insert_rows("transaction_log", {
            {{"operation", "INSERT"}, {"table_name", "users"}, {"record_id", user_id}}
        });
        
        // Add their order
        db.insert_rows("orders", {{{"user_id", user_id}, {"product_id", "2"}, {"quantity", "1"}}});
        
        // Log the order creation
        auto new_order = db.execute_query("SELECT last_insert_rowid() as order_id");
        std::string order_id = new_order.data[0].at("order_id");
        db.insert_rows("transaction_log", {
            {{"operation", "INSERT"}, {"table_name", "orders"}, {"record_id", order_id}}
        });
        
        std::cout << "   Created user " << user_id << " and order " << order_id << std::endl;
        
        // 6. Performance testing
        std::cout << "\n6. Performance testing..." << std::endl;
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        // Batch insert performance test
        std::vector<dbforge::Row> batch_users;
        for (int i = 0; i < 100; ++i) {
            batch_users.push_back({
                {"name", "User" + std::to_string(i)},
                {"email", "user" + std::to_string(i) + "@batch.test"}
            });
        }
        
        db.insert_rows("users", batch_users);
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        
        std::cout << "   Inserted 100 users in " << duration.count() << "ms" << std::endl;
        
        // 7. Final statistics
        std::cout << "\n7. Final database statistics..." << std::endl;
        
        auto stats = db.execute_query(R"(
            SELECT 
                (SELECT COUNT(*) FROM users) as user_count,
                (SELECT COUNT(*) FROM products) as product_count,
                (SELECT COUNT(*) FROM orders) as order_count,
                (SELECT SUM(p.price * o.quantity) FROM orders o JOIN products p ON o.product_id = p.id) as total_revenue
        )");
        
        if (!stats.data.empty()) {
            auto row = stats.data[0];
            std::cout << "   Users: " << row.at("user_count") << std::endl;
            std::cout << "   Products: " << row.at("product_count") << std::endl;
            std::cout << "   Orders: " << row.at("order_count") << std::endl;
            std::cout << "   Total Revenue: $" << row.at("total_revenue") << std::endl;
        }
        
        // Cleanup
        std::cout << "\n=== Cleanup ===" << std::endl;
        client.prune_database(db_name);
        std::cout << "Database cleaned up successfully." << std::endl;
        
        std::cout << "\n✅ Advanced example completed successfully!" << std::endl;
        
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