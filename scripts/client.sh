#!/bin/bash

# client.sh: A simple curl wrapper for the DB Gateway API
# Usage: client.sh <METHOD> <ENDPOINT> [JSON_PAYLOAD_FILE]

METHOD=$1
ENDPOINT=$2
JSON_PAYLOAD_FILE=$3

BASE_URL="http://db.localhost" # Exposed via Traefik

if [ -z "$METHOD" ] || [ -z "$ENDPOINT" ]; then
    echo "Usage: $0 <METHOD> <ENDPOINT> [JSON_PAYLOAD_FILE]"
    exit 1
fi

URL="${BASE_URL}${ENDPOINT}"

if [ -n "$JSON_PAYLOAD_FILE" ]; then
    if [ ! -f "$JSON_PAYLOAD_FILE" ]; then
        echo "Error: JSON payload file not found: $JSON_PAYLOAD_FILE"
        exit 1
    fi
    curl -s -X "$METHOD" -H "Content-Type: application/json" -d "@$JSON_PAYLOAD_FILE" "$URL"
else
    curl -s -X "$METHOD" "$URL"
fi