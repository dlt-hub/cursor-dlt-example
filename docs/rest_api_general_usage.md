# REST API Source Documentation for LLMs (Enhanced)

## Table of Contents
1. [Overview](#overview)
2. [Quick Start Example](#quick-start-example)
3. [Client Configuration](#client-configuration)
4. [Pagination Methods](#pagination-methods)
5. [Resource Configuration](#resource-configuration)
6. [Dependent Resources](#dependent-resources)
7. [Authentication](#authentication)
8. [Data Selection and Processing](#data-selection-and-processing)
9. [Rate Limiting and Backoff](#rate-limiting-and-backoff)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Testing](#testing)

## Overview

The REST API source extracts JSON data from RESTful APIs using declarative configurations. This documentation combines best practices and configuration approaches for building robust REST API pipelines, with special attention to dependent resources and testing.

[Previous sections unchanged up to Resource Configuration...]

## Dependent Resources

### 1. Parent-Child Relationships
Configure resources that depend on data from other resources:

```python
"resources": [
    {
        "name": "organizations",
        "endpoint": {
            "path": "v1/organizations",
            "data_selector": "data.*"
        }
    },
    {
        "name": "repositories",
        "endpoint": {
            "path": "v1/organizations/{resources.organizations.id}/repositories",
            "data_selector": "data.*",
            "depends_on": ["organizations"],
            "parameters": {
                "org_id": "{resources.organizations.id}"
            }
        }
    },
    {
        "name": "issues",
        "endpoint": {
            "path": "v1/repositories/{resources.repositories.id}/issues",
            "data_selector": "data.*",
            "depends_on": ["repositories"],
            "parameters": {
                "repo_id": "{resources.repositories.id}"
            }
        }
    }
]
```

### 2. Complex Dependencies
Handle multiple dependency levels and conditional loading:

```python
{
    "name": "comments",
    "endpoint": {
        "path": "v1/issues/{resources.issues.id}/comments",
        "depends_on": ["issues"],
        "parameters": {
            "issue_id": "{resources.issues.id}"
        },
        "load_condition": "lambda issue: issue.get('comments_count', 0) > 0"
    }
}
```

### 3. Dependency Configuration Options
```python
"endpoint": {
    "depends_on": {
        "resources": ["parent_resource"],
        "mode": "sequential",  # or "parallel"
        "batch_size": 10,     # Number of parent items to process at once
        "max_retries": 3      # Retries for dependent resource failures
    }
}
```

### 4. Resource State Management
```python
"endpoint": {
    "state_management": {
        "store_state": True,
        "state_key": "last_processed_id",
        "resume_from_state": True
    }
}
```

## Rate Limiting and Backoff

### 1. Basic Rate Limiting
```python
"client": {
    "rate_limit": {
        "calls": 100,
        "period": 60  # seconds
    }
}
```

### 2. Advanced Rate Limiting
```python
"client": {
    "rate_limit": {
        "strategy": "adaptive",
        "initial_calls": 100,
        "period": 60,
        "backoff_factor": 2,
        "max_retries": 5,
        "retry_statuses": [429, 503]
    }
}
```

### 3. Resource-Specific Rate Limits
```python
"resources": [
    {
        "name": "high_priority",
        "endpoint": {
            "rate_limit": {
                "calls": 200,
                "period": 60
            }
        }
    },
    {
        "name": "low_priority",
        "endpoint": {
            "rate_limit": {
                "calls": 50,
                "period": 60
            }
        }
    }
]
```

## Testing

### 1. Mock Response Testing
```python
import pytest
from unittest.mock import patch

def test_api_pagination():
    mock_responses = [
        {"data": [{"id": 1}], "next_cursor": "cursor1"},
        {"data": [{"id": 2}], "next_cursor": None}
    ]
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = [
            type('Response', (), {'json': lambda: r, 'status_code': 200})
            for r in mock_responses
        ]
        
        pipeline = dlt.pipeline(...)
        info = pipeline.run(source)
        assert info.load_packages == 2
```

### 2. Dependency Chain Testing
```python
@pytest.fixture
def mock_dependent_responses():
    return {
        "organizations": [{"id": 1, "name": "Org1"}],
        "repositories": [{"id": 101, "org_id": 1}],
        "issues": [{"id": 201, "repo_id": 101}]
    }

def test_dependent_resources(mock_dependent_responses):
    with patch('requests.get') as mock_get:
        def mock_response(url):
            if "organizations" in url:
                data = mock_dependent_responses["organizations"]
            elif "repositories" in url:
                data = mock_dependent_responses["repositories"]
            elif "issues" in url:
                data = mock_dependent_responses["issues"]
            return type('Response', (), {
                'json': lambda: {"data": data},
                'status_code': 200
            })
        
        mock_get.side_effect = mock_response
        pipeline = dlt.pipeline(...)
        info = pipeline.run(source)
        # Add assertions
```

### 3. Error Handling Tests
```python
def test_rate_limit_handling():
    responses = [
        type('Response', (), {
            'status_code': 429,
            'headers': {'Retry-After': '60'}
        }),
        type('Response', (), {
            'json': lambda: {"data": [{"id": 1}]},
            'status_code': 200
        })
    ]
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = responses
        pipeline = dlt.pipeline(...)
        info = pipeline.run(source)
        # Verify rate limit handling
```

### 4. Integration Tests
```python
def test_full_pipeline_integration():
    # Configure test credentials
    dlt.secrets.update({
        "api_token": "test_token",
        "base_url": "http://test-api.example.com"
    })
    
    # Run pipeline with test configuration
    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline",
        destination="duckdb",
        dataset_name="test_dataset"
    )
    
    source = rest_api_source({
        # Test configuration
    })
    
    info = pipeline.run(source)
    # Verify pipeline execution
```

## Best Practices (Additional)

1. **Dependent Resource Management**:
   - Use appropriate dependency modes (sequential/parallel)
   - Implement proper error handling for dependency chains
   - Consider resource state management for long-running processes

2. **Testing Strategy**:
   - Create comprehensive mock responses
   - Test all pagination scenarios
   - Verify dependency chain behavior
   - Test error handling and recovery

3. **Rate Limit Handling**:
   - Implement adaptive rate limiting
   - Use appropriate backoff strategies
   - Monitor API usage patterns

4. **Resource Optimization**:
   - Batch dependent resource requests when possible
   - Use conditional loading to minimize API calls
   - Implement proper state management for resumability

## Troubleshooting (Additional)

6. **Dependency Chain Issues**:
   - Verify dependency configuration
   - Check parameter interpolation
   - Monitor dependency execution order

7. **Rate Limit Exceeded**:
   - Review rate limit configuration
   - Check backoff strategy
   - Monitor API usage patterns

8. **State Management Problems**:
   - Verify state storage configuration
   - Check state keys and values
   - Monitor state persistence

Remember to:
- Test dependency chains thoroughly
- Monitor rate limit compliance
- Implement proper error handling
- look into incremental strategies and how they can be implemented
- Maintain state for long-running processes 