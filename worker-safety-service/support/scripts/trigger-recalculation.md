# Trigger Recalculation Script

This script is used to trigger a recalculation in the risk model. It does this by sending a POST request to the `/graphql` endpoint of the Worker Safety API to the `recalculate` mutation.

It reads a list of UUIDs from standard input and sends a POST request to a specified URL for each UUID. The type of recalculation to be triggered is specified as a command-line argument.

## Environment Variables

The script uses the following environment variables:

- `WS_API_URL`: The base URL of the server. The script will append `/graphql` to this base URL to construct the full URL for the POST requests.
- `WS_GRAPHQL_ADMIN_TOKEN`: The bearer token for authorization.

## Usage

Before running the script, make sure to set the `WS_API_URL` and `WS_GRAPHQL_ADMIN_TOKEN` environment variables. You can do this in the terminal with the `export` command:

```bash
export WS_API_URL="http://localhost:8001"
export WS_GRAPHQL_ADMIN_TOKEN="your_token_here"
```

### Running the Script with a List of UUIDs
To run the script, pass the trigger name as a command-line argument and pipe in a list of UUIDs. For example:

```bash
echo -e "123e4567-e89b-12d3-a456-426614174000\n123e4567-e89b-12d3-a456-426614174001" | ./trigger-recalculation.sh LIBRARY_TASK_DATA_CHANGED
```

### Running the Script with a File of UUIDs

If you have a file with a list of UUIDs, you can use the `cat` command to pass them to the script. Each UUID should be on a separate line. Here's an example:

```bash
cat uuids.txt | ./trigger-recalculation.sh LIBRARY_TASK_DATA_CHANGED
```

### Recalculation Trigger Names
Valid trigger names correspond to the [`Triggers`](../worker_safety_service/risk_model/triggers/__init__.py#L30) enum in the `RecalculateInput` type in the `recalculate` mutation. 
