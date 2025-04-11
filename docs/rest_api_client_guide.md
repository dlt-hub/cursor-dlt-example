# REST API Client Guide

## Table of Contents
1. [Overview](#overview)
2. [Client Configuration](#client-configuration)
3. [Authentication Methods](#authentication-methods)
4. [Request Customization](#request-customization)
5. [Response Handling](#response-handling)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Pagination](#pagination)
10. [Advanced OAuth2 Implementation](#advanced-oauth2-implementation)
11. [Response Hooks and Custom Handlers](#response-hooks-and-custom-handlers)

## Overview

The dlt REST API client provides a robust way to interact with REST APIs, handling authentication, request customization, and response processing. This guide covers all aspects of configuring and using the REST client effectively.

## Client Configuration

### Basic Client Setup
```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/v1/",
        "headers": {
            "Accept": "application/json",
            "User-Agent": "dlt-client/1.0"
        },
        "verify_ssl": True,
        "timeout": 30
    }
})
```

### Advanced Configuration
```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/v1/",
        "request_config": {
            "allow_redirects": True,
            "proxies": {
                "http": "http://proxy.example.com:8080",
                "https": "https://proxy.example.com:8080"
            },
            "cert": "/path/to/cert.pem",
            "timeout": (5, 30)  # (connect timeout, read timeout)
        }
    }
})
```

## Authentication Methods

### 1. API Key Authentication
```python
source = rest_api_source({
    "client": {
        "auth": {
            "type": "api_key",
            "name": "api_key",
            "api_key": dlt.secrets["api_key"],
            "location": "query"  # or "header"
        }
    }
})
```

### 2. Bearer Token Authentication
```python
source = rest_api_source({
    "client": {
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["bearer_token"]
        }
    }
})
```

### 3. Basic Authentication
```python
source = rest_api_source({
    "client": {
        "auth": {
            "type": "basic",
            "username": dlt.secrets["username"],
            "password": dlt.secrets["password"]
        }
    }
})
```

### 4. OAuth2 Authentication
```python
source = rest_api_source({
    "client": {
        "auth": {
            "type": "oauth2",
            "token_url": "https://auth.example.com/oauth/token",
            "client_id": dlt.secrets["client_id"],
            "client_secret": dlt.secrets["client_secret"],
            "scopes": ["read", "write"]
        }
    }
})
```

### 5. Custom Authentication
```python
from dlt.sources.helpers.rest_client.auth import BaseAuthenticator

class CustomAuthenticator(BaseAuthenticator):
    def __init__(self, custom_token):
        self.custom_token = custom_token

    def apply_auth(self, request):
        request.headers["X-Custom-Auth"] = self.custom_token
        return request

source = rest_api_source({
    "client": {
        "auth": CustomAuthenticator(dlt.secrets["custom_token"])
    }
})
```

## Request Customization

### 1. Headers Configuration
```python
source = rest_api_source({
    "client": {
        "headers": {
            "Accept": "application/json",
            "X-API-Version": "2.0",
            "Custom-Header": "{resources.custom_value}"  # Dynamic header
        }
    }
})
```

### 2. Query Parameters
```python
source = rest_api_source({
    "resources": [
        {
            "name": "items",
            "endpoint": {
                "path": "items",
                "params": {
                    "fields": "id,name,created_at",
                    "filter": "status=active",
                    "sort": "-created_at"
                }
            }
        }
    ]
})
```

### 3. Request Body
```python
source = rest_api_source({
    "resources": [
        {
            "name": "search_items",
            "endpoint": {
                "path": "search",
                "method": "POST",
                "json": {
                    "query": "status:active",
                    "filters": {
                        "date_range": {
                            "start": "{start_date}",
                            "end": "{end_date}"
                        }
                    }
                }
            }
        }
    ]
})
```

## Response Handling

### 1. Data Selection
```python
source = rest_api_source({
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "data_selector": "data.items.*",  # JSONPath selector
                "response_handlers": [
                    {
                        "type": "json_response",
                        "selector": "data.items.*"
                    }
                ]
            }
        }
    ]
})
```

### 2. Response Transformation
```python
def transform_response(response_data):
    """Custom response transformation"""
    return [
        {
            "id": item["id"],
            "full_name": f"{item['first_name']} {item['last_name']}",
            "active": item["status"] == "active"
        }
        for item in response_data["data"]["items"]
    ]

source = rest_api_source({
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "transform": transform_response
            }
        }
    ]
})
```

### 3. Response Validation
```python
def validate_response(response):
    """Custom response validation"""
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            raise ValueError(f"API returned errors: {data['errors']}")
    return response

source = rest_api_source({
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "response_handlers": [
                    {
                        "type": "validator",
                        "function": validate_response
                    }
                ]
            }
        }
    ]
})
```

## Error Handling

### 1. Retry Configuration
```python
source = rest_api_source({
    "client": {
        "retry_config": {
            "max_retries": 3,
            "retry_statuses": [429, 503],
            "retry_methods": ["GET", "HEAD"],
            "backoff_factor": 2,
            "backoff_max": 60
        }
    }
})
```

### 2. Custom Error Handling
```python
def handle_error(response):
    """Custom error handler"""
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
        return True  # Retry the request
    return False  # Don't retry

source = rest_api_source({
    "client": {
        "error_handlers": [
            {
                "type": "custom",
                "function": handle_error
            }
        ]
    }
})
```

## Best Practices

1. **Security**:
   - Always use environment variables or secrets management for sensitive data
   - Implement proper SSL verification
   - Use appropriate authentication methods

2. **Performance**:
   - Configure appropriate timeouts
   - Implement retry mechanisms with exponential backoff
   - Use connection pooling for multiple requests

3. **Error Handling**:
   - Implement comprehensive error handling
   - Log failed requests appropriately
   - Use proper status code handling

4. **Request Management**:
   - Use appropriate HTTP methods
   - Implement proper header management
   - Handle rate limiting appropriately

## Troubleshooting

### Common Issues

1. **Authentication Failures**
```python
# Problem: Incorrect auth configuration
"auth": {
    "type": "bearer",
    "token": "invalid_token"
}

# Solution: Use proper secret management
"auth": {
    "type": "bearer",
    "token": dlt.secrets["bearer_token"]
}
```

2. **Timeout Issues**
```python
# Problem: Default timeout too short
"timeout": 5

# Solution: Configure appropriate timeouts
"timeout": {
    "connect": 5,
    "read": 30
}
```

3. **SSL Verification Issues**
```python
# Problem: SSL verification failing
"verify_ssl": False  # UNSAFE

# Solution: Provide proper cert
"verify_ssl": "/path/to/cert.pem"
```

### Debugging Tips

1. **Enable Request Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
```

2. **Request Inspection**
```python
def inspect_request(request):
    print(f"URL: {request.url}")
    print(f"Method: {request.method}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.body}")
    return request

source = rest_api_source({
    "client": {
        "request_hooks": [inspect_request]
    }
})
```

Remember to:
- Always use secure authentication methods
- Implement proper error handling
- Configure appropriate timeouts and retries
- Monitor API usage and rate limits
- Document client configuration
- Test with small datasets first 

## Pagination

### Built-in Paginators
1. JSONLinkPaginator
2. HeaderLinkPaginator
3. OffsetPaginator
4. PageNumberPaginator
5. JSONResponseCursorPaginator
6. HeaderCursorPaginator

### Custom Pagination
[Examples from restclient.md]

## Advanced OAuth2 Implementation
[Details from restclient.md]

## Response Hooks and Custom Handlers
[Examples from restclient.md] 