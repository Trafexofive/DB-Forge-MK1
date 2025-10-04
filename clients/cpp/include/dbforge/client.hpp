#pragma once

#include "types.hpp"
#include "database.hpp"
#include <string>
#include <vector>
#include <memory>

namespace dbforge {

class HttpClient;

/**
 * Main DB-Forge client class for admin operations and database management.
 */
class Client {
public:
    /**
     * Construct a new DB-Forge client.
     * 
     * @param base_url Base URL of the DB-Forge server (e.g., "http://db.localhost")
     * @param api_key Optional API key for authentication
     * @param timeout_seconds Request timeout in seconds (default: 30)
     */
    explicit Client(
        const std::string& base_url,
        const std::string& api_key = "",
        int timeout_seconds = 30
    );
    
    /**
     * Destructor
     */
    ~Client();
    
    // Disable copy constructor and assignment
    Client(const Client&) = delete;
    Client& operator=(const Client&) = delete;
    
    // Enable move constructor and assignment
    Client(Client&&) = default;
    Client& operator=(Client&&) = default;

    // Admin API operations

    /**
     * Spawn a new database instance.
     * 
     * @param name Database name
     * @return SpawnResult containing database information
     * @throws Exception on error
     */
    SpawnResult spawn_database(const std::string& name);

    /**
     * Prune (remove) a database instance.
     * 
     * @param name Database name
     * @return PruneResult containing operation status
     * @throws Exception on error
     */
    PruneResult prune_database(const std::string& name);

    /**
     * List all active database instances.
     * 
     * @return Vector of DatabaseInfo objects
     * @throws Exception on error
     */
    std::vector<DatabaseInfo> list_databases();

    /**
     * Get a database instance for operations.
     * 
     * @param name Database name
     * @return Database object for performing operations
     */
    Database get_database(const std::string& name);

    /**
     * Perform health check on the DB-Forge server.
     * 
     * @return HealthResult containing server status
     * @throws Exception on error
     */
    HealthResult health_check();

    /**
     * Get the base URL of the DB-Forge server.
     * 
     * @return Base URL string
     */
    const std::string& base_url() const;

    /**
     * Get the API key (if set).
     * 
     * @return API key string (may be empty)
     */
    const std::string& api_key() const;

private:
    std::string base_url_;
    std::string api_key_;
    std::unique_ptr<HttpClient> http_client_;
    
    friend class Database;
};

} // namespace dbforge