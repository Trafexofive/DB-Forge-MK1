find_package(GTest QUIET)

if(GTest_FOUND)
    add_executable(test_client test_client.cpp)
    target_link_libraries(test_client dbforge_client GTest::gtest GTest::gtest_main)
    add_test(NAME ClientTests COMMAND test_client)
else()
    message(STATUS "Google Test not found, skipping tests. Install with: sudo apt-get install libgtest-dev")
endif()