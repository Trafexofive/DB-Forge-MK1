#!/bin/bash

# test.sh: Orchestrates API tests for the DB Gateway
# This script runs on the host and calls client.sh to interact with the DB Gateway.

CLIENT_SCRIPT="./scripts/client.sh" # Path to client.sh on the host
API_KEY="CJOWtInYnebSwD3wknEy0pgsQxvfORxXzd04OBpuYYE" # API key from first-time setup

# Function to assert a condition
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    if [ "$expected" == "$actual" ]; then
        echo "✅ $message"
    else
        echo "❌ $message"
        echo "   Expected: $expected"
        echo "   Actual:   $actual"
        exit 1
    fi
}

# --- Test Setup ---
echo "--- Running DB Gateway API Tests ---"

# Ensure the gateway is healthy
echo "Waiting for db-gateway to be healthy..."
DB_GATEWAY_CONTAINER="db-gateway"
for i in {1..30}; do # Increased from 10 to 30
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$DB_GATEWAY_CONTAINER" 2>/dev/null || echo "unhealthy")
    if [ "$STATUS" == "healthy" ]; then
        echo "db-gateway is healthy."
        break
    fi
    echo "Still waiting... ($i/30)"
    sleep 2
done

if [ "$STATUS" != "healthy" ]; then
    echo "Error: db-gateway did not become healthy in time."
    exit 1
fi

# --- Test Cases ---

# Test 1: Root endpoint
echo "Test 1: Root endpoint"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" get_root)
assert_equals "{\"message\":\"Praetorian DB-Forge is online.\"}" "$RESPONSE" "Root endpoint returns correct message"

# Test 2: Spawn a new database
echo "Test 2: Spawn a new database"
DB_NAME="test_db_spawn_01"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" spawn_db "$DB_NAME")
EXPECTED_MESSAGE="\"message\":\"Database instance spawned successfully.\""
assert_equals "true" "$(echo "$RESPONSE" | grep -q "$EXPECTED_MESSAGE" && echo "true" || echo "false")" "Spawn new DB"

# Test 3: Idempotent spawn
echo "Test 3: Idempotent spawn"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" spawn_db "$DB_NAME")
EXPECTED_MESSAGE="\"message\":\"Database instance already exists and is running.\""
assert_equals "true" "$(echo "$RESPONSE" | grep -q "$EXPECTED_MESSAGE" && echo "true" || echo "false")" "Idempotent spawn"

# Test 4: List databases
echo "Test 4: List databases"
DB_NAME_2="test_db_spawn_02"
"$CLIENT_SCRIPT" --api-key "$API_KEY" spawn_db "$DB_NAME_2" > /dev/null
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" list_dbs)
assert_equals "true" "$(echo "$RESPONSE" | grep -q "$DB_NAME" && echo "true" || echo "false")" "List contains $DB_NAME"
assert_equals "true" "$(echo "$RESPONSE" | grep -q "$DB_NAME_2" && echo "true" || echo "false")" "List contains $DB_NAME_2"

# Test 5: Prune database
echo "Test 5: Prune database"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "$DB_NAME_2")
EXPECTED_MESSAGE="\"message\":\"Database instance pruned successfully.\""
assert_equals "true" "$(echo "$RESPONSE" | grep -q "$EXPECTED_MESSAGE" && echo "true" || echo "false")" "Prune DB"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" list_dbs)
assert_equals "false" "$(echo "$RESPONSE" | grep -q "$DB_NAME_2" && echo "true" || echo "false")" "Pruned DB not in list"

# Test 6: Create table and insert data
echo "Test 6: Create table and insert data"
DB_NAME_DATA="test_db_data_01"
TABLE_NAME="users"
"$CLIENT_SCRIPT" --api-key "$API_KEY" spawn_db "$DB_NAME_DATA" > /dev/null

# Create JSON payload for table creation
cat <<EOF > scripts/create_table_payload.json
{
  "table_name": "$TABLE_NAME",
  "columns": [
    {"name": "id", "type": "INTEGER", "primary_key": true},
    {"name": "name", "type": "TEXT", "not_null": true},
    {"name": "age", "type": "INTEGER"}
  ]
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" create_table "$DB_NAME_DATA" "$TABLE_NAME" "scripts/create_table_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"message\":\"Table '$TABLE_NAME' created successfully.\"" && echo "true" || echo "false")" "Create table"

