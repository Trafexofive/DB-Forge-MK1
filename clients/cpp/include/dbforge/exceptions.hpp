#pragma once

#include <stdexcept>
#include <string>

namespace dbforge {

/**
 * Base exception for all DB-Forge related errors.
 */
class Exception : public std::runtime_error {
public:
    explicit Exception(const std::string& message, 
                      int status_code = 0, 
                      const std::string& error_code = "")
        : std::runtime_error(message), 
          status_code_(status_code), 
          error_code_(error_code) {}

    /**
     * Get HTTP status code (if available).
     * 
     * @return HTTP status code or 0 if not available
     */
    int status_code() const noexcept { return status_code_; }

    /**
     * Get error code (if available).
     * 
     * @return Error code string
     */
    const std::string& error_code() const noexcept { return error_code_; }

private:
    int status_code_;
    std::string error_code_;
};

/**
 * Thrown when a database instance is not found (404).
 */
class DatabaseNotFound : public Exception {
public:
    explicit DatabaseNotFound(const std::string& message, 
                             int status_code = 404, 
                             const std::string& error_code = "NOT_FOUND")
        : Exception(message, status_code, error_code) {}
};

/**
 * Thrown when a request is invalid (400).
 */
class InvalidRequest : public Exception {
public:
    explicit InvalidRequest(const std::string& message, 
                           int status_code = 400, 
                           const std::string& error_code = "BAD_REQUEST")
        : Exception(message, status_code, error_code) {}
};

/**
 * Thrown when authentication fails (401).
 */
class AuthenticationError : public Exception {
public:
    explicit AuthenticationError(const std::string& message, 
                                int status_code = 401, 
                                const std::string& error_code = "UNAUTHORIZED")
        : Exception(message, status_code, error_code) {}
};

/**
 * Thrown when server encounters an error (5xx).
 */
class ServerError : public Exception {
public:
    explicit ServerError(const std::string& message, 
                        int status_code = 500, 
                        const std::string& error_code = "SERVER_ERROR")
        : Exception(message, status_code, error_code) {}
};

/**
 * Thrown when unable to connect to the server.
 */
class ConnectionError : public Exception {
public:
    explicit ConnectionError(const std::string& message)
        : Exception("Connection failed: " + message, 0, "CONNECTION_ERROR") {}
};

/**
 * Thrown when a request times out.
 */
class TimeoutError : public Exception {
public:
    explicit TimeoutError(const std::string& message)
        : Exception("Request timed out: " + message, 0, "TIMEOUT_ERROR") {}
};

} // namespace dbforge