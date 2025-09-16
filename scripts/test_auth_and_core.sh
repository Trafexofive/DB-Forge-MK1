#!/bin/bash

# test_auth_and_core.sh: Comprehensive test for authentication and core API functionality.

set -e # Exit immediately if a command exits with a non-zero status.

BASE_URL="http://localhost:8081"
HOST_HEADER="db.localhost"
API_KEY_FILE="/tmp/db_forge_api_key"
TEST_DB_NAME="test_auth_db_01"
TEST_TABLE_NAME="test_table"

echo "=== DB-Forge Authentication and Core API Test ==="

# Function to get API key from logs if not already saved
get_api_key() {
    if [ -f "$API_KEY_FILE" ]; then
        # Only output the key, nothing else
        cat "$API_KEY_FILE"
        return
    fi

    echo "!!! API KEY NOT FOUND !!!" >&2
    echo "Please check the db-gateway logs for the initial API key." >&2
    echo "Look for a line like: 'Your API Key is: <key>'" >&2
    echo "Save this key to $API_KEY_FILE" >&2
    echo "Example: echo 'your_actual_api_key_here' > $API_KEY_FILE" >&2
    echo "Then re-run this test." >&2
    exit 1
}

# Function to make a request and check the response
# Usage: make_request <method> <endpoint> <expected_status_code> [api_key] [data]
make_request() {
    local METHOD=$1
    local ENDPOINT=$2
    local EXPECTED_STATUS=$3
    local API_KEY=$4
    local DATA=$5

    local BODY_FILE=$(mktemp)
    local CURL_CMD="curl -s -o \"$BODY_FILE\" -w \"%{http_code}\" -H \"Host: $HOST_HEADER\""
    
    if [ -n "$API_KEY" ]; then
        CURL_CMD+=" -H \"X-API-Key: $API_KEY\""
    fi
    
    if [ "$METHOD" != "GET" ] && [ -n "$DATA" ]; then
        CURL_CMD+=" -H \"Content-Type: application/json\" -d '$DATA'"
    fi
    
    CURL_CMD+=" -X $METHOD \"$BASE_URL$ENDPOINT\""
    
    # Debug: Uncomment the next line to see the curl command
    # echo "DEBUG: $CURL_CMD"
    
    local HTTP_CODE=$(eval "$CURL_CMD")
    local BODY=$(cat "$BODY_FILE")
    rm -f "$BODY_FILE"
    
    if [ "$HTTP_CODE" == "$EXPECTED_STATUS" ]; then
        echo "   ✅ Request to $ENDPOINT returned $HTTP_CODE as expected."
        echo "$BODY" # Print the response body for further checks if needed
    else
        echo "   ❌ Request to $ENDPOINT failed. Expected $EXPECTED_STATUS, got $HTTP_CODE."
        echo "   Response Body: $BODY"
        exit 1
    fi
}

# --- 1. Check if the gateway is reachable ---
echo "1. Checking if DB-Gateway is reachable..."
make_request "GET" "/" "200"

# --- 2. Test Unauthenticated Access to Admin Endpoint ---
echo "2. Testing unauthenticated access to admin endpoint..."
make_request "GET" "/admin/databases" "401"

# --- 3. Get API Key ---
echo "3. Getting API key..."
API_KEY=$(get_api_key)
echo "   API Key: $API_KEY"

# --- 4. Test Authenticated Access to Admin Endpoint ---
echo "4. Testing authenticated access to admin endpoint..."
make_request "GET" "/admin/databases" "200" "$API_KEY"

# --- 5. Test Core Admin API Functionality ---
echo "5. Testing core admin API functionality (spawn, list, prune)..."

# Spawn DB
echo "   a) Spawning database..."
RESPONSE=$(make_request "POST" "/admin/databases/spawn/$TEST_DB_NAME" "201" "$API_KEY")
# The response should contain the database name
if echo "$RESPONSE" | grep -q "\"db_name\":\"$TEST_DB_NAME\""; then
    echo "      ✅ Spawn database successful."
else
    echo "      ❌ Spawn database response unexpected."
    echo "      Response: $RESPONSE"
    exit 1
fi

# List Databases and check if our test DB is there
echo "   b) Listing databases..."
RESPONSE=$(make_request "GET" "/admin/databases" "200" "$API_KEY")
if echo "$RESPONSE" | grep -q "\"name\":\"$TEST_DB_NAME\""; then
    echo "      ✅ List databases includes test DB."
else
    echo "      ❌ List databases does not include test DB."
    echo "      Response: $RESPONSE"
    exit 1
fi

# --- 6. Test Data Plane API Functionality ---
echo "6. Testing data plane API functionality..."

# Create a table
echo "   a) Creating a table..."
CREATE_TABLE_DATA='{
    "table_name": "'"$TEST_TABLE_NAME"'",
    "columns": [
        {"name": "id", "type": "INTEGER", "primary_key": true},
        {"name": "name", "type": "TEXT", "not_null": true},
        {"name": "value", "type": "INTEGER"}
    ]
}'
make_request "POST" "/api/db/$TEST_DB_NAME/tables" "201" "$API_KEY" "$CREATE_TABLE_DATA"

# Insert data
echo "   b) Inserting data..."
INSERT_DATA='{
    "rows": [
        {"name": "item1", "value": 100},
        {"name": "item2", "value": 200}
    ]
}'
make_request "POST" "/api/db/$TEST_DB_NAME/tables/$TEST_TABLE_NAME/rows" "201" "$API_KEY" "$INSERT_DATA"

# Query data
echo "   c) Querying data..."
RESPONSE=$(make_request "GET" "/api/db/$TEST_DB_NAME/tables/$TEST_TABLE_NAME/rows" "200" "$API_KEY")
if echo "$RESPONSE" | grep -q "\"rows_affected\":2"; then
    echo "      ✅ Query returned 2 rows as expected."
else
    echo "      ❌ Query did not return expected number of rows."
    echo "      Response: $RESPONSE"
    exit 1
fi

# Query with filter
echo "   d) Querying data with filter..."
RESPONSE=$(make_request "GET" "/api/db/$TEST_DB_NAME/tables/$TEST_TABLE_NAME/rows?name=item1" "200" "$API_KEY")
if echo "$RESPONSE" | grep -q "\"rows_affected\":1" && echo "$RESPONSE" | grep -q "\"name\":\"item1\""; then
    echo "      ✅ Filtered query returned 1 row as expected."
else
    echo "      ❌ Filtered query did not return expected result."
    echo "      Response: $RESPONSE"
    exit 1
fi

# --- 7. Cleanup ---
echo "7. Cleaning up test database..."
make_request "POST" "/admin/databases/prune/$TEST_DB_NAME" "200" "$API_KEY"

echo "=== All tests passed! ==="
exit 0