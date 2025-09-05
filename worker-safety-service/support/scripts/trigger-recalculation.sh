#!/bin/bash

# Check if the WS_API_URL environment variable is set
if [ -z "$WS_API_URL" ]; then
    echo "Error: The WS_API_URL environment variable is not set."
    exit 1
fi

# Check if the WS_GRAPHQL_ADMIN_TOKEN environment variable is set
if [ -z "$WS_GRAPHQL_ADMIN_TOKEN" ]; then
    echo "Error: The WS_GRAPHQL_ADMIN_TOKEN environment variable is not set."
    exit 1
fi

# Check if the trigger name is passed as a command-line argument
if [ -z "$1" ]; then
    echo "Error: The trigger name must be passed as a command-line argument."
    exit 1
fi

# URL to make the POST request to
url="${WS_API_URL}/graphql"
echo "URL: $url"
# Authorization header
authheader="Authorization: Bearer $WS_GRAPHQL_ADMIN_TOKEN"

# Trigger name
trigger=$1

# Read the UUIDs from standard input
while IFS= read -r uuid
do
    # JSON body of the POST request
    json_body=$(cat <<EOF
{
    "query": "mutation TriggerRecalculation { recalculate( recalculateInput: {trigger: $trigger, id: \"$uuid\"} )}",
    "operationName": "TriggerRecalculation"
}
EOF
)

    # Make the POST request
    curl --request POST \
        --url "$url" \
        --header "$authheader" \
        --header 'Content-Type: application/json' \
        --data "$json_body"
done
