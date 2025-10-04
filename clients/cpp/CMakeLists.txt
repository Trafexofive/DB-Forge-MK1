cmake_minimum_required(VERSION 3.15)
project(DBForgeClient VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_EXAMPLES "Build example programs" ON)
option(BUILD_TESTS "Build tests" ON)

# Find required packages
find_package(CURL REQUIRED)

# Check if we have pkg-config for finding jsoncpp
find_package(PkgConfig QUIET)
if(PkgConfig_FOUND)
    pkg_check_modules(JSONCPP jsoncpp)
endif()

# If pkg-config didn't find jsoncpp, try find_package
if(NOT JSONCPP_FOUND)
    find_package(jsoncpp REQUIRED)
    set(JSONCPP_LIBRARIES jsoncpp_lib)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Library source files
set(SOURCES
    src/dbforge_client.cpp
    src/dbforge_database.cpp
    src/dbforge_exceptions.cpp
    src/http_client.cpp
    src/json_utils.cpp
)

# Create library
add_library(dbforge_client ${SOURCES})

# Link libraries
target_link_libraries(dbforge_client 
    PUBLIC ${CURL_LIBRARIES}
    PUBLIC ${JSONCPP_LIBRARIES}
)

target_include_directories(dbforge_client
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CURL_INCLUDE_DIRS}
        ${JSONCPP_INCLUDE_DIRS}
)

# Compiler flags
target_compile_options(dbforge_client PRIVATE ${CURL_CFLAGS_OTHER})

# Examples
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Install configuration
install(TARGETS dbforge_client
    EXPORT DBForgeClientTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/dbforge
    DESTINATION include
)

install(EXPORT DBForgeClientTargets
    FILE DBForgeClientConfig.cmake
    NAMESPACE DBForge::
    DESTINATION lib/cmake/DBForgeClient
)

# Package configuration
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    DBForgeClientConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/DBForgeClientConfigVersion.cmake
    DESTINATION lib/cmake/DBForgeClient
)