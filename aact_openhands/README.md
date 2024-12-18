# AACT OpenHands Action Endpoint

This document describes the usage of the action endpoint in the AACT OpenHands server.

## Overview

The `/action` endpoint accepts POST requests with JSON payloads that define agent actions. It allows you to execute various actions like browsing URLs, running commands, and file operations.

## Endpoint Details
- **URL**: `http://localhost:5000/action`
- **Method**: `POST`
- **Content-Type**: `application/json`

## Request Format
```json
{
    "agent_name": "string",
    "action_type": "string",
    "argument": "string",
    "path": "string (optional)"
}
```

## Supported Action Types

The server supports the following action types:

1. **Browse Action** (`browse`)
   - Used for navigating to URLs
   - Requires `argument` field containing the URL
```bash
curl -X POST http://localhost:5000/action \
-H "Content-Type: application/json" \
-d '{
    "agent_name": "assistant",
    "action_type": "browse",
    "argument": "https://example.com"
}'
```

```python
response = requests.post(
    "http://localhost:5000/action",
    json={
        "agent_name": "assistant",
        "action_type": "browse",
        "argument": "https://example.com"
    }
)
print(response.json())
```

2. **Interactive Browse Action** (`browse_action`)
   - Used for browser interactions
   - Requires `argument` field containing browser actions
```bash
curl -X POST http://localhost:5000/action \
-H "Content-Type: application/json" \
-d '{
    "agent_name": "assistant",
    "action_type": "browse_action",
    "argument": "click .button-class"
}'
```

```python
response = requests.post(
    "http://localhost:5000/action",
    json={
        "agent_name": "assistant",
        "action_type": "browse_action",
        "argument": "click .button-class"
    }
)
print(response.json())
```

3. **Run Command Action** (`run`)
   - Used for executing shell commands
   - Requires `argument` field containing the command
```bash
curl -X POST http://localhost:5000/action \
-H "Content-Type: application/json" \
-d '{
    "agent_name": "assistant",
    "action_type": "run",
    "argument": "ls -la"
}'
```

```python
response = requests.post(
    "http://localhost:5000/action",
    json={
        "agent_name": "assistant",
        "action_type": "run",
        "argument": "ls -la"
    }
)
print(response.json())
```

4. **Read File Action** (`read`)
   - Used for reading file contents
   - Requires both `path` and `argument` fields
```bash
curl -X POST http://localhost:5000/action \
-H "Content-Type: application/json" \
-d '{
    "agent_name": "assistant",
    "action_type": "read",
    "argument": "Reading file",
    "path": "/path/to/file.txt"
}'
```

```python
response = requests.post(
    "http://localhost:5000/action",
    json={
        "agent_name": "assistant",
        "action_type": "read",
        "argument": "Reading file",
        "path": "/path/to/file.txt"
    }
)
print(response.json())
```

5. **Write File Action** (`write`)
   - Used for writing to files
   - Requires both `path` and `argument` fields
   - The `argument` field contains the content to write
```bash
curl -X POST http://localhost:5000/action \
-H "Content-Type: application/json" \
-d '{
    "agent_name": "assistant",
    "action_type": "write",
    "argument": "Content to write",
    "path": "/path/to/file.txt"
}'
```

```python
response = requests.post(
    "http://localhost:5000/action",
    json={
        "agent_name": "assistant",
        "action_type": "write",
        "argument": "Content to write",
        "path": "/path/to/file.txt"
    }
)
print(response.json())
```

## Helper Function
For convenience, you can use this helper function to make requests:

```python
import requests
from typing import Optional

def make_action_request(
    agent_name: str,
    action_type: str,
    argument: str,
    path: Optional[str] = None
) -> dict:
    """
    Make a request to the action endpoint.
    
    Args:
        agent_name: Name of the agent making the request
        action_type: Type of action (browse, browse_action, run, read, write)
        argument: The main argument for the action (URL, command, content)
        path: Required for read and write actions
        
    Returns:
        dict: The JSON response from the server
    """
    payload = {
        "agent_name": agent_name,
        "action_type": action_type,
        "argument": argument
    }
    
    if path is not None:
        payload["path"] = path
        
    response = requests.post(
        "http://localhost:5000/action",
        json=payload
    )
    return response.json()

# Example usage:
result = make_action_request(
    agent_name="assistant",
    action_type="browse",
    argument="https://example.com"
)
print(result)
```

## Response Format

The endpoint returns a JSON response with the following structure:

```json
{
    "status": "success",
    "action_type": "string",
    "result": "string"
}
```

## Error Responses

If there's an error, the response will include an error message:

```json
{
    "status": "error",
    "error": "Error description"
}
```

Common error cases:
- Invalid action type (must be one of: browse, browse_action, run, read, write)
- Missing required fields (path is required for read/write actions)
- Runtime not available (503 error)
- Server processing errors (500 error)

## Notes
- The `path` field is required for `read` and `write` actions
- All action types are case-sensitive and should be lowercase
- The server processes one action at a time
- The response includes a string representation of the action object
``` 