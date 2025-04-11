# REST API Pagination Guide

## Table of Contents
1. [Overview](#overview)
2. [Paginator Classes](#paginator-classes)
3. [Configuration Examples](#configuration-examples)
4. [Common Pagination Patterns](#common-pagination-patterns)
5. [Parameters by Paginator Type](#parameters-by-paginator-type)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

When configuring pagination for REST API sources in dlt, it's important to use the correct paginator class rather than a dictionary configuration. This guide explains the proper way to configure pagination with examples.

## Paginator Classes

Import the appropriate paginator class from `dlt.sources.helpers.rest_client.paginators`:

```python
from dlt.sources.helpers.rest_client.paginators import (
    JSONResponseCursorPaginator,
    HeaderLinkPaginator,
    JSONLinkPaginator,
    OffsetPaginator,
    PageNumberPaginator
)
```

### Available Classes:
- `JSONResponseCursorPaginator`: For cursor-based pagination where the cursor is in the JSON response
- `HeaderLinkPaginator`: For pagination based on Link headers
- `JSONLinkPaginator`: For pagination where the next URL is in the JSON response
- `OffsetPaginator`: For offset-based pagination
- `PageNumberPaginator`: For page number based pagination

## Configuration Examples

### 1. Cursor-Based Pagination (JSON Response)
```python
from dlt.sources.helpers.rest_client.paginators import JSONResponseCursorPaginator

source = rest_api_source({
    "client": {
        "base_url": "https://api.pipedrive.com/v1/",
        "auth": {
            "type": "api_key",
            "name": "api_token",
            "api_key": dlt.secrets["pipedrive_api_token"],
            "location": "query"
        },
        "paginator": JSONResponseCursorPaginator(
            cursor_path="additional_data.pagination.next_start",  # Path to next cursor value
            cursor_param="start"                                 # Query param name for cursor
        )
    },
    "resource_defaults": {
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "params": {
                "limit": 50  # Number of items per page
            }
        }
    }
})
```

### 2. Header-Based Pagination (GitHub Style)
```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.github.com/",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["github_token"]
        },
        "paginator": HeaderLinkPaginator(
            link_header="Link",    # Header containing pagination links
            rel="next"             # Relation type for next page
        )
    }
})
```

### 3. Offset-Based Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": OffsetPaginator(
            offset_param="offset",     # Parameter name for offset
            limit_param="limit",       # Parameter name for limit
            limit=100,                 # Items per page
            total_path="meta.total"    # Optional: path to total count
        )
    }
})
```

### 4. Page Number Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": PageNumberPaginator(
            page_param="page",         # Parameter name for page number
            base_page=1,               # Starting page number (0 or 1)
            total_path="meta.pages"    # Optional: path to total pages
        )
    }
})
```

### 5. JSON Link Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": JSONLinkPaginator(
            link_path="meta.next_url"  # Path to next page URL in response
        )
    }
})
```

## Common Pagination Patterns

### 1. HubSpot-style Cursor Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": JSONResponseCursorPaginator(
            cursor_path="paging.next.after",
            cursor_param="after"
        )
    }
})

# API Request Flow Example:
# GET /v1/contacts?after=null&limit=100     # First page
# GET /v1/contacts?after=cursor1&limit=100  # Second page
# GET /v1/contacts?after=cursor2&limit=100  # Third page
```

### 2. GitHub-style Link Header Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": HeaderLinkPaginator(
            link_header="Link",
            rel="next"
        )
    }
})

# Response Headers Example:
# Link: <https://api.github.com/repos/owner/repo/issues?page=2>; rel="next"
```

### 3. Stripe-style Cursor Pagination
```python
source = rest_api_source({
    "client": {
        "paginator": JSONResponseCursorPaginator(
            cursor_path="data.next_cursor",
            cursor_param="starting_after"
        )
    }
})
```

## Parameters by Paginator Type

### JSONResponseCursorPaginator
```python
JSONResponseCursorPaginator(
    cursor_path="",      # JSONPath to the next cursor value
    cursor_param="",     # Query parameter name for cursor
    cursor_body_path=""  # Optional: JSONPath for cursor in request body
)
```

### HeaderLinkPaginator
```python
HeaderLinkPaginator(
    link_header="Link",  # Header containing pagination links
    rel="next"          # Relation type for next page
)
```

### OffsetPaginator
```python
OffsetPaginator(
    offset_param="",    # Name of the offset parameter
    limit_param="",     # Name of the limit parameter
    limit=100,          # Number of items per page
    total_path=""       # Optional: JSONPath to total count
)
```

### PageNumberPaginator
```python
PageNumberPaginator(
    page_param="",      # Name of the page parameter
    base_page=1,        # Starting page number (0 or 1)
    total_path=""       # Optional: JSONPath to total pages
)
```

### JSONLinkPaginator
```python
JSONLinkPaginator(
    link_path=""        # JSONPath to next page URL
)
```

## Best Practices

1. **Use Class Instances**:
   - Always use paginator class instances rather than dictionary configurations
   - Import the correct paginator class for your API's pagination style

2. **Verify Response Structure**:
   - Ensure the cursor_path matches your API's response structure
   - Test pagination with small datasets first
   - Verify all pagination parameters work as expected

3. **Handle Rate Limits**:
   - Set appropriate page sizes to avoid rate limits
   - Implement backoff strategies when needed
   - Monitor API usage during pagination

4. **Error Handling**:
   - Implement proper error handling for pagination failures
   - Handle edge cases (last page, empty responses)
   - Log pagination progress

## Troubleshooting

### Common Issues

1. **DictValidationException**
   ```python
   # Wrong: Dictionary configuration
   "paginator": {
       "type": "cursor",
       "cursor_path": "meta.next"
   }

   # Correct: Class instance
   "paginator": JSONResponseCursorPaginator(
       cursor_path="meta.next",
       cursor_param="cursor"
   )
   ```

2. **Cursor Not Found**
   ```python
   # Problem: Incorrect cursor path
   cursor_path="data.pagination.next"

   # Solution: Verify exact path in response
   cursor_path="meta.pagination.next_cursor"
   ```

3. **Invalid Page Size**
   ```python
   # Problem: Page size too large
   "params": {"limit": 1000}

   # Solution: Check API limits
   "params": {"limit": 100}
   ```

### Debugging Tips

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Verify Response Structure**:
   ```python
   def verify_pagination(response):
       print("Response structure:", response.json())
       print("Headers:", response.headers)
       return response
   ```

3. **Test Pagination Flow**:
   ```python
   # Add pagination verification
   def test_pagination():
       pipeline = dlt.pipeline(...)
       info = pipeline.run(source)
       assert info.load_packages > 1  # Verify multiple pages loaded
   ```

Remember to:
- Test pagination with small datasets first
- Verify response structures match your configuration
- Monitor rate limits and API usage
- Implement proper error handling
- Document pagination configuration 