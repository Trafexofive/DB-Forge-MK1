#include <dbforge/client.hpp>
#include <dbforge/exceptions.hpp>
#include "http_client.hpp"
#include "json_utils.hpp"
#include <cstdlib>

namespace dbforge {

Client::Client(const std::string& base_url, const std::string& api_key, int timeout_seconds)
    : base_url_(base_url), api_key_(api_key) {
    
    // Allow environment variable override for base_url if not provided
    std::string actual_base_url = base_url;
    if (actual_base_url.empty()) {
        const char* env_url = std::getenv("DBFORGE_BASE_URL");
        if (env_url) {
            actual_base_url = env_url;
        } else {
            actual_base_url = "http://db.localhost";
        }
    }
    
    // Allow environment variable override for api_key if not provided
    std::string actual_api_key = api_key;
    if (actual_api_key.empty()) {
        const char* env_key = std::getenv("DBFORGE_API_KEY");
        if (env_key) {
            actual_api_key = env_key;
        }
    }
    
    // Allow environment variable override for timeout
    int actual_timeout = timeout_seconds;
    const char* env_timeout = std::getenv("DBFORGE_TIMEOUT");
    if (env_timeout) {
        try {
            actual_timeout = std::stoi(env_timeout);
        } catch (...) {
            // Ignore parsing errors, use default
        }
    }
    
    base_url_ = actual_base_url;
    api_key_ = actual_api_key;
    
    http_client_ = std::make_unique<HttpClient>(base_url_, api_key_, actual_timeout);
}

Client::~Client() = default;

SpawnResult Client::spawn_database(const std::string& name) {
    auto response = http_client_->request("POST", "/admin/databases/spawn/" + name);
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_spawn_result(json);
}

PruneResult Client::prune_database(const std::string& name) {
    auto response = http_client_->request("POST", "/admin/databases/prune/" + name);
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_prune_result(json);
}

std::vector<DatabaseInfo> Client::list_databases() {
    auto response = http_client_->request("GET", "/admin/databases");
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_database_list(json);
}

Database Client::get_database(const std::string& name) {
    return Database(*this, name);
}

HealthResult Client::health_check() {
    auto response = http_client_->request("GET", "/");
    auto json = json_utils::parse_json(response.body);
    json_utils::check_error_response(response.status_code, json);
    return json_utils::parse_health_result(json);
}

const std::string& Client::base_url() const {
    return base_url_;
}

const std::string& Client::api_key() const {
    return api_key_;
}

} // namespace dbforge