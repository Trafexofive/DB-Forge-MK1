#!/bin/bash

# client.sh: Simplified CLI for Praetorian DB-Forge API interactions

BASE_URL="http://db.localhost:8081" # Updated to match Traefik's mapped port
API_KEY="${DB_FORGE_API_KEY:-}"   # Default to environment variable, if set

# --- Helper Function for API Calls ---
_call_api() {
    local METHOD=$1
    local ENDPOINT=$2
    local JSON_PAYLOAD_FILE=$3

    local URL="${BASE_URL}${ENDPOINT}"
    local CURL_CMD="curl -s -X $METHOD -H \"Host: db.localhost\""

    # Add API Key header if API_KEY is set
    if [ -n "$API_KEY" ]; then
        CURL_CMD+=" -H \"X-API-Key: $API_KEY\""
    fi

    if [ -n "$JSON_PAYLOAD_FILE" ]; then
        if [ ! -f "$JSON_PAYLOAD_FILE" ]; then
            echo "Error: JSON payload file not found: $JSON_PAYLOAD_FILE" >&2
            return 1
        fi
        CURL_CMD+=" -H \"Content-Type: application/json\" -d \"@$JSON_PAYLOAD_FILE\""
    fi
    CURL_CMD+=" \"$URL\""

    eval "$CURL_CMD"
}

# --- User-Friendly Commands ---

# Utility command to test if the API key is valid
test_auth() {
    if [ -z "$API_KEY" ]; then
        echo "Error: API key not set. Please set DB_FORGE_API_KEY environment variable or use --api-key option." >&2
        return 1
    fi
    echo "Testing authentication with provided API key..."
    local response=$(_call_api "GET" "/admin/databases")
    if echo "$response" | grep -q '"error"'; then
        echo "Authentication failed."
        echo "$response"
        return 1
    else
        echo "Authentication successful!"
        echo "$response" | jq . || echo "$response" # Pretty print JSON if jq is available
    fi
}

# Admin API
spawn_db() {
    local db_name=$1
    if [ -z "$db_name" ]; then
        echo "Usage: client.sh spawn_db <db_name>" >&2
        return 1
    fi
    _call_api "POST" "/admin/databases/spawn/$db_name"
}

prune_db() {
    local db_name=$1
    if [ -z "$db_name" ]; then
        echo "Usage: client.sh prune_db <db_name>" >&2
        return 1
    fi
    _call_api "POST" "/admin/databases/prune/$db_name"
}

list_dbs() {
    _call_api "GET" "/admin/databases"
}

get_root() {
    _call_api "GET" "/"
}

# Data Plane API (simplified examples)
# For complex queries, users might still need to provide JSON files or use raw_query
create_table() {
    local db_name=$1
    local table_name=$2
    local columns_json_file=$3 # Path to a JSON file defining columns

    if [ -z "$db_name" ] || [ -z "$table_name" ] || [ -z "$columns_json_file" ]; then
        echo "Usage: client.sh create_table <db_name> <table_name> <columns_json_file>" >&2
        return 1
    fi
    _call_api "POST" "/api/db/$db_name/tables" "$columns_json_file"
}

insert_rows() {
    local db_name=$1
    local table_name=$2
    local rows_json_file=$3 # Path to a JSON file defining rows

    if [ -z "$db_name" ] || [ -z "$table_name" ] || [ -z "$rows_json_file" ]; then
        echo "Usage: client.sh insert_rows <db_name> <table_name> <rows_json_file>" >&2
        return 1
    fi
    _call_api "POST" "/api/db/$db_name/tables/$table_name/rows" "$rows_json_file"
}

get_rows() {
    local db_name=$1
    local table_name=$2
    local query_params=$3 # e.g., "status=pending&user=alice"

    if [ -z "$db_name" ] || [ -z "$table_name" ]; then
        echo "Usage: client.sh get_rows <db_name> <table_name> [query_params]" >&2
        return 1
    fi
    local ENDPOINT="/api/db/$db_name/tables/$table_name/rows"
    if [ -n "$query_params" ]; then
        ENDPOINT+="?$query_params"
    fi
    _call_api "GET" "$ENDPOINT"
}

raw_query() {
    local db_name=$1
    local query_json_file=$2 # Path to a JSON file defining the query and params

    if [ -z "$db_name" ] || [ -z "$query_json_file" ]; then
        echo "Usage: client.sh raw_query <db_name> <query_json_file>" >&2
        return 1
    fi
    _call_api "POST" "/api/db/$db_name/query" "$query_json_file"
}

# --- Main execution ---
# Parse command-line options for API key
TEMP=$(getopt -o k: --long api-key: -n 'client.sh' -- "$@")
if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi
eval set -- "$TEMP"

while true ; do
    case "$1" in
        -k|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        --) shift ; break ;;
        *) echo "Internal error!" ; exit 1 ;;
    esac
done

# If no command is given, show usage
if [ $# -lt 1 ]; then
    echo "Usage: client.sh [options] <command> [arguments]"
    echo "Options:"
    echo "  -k, --api-key <key>  Specify the API key to use for authentication"
    echo "                       Can also be set via DB_FORGE_API_KEY environment variable"
    echo "Commands:"
    echo "  Utility:"
    echo "    test_auth             Test if the provided API key is valid"
    echo "  Admin API:"
    echo "    spawn_db <db_name>"
    echo "    prune_db <db_name>"
    echo "    list_dbs"
    echo "    get_root"
    echo "  Data Plane API:"
    echo "    create_table <db_name> <table_name> <columns_json_file>"
    echo "    insert_rows <db_name> <table_name> <rows_json_file>"
    echo "    get_rows <db_name> <table_name> [query_params]"
    echo "    raw_query <db_name> <query_json_file>"
    exit 1
fi

COMMAND=$1
shift

case "$COMMAND" in
    test_auth|spawn_db|prune_db|list_dbs|get_root|create_table|insert_rows|get_rows|raw_query)
        "$COMMAND" "$@"
        ;;
    *)
        echo "Unknown command: $COMMAND" >&2
        exit 1
        ;;
esac