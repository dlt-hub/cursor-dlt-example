# REST API Pagination Configuration

## Overview

When configuring pagination for REST API sources in dlt, it's important to use the correct paginator class rather than a dictionary configuration. This guide explains the proper way to configure pagination with examples.

## Paginator Classes

Import the appropriate paginator class from `dlt.sources.helpers.rest_client.paginators`. Available classes include:

- `JSONResponseCursorPaginator`: For cursor-based pagination where the cursor is in the JSON response
- `HeaderLinkPaginator`: For pagination based on Link headers
- `JSONLinkPaginator`: For pagination where the next URL is in the JSON response
- `OffsetPaginator`: For offset-based pagination
- `PageNumberPaginator`: For page number based pagination

## Example: Cursor-Based Pagination

```python
from dlt.sources.helpers.rest_client.paginators import JSONResponseCursorPaginator

# Complete configuration with pagination
rest_api_source({
    "client": {
        "base_url": "https://api.pipedrive.com/v1/",
        "auth": {
            "type": "api_key",
            "name": "api_token",
            "api_key": dlt.secrets["pipedrive_api_token"],
            "location": "query"
        },
        # Paginator configuration - defines how to get next page
        "paginator": JSONResponseCursorPaginator(
            cursor_path="additional_data.pagination.next_start",  # Path to next cursor value
            cursor_param="start"                                 # Query param name for cursor
        )
    },
    # Default configuration for all resources
    "resource_defaults": {
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "params": {
                "limit": 50  # Number of items per page - goes in endpoint params
            }
        }
    }
})
```

#### API Request Flow
```
GET /v1/deals?start=0&limit=50     # First page
GET /v1/deals?start=50&limit=50    # Second page
GET /v1/deals?start=100&limit=50   # Third page
```

### Configuration Structure Explained

1. Client Section (`client`):
   - Contains base configuration for the API client
   - Includes the paginator configuration that defines how to navigate pages
   - Parameters:
     - `cursor_path`: JSONPath to the next cursor value in the response
     - `cursor_param`: Query parameter name for the cursor

2. Resource Defaults Section (`resource_defaults`):
   - Contains default configuration applied to all resources
   - The `endpoint.params` section is where you put request parameters like:
     - Page size limits (`limit`)
     - Other API-specific parameters

3. Resources Section (`resources`):
   - Individual resource configurations
   - Can override defaults for specific endpoints
   - Can specify endpoint-specific pagination parameters

### Common Pagination Patterns

#### 1. Token-Based Cursor
Used by APIs that provide an opaque token for the next page.

```python
{
    "client": {
        "paginator": JSONResponseCursorPaginator(
            cursor_path="pagination.next_token",
            cursor_param="page_token"
        )
    },
    "resource_defaults": {
        "endpoint": {
            "params": {
                "page_size": 100  # Page size parameter goes here
            }
        }
    }
}
```

## Common Pagination Patterns

### 1. HubSpot-style Cursor Pagination
```python
JSONResponseCursorPaginator(
    cursor_path="paging.next.after",
    cursor_param="after"
)
```

### 2. Offset-based Pagination
```python
OffsetPaginator(
    offset_param="offset",
    limit_param="limit",
    limit=100
)
```

### 3. Page Number Pagination
```python
PageNumberPaginator(
    page_param="page",
    base_page=1
)
```

## Parameters by Paginator Type

### JSONResponseCursorPaginator
- `cursor_path`: JSONPath to the next cursor value in the response
- `cursor_param`: Query parameter name for the cursor
- `cursor_body_path`: (Optional) JSONPath for cursor in request body

### OffsetPaginator
- `offset_param`: Name of the offset parameter
- `limit_param`: Name of the limit parameter
- `limit`: Number of items per page
- `total_path`: (Optional) JSONPath to total count

### PageNumberPaginator
- `page_param`: Name of the page parameter
- `base_page`: Starting page number (usually 0 or 1)
- `total_path`: (Optional) JSONPath to total pages

## Best Practices

1. **Use Class Instances**: Always use paginator class instances rather than dictionary configurations.
2. **Verify Response Structure**: Ensure the cursor_path matches your API's response structure.
3. **Handle Rate Limits**: Consider using appropriate page sizes to avoid rate limits.
4. **Test Pagination**: Verify pagination works with small and large datasets.

## Troubleshooting

### Common Issues

1. **DictValidationException**
   - Cause: Using dictionary configuration instead of paginator class
   - Solution: Import and use appropriate paginator class

2. **Cursor Not Found**
   - Cause: Incorrect cursor_path
   - Solution: Verify API response structure and update path

3. **Invalid Page Size**
   - Cause: Page size exceeds API limits
   - Solution: Check API documentation for limits

The recents endpoint returns data in a nested structure:

```json
{
    "success": true,
    "data": [
        {
            "item": "deal",
            "id": 123,
            "data": {
                "id": 123,
                "update_time": "2024-01-01 12:00:00",
                // ... other fields
            }
        }
    ]
}
```

Configuration for this structure:
```python
{
    "name": "deals",
    "endpoint": {
        "path": "recents",
        "params": {
            "items": "deal"
        },
        "data_selector": "data",
        "incremental": {
            "start_param": "since_timestamp",      # Parameter name for the API
            "cursor_path": "data.update_time",     # Path to the timestamp in the response
            "initial_value": "2024-01-01 00:00:00" # Starting point for incremental loading
        }
    }
}
```

Key points:
1. `data_selector`: Specifies which part of the response contains the items
2. `cursor_path`: Must include the full path to the timestamp field, including any nested objects
3. `start_param`: The parameter name the API expects for filtering by timestamp
4. `initial_value`: The starting point for incremental loading, in the format expected by the API 