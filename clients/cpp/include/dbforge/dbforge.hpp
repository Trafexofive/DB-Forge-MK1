#pragma once

/**
 * DB-Forge C++ Client Library
 * 
 * Single header include for all DB-Forge functionality.
 */

#include "types.hpp"
#include "exceptions.hpp"
#include "database.hpp"
#include "client.hpp"

namespace dbforge {

/**
 * Library version information.
 */
struct Version {
    static constexpr int major = 1;
    static constexpr int minor = 0;
    static constexpr int patch = 0;
    static constexpr const char* string = "1.0.0";
};

} // namespace dbforge