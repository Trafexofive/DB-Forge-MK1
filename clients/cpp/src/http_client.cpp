#include "http_client.hpp"
#include <dbforge/exceptions.hpp>
#include <curl/curl.h>
#include <sstream>
#include <stdexcept>

namespace dbforge {

// Callback function for writing HTTP response data
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    size_t totalSize = size * nmemb;
    userp->append(static_cast<char*>(contents), totalSize);
    return totalSize;
}

struct HttpClient::Impl {
    CURL* curl;
    struct curl_slist* headers;
    std::string base_url;
    int timeout_seconds;

    Impl(const std::string& base_url, int timeout_seconds)
        : curl(nullptr), headers(nullptr), base_url(base_url), timeout_seconds(timeout_seconds) {
        
        curl = curl_easy_init();
        if (!curl) {
            throw std::runtime_error("Failed to initialize libcurl");
        }

        // Set basic options
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout_seconds);
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 2L);

        // Set default headers
        headers = curl_slist_append(headers, "Content-Type: application/json");
        headers = curl_slist_append(headers, "User-Agent: DBForge-CPP-Client/1.0.0");
    }

    ~Impl() {
        if (headers) {
            curl_slist_free_all(headers);
        }
        if (curl) {
            curl_easy_cleanup(curl);
        }
    }
};

HttpClient::HttpClient(const std::string& base_url, const std::string& api_key, int timeout_seconds)
    : pImpl(std::make_unique<Impl>(base_url, timeout_seconds)) {
    
    if (!api_key.empty()) {
        std::string auth_header = "X-API-Key: " + api_key;
        pImpl->headers = curl_slist_append(pImpl->headers, auth_header.c_str());
    }
}

HttpClient::~HttpClient() = default;

HttpResponse HttpClient::request(const std::string& method, 
                                const std::string& endpoint, 
                                const std::string& json_data,
                                const std::map<std::string, std::string>& params) {
    
    std::string response_data;
    long response_code = 0;

    // Build URL
    std::string url = pImpl->base_url;
    if (url.back() != '/' && endpoint.front() != '/') {
        url += "/";
    }
    url += endpoint;

    // Add query parameters
    if (!params.empty()) {
        url += "?";
        bool first = true;
        for (const auto& param : params) {
            if (!first) url += "&";
            url += param.first + "=" + param.second; // TODO: URL encode
            first = false;
        }
    }

    // Set URL
    curl_easy_setopt(pImpl->curl, CURLOPT_URL, url.c_str());

    // Set method and data
    if (method == "GET") {
        curl_easy_setopt(pImpl->curl, CURLOPT_HTTPGET, 1L);
    } else if (method == "POST") {
        curl_easy_setopt(pImpl->curl, CURLOPT_POST, 1L);
        if (!json_data.empty()) {
            curl_easy_setopt(pImpl->curl, CURLOPT_POSTFIELDS, json_data.c_str());
            curl_easy_setopt(pImpl->curl, CURLOPT_POSTFIELDSIZE, json_data.length());
        }
    } else if (method == "PUT") {
        curl_easy_setopt(pImpl->curl, CURLOPT_CUSTOMREQUEST, "PUT");
        if (!json_data.empty()) {
            curl_easy_setopt(pImpl->curl, CURLOPT_POSTFIELDS, json_data.c_str());
            curl_easy_setopt(pImpl->curl, CURLOPT_POSTFIELDSIZE, json_data.length());
        }
    } else if (method == "DELETE") {
        curl_easy_setopt(pImpl->curl, CURLOPT_CUSTOMREQUEST, "DELETE");
    }

    // Set headers
    curl_easy_setopt(pImpl->curl, CURLOPT_HTTPHEADER, pImpl->headers);

    // Set response callback
    curl_easy_setopt(pImpl->curl, CURLOPT_WRITEDATA, &response_data);

    // Perform request
    CURLcode res = curl_easy_perform(pImpl->curl);

    if (res != CURLE_OK) {
        std::string error_msg = curl_easy_strerror(res);
        if (res == CURLE_OPERATION_TIMEDOUT) {
            throw TimeoutError(error_msg);
        } else if (res == CURLE_COULDNT_CONNECT || res == CURLE_COULDNT_RESOLVE_HOST) {
            throw ConnectionError(error_msg);
        } else {
            throw Exception("HTTP request failed: " + error_msg);
        }
    }

    // Get response code
    curl_easy_getinfo(pImpl->curl, CURLINFO_RESPONSE_CODE, &response_code);

    return HttpResponse{static_cast<int>(response_code), response_data};
}

} // namespace dbforge