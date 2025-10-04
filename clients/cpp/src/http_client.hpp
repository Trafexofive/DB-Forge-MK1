#pragma once

#include <string>
#include <map>
#include <memory>

namespace dbforge {

struct HttpResponse {
    int status_code;
    std::string body;
};

/**
 * HTTP client using libcurl for making requests to DB-Forge server.
 */
class HttpClient {
public:
    explicit HttpClient(const std::string& base_url, 
                       const std::string& api_key = "", 
                       int timeout_seconds = 30);
    ~HttpClient();

    // Disable copy
    HttpClient(const HttpClient&) = delete;
    HttpClient& operator=(const HttpClient&) = delete;

    // Enable move
    HttpClient(HttpClient&&) = default;
    HttpClient& operator=(HttpClient&&) = default;

    /**
     * Make HTTP request.
     * 
     * @param method HTTP method (GET, POST, PUT, DELETE)
     * @param endpoint API endpoint
     * @param json_data JSON request body (optional)
     * @param params URL query parameters (optional)
     * @return HttpResponse with status code and body
     */
    HttpResponse request(const std::string& method, 
                        const std::string& endpoint, 
                        const std::string& json_data = "",
                        const std::map<std::string, std::string>& params = {});

private:
    struct Impl;
    std::unique_ptr<Impl> pImpl;
};

} // namespace dbforge