# Create JSON payload for inserting data
cat <<EOF > scripts/insert_payload.json
{
  "rows": [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 24}
  ]
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" insert_rows "$DB_NAME_DATA" "$TABLE_NAME" "scripts/insert_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"message\":\"Rows inserted successfully.\"" && echo "true" || echo "false")" "Insert data"
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":2" && echo "true" || echo "false")" "Insert data rows affected"

# Test 7: Query data
echo "Test 7: Query data"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" get_rows "$DB_NAME_DATA" "$TABLE_NAME")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":2" && echo "true" || echo "false")" "Query all data rows affected"
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"name\":\"Alice\"" && echo "true" || echo "false")" "Query all data contains Alice"

# Test 8: Query data with filter
echo "Test 8: Query data with filter"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" get_rows "$DB_NAME_DATA" "$TABLE_NAME" "age=24")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":1" && echo "true" || echo "false")" "Query filtered data rows affected"
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"name\":\"Bob\"" && echo "true" || echo "false")" "Query filtered data contains Bob"

# Test 9: Raw SQL query - SELECT
echo "Test 9: Raw SQL query - SELECT"
cat <<EOF > scripts/query_payload.json
{
  "sql": "SELECT name FROM $TABLE_NAME WHERE age = 30"
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" raw_query "$DB_NAME_DATA" "scripts/query_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"name\":\"Alice\"" && echo "true" || echo "false")" "Raw SQL SELECT"

# Test 10: Raw SQL query - INSERT
echo "Test 10: Raw SQL query - INSERT"
cat <<EOF > scripts/insert_raw_payload.json
{
  "sql": "INSERT INTO $TABLE_NAME (name, age) VALUES ('Charlie', 28)"
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" raw_query "$DB_NAME_DATA" "scripts/insert_raw_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":1" && echo "true" || echo "false")" "Raw SQL INSERT rows affected"

# Test 11: Raw SQL query - UPDATE
echo "Test 11: Raw SQL query - UPDATE"
cat <<EOF > scripts/update_raw_payload.json
{
  "sql": "UPDATE $TABLE_NAME SET age = 29 WHERE name = 'Charlie'"
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" raw_query "$DB_NAME_DATA" "scripts/update_raw_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":1" && echo "true" || echo "false")" "Raw SQL UPDATE rows affected"

# Test 12: Raw SQL query - DELETE
echo "Test 12: Raw SQL query - DELETE"
cat <<EOF > scripts/delete_raw_payload.json
{
  "sql": "DELETE FROM $TABLE_NAME WHERE name = 'Charlie'"
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" raw_query "$DB_NAME_DATA" "scripts/delete_raw_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"rows_affected\":1" && echo "true" || echo "false")" "Raw SQL DELETE rows affected"

# Test 13: Raw SQL query - SQL error handling
echo "Test 13: Raw SQL query - SQL error handling"
cat <<EOF > scripts/error_query_payload.json
{
  "sql": "SELECT * FROM non_existent_table"
}
EOF
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" raw_query "$DB_NAME_DATA" "scripts/error_query_payload.json")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"detail\":\"SQL Error:" && echo "true" || echo "false")" "Raw SQL error handling"

# Test 14: Data plane - DB not found
echo "Test 14: Data plane - DB not found"
NON_EXISTENT_DB="non_existent_db_for_test"
RESPONSE=$("$CLIENT_SCRIPT" --api-key "$API_KEY" get_rows "$NON_EXISTENT_DB" "some_table")
assert_equals "true" "$(echo "$RESPONSE" | grep -q "\"detail\":\"Database not found.\"" && echo "true" || echo "false")" "Data plane DB not found"

echo "--- All tests passed! ---"

# --- Test Teardown ---
echo "Cleaning up test databases..."
# Prune all test databases created by this script
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "$DB_NAME" > /dev/null
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "$DB_NAME_DATA" > /dev/null
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "test_db_spawn_01" > /dev/null
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "test_db_spawn_02" > /dev/null
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "test_db_data_01" > /dev/null
"$CLIENT_SCRIPT" --api-key "$API_KEY" prune_db "test_db_raw_sql" > /dev/null

# Clean up temporary JSON payload files
rm -f scripts/*.json

echo "Test cleanup complete."