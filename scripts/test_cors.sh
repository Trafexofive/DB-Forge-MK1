#!/bin/bash

# test_cors.sh: End-to-end test for CORS functionality and basic API health.

set -e # Exit immediately if a command exits with a non-zero status.

BASE_URL="http://localhost:8081"
HOST_HEADER="db.localhost:8081"
FRONTEND_ORIGIN="http://localhost:3000"
TEST_DB_NAME="test_cors_db_01"

echo "=== DB-Forge CORS & API Smoke Test ==="

# --- 1. Check if the gateway is reachable ---
echo "1. Checking if DB-Gateway is reachable..."
curl -s -f -H "Host: $HOST_HEADER" "$BASE_URL/" > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ DB-Gateway is reachable."
else
    echo "   ❌ DB-Gateway is NOT reachable at $BASE_URL/"
    exit 1
fi

# --- 2. Test CORS Pre-flight Request ---
echo "2. Testing CORS pre-flight (OPTIONS) request..."
RESPONSE_HEADERS=$(mktemp)
curl -s -i -X OPTIONS \
  -H "Host: $HOST_HEADER" \
  -H "Origin: $FRONTEND_ORIGIN" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  "$BASE_URL/admin/databases/spawn/$TEST_DB_NAME" > "$RESPONSE_HEADERS"

# Check status code
if grep -q "HTTP/1.1 200 OK" "$RESPONSE_HEADERS"; then
    echo "   ✅ Pre-flight request returned 200 OK."
else
    echo "   ❌ Pre-flight request did not return 200 OK."
    cat "$RESPONSE_HEADERS"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

# Check for key CORS headers
if grep -q "Access-Control-Allow-Origin: $FRONTEND_ORIGIN" "$RESPONSE_HEADERS"; then
    echo "   ✅ Correct Access-Control-Allow-Origin header found."
else
    echo "   ❌ Access-Control-Allow-Origin header not found or incorrect."
    grep "Access-Control-Allow-Origin" "$RESPONSE_HEADERS" || echo "   (Header not present)"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

if grep -q "Access-Control-Allow-Methods:" "$RESPONSE_HEADERS" && grep -q "POST" "$RESPONSE_HEADERS"; then
    echo "   ✅ Access-Control-Allow-Methods includes POST."
else
    echo "   ❌ Access-Control-Allow-Methods header not found or does not include POST."
    grep "Access-Control-Allow-Methods" "$RESPONSE_HEADERS" || echo "   (Header not present)"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

if grep -q "Access-Control-Allow-Headers: Content-Type" "$RESPONSE_HEADERS"; then
    echo "   ✅ Correct Access-Control-Allow-Headers header found."
else
    echo "   ❌ Access-Control-Allow-Headers header not found or incorrect."
    grep "Access-Control-Allow-Headers" "$RESPONSE_HEADERS" || echo "   (Header not present)"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

rm -f "$RESPONSE_HEADERS"

# --- 3. Test CORS on Simple Request ---
echo "3. Testing CORS on simple GET request..."
RESPONSE_HEADERS=$(mktemp)
curl -s -i -H "Host: $HOST_HEADER" -H "Origin: $FRONTEND_ORIGIN" "$BASE_URL/admin/databases" > "$RESPONSE_HEADERS"

# Check status code
if grep -q "HTTP/1.1 200 OK" "$RESPONSE_HEADERS"; then
    echo "   ✅ Simple GET request returned 200 OK."
else
    echo "   ❌ Simple GET request did not return 200 OK."
    cat "$RESPONSE_HEADERS"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

# Check for CORS headers on simple request
if grep -q "Access-Control-Allow-Origin: *" "$RESPONSE_HEADERS" || grep -q "Access-Control-Allow-Origin: $FRONTEND_ORIGIN" "$RESPONSE_HEADERS"; then
    echo "   ✅ Access-Control-Allow-Origin header found for simple request."
else
    echo "   ❌ Access-Control-Allow-Origin header not found for simple request."
    grep "Access-Control-Allow-Origin" "$RESPONSE_HEADERS" || echo "   (Header not present)"
    rm -f "$RESPONSE_HEADERS"
    exit 1
fi

rm -f "$RESPONSE_HEADERS"

# --- 4. Test Core API Functionality (Spawn, List, Prune) ---
echo "4. Testing core API functionality (spawn, list, prune)..."
# Spawn DB
RESPONSE=$(curl -s -X POST -H "Host: $HOST_HEADER" "$BASE_URL/admin/databases/spawn/$TEST_DB_NAME")
if echo "$RESPONSE" | grep -q "\"message\":\"Database instance spawned successfully.\""; then
    echo "   ✅ Spawn database successful."
elif echo "$RESPONSE" | grep -q "\"message\":\"Database instance already exists and is running.\""; then
    echo "   ✅ Spawn database successful (already existed)."
else
    echo "   ❌ Spawn database failed."
    echo "   Response: $RESPONSE"
    exit 1
fi

# List Databases and check if our test DB is there
RESPONSE=$(curl -s -H "Host: $HOST_HEADER" "$BASE_URL/admin/databases")
if echo "$RESPONSE" | grep -q "\"name\":\"$TEST_DB_NAME\""; then
    echo "   ✅ List databases includes test DB."
else
    echo "   ❌ List databases does not include test DB."
    echo "   Response: $RESPONSE"
    # We'll try to prune anyway in cleanup
fi

# Prune DB
RESPONSE=$(curl -s -X POST -H "Host: $HOST_HEADER" "$BASE_URL/admin/databases/prune/$TEST_DB_NAME")
if echo "$RESPONSE" | grep -q "\"message\":\"Database instance pruned successfully.\""; then
    echo "   ✅ Prune database successful."
else
    echo "   ❌ Prune database failed."
    echo "   Response: $RESPONSE"
    exit 1
fi

echo "=== All tests passed! ==="
exit 0