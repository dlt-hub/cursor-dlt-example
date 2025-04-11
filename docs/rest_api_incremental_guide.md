# DLT Incremental Extract and Load Guide for REST APIs

## Table of Contents
1. [Overview](#overview)
2. [Incremental Loading Patterns](#incremental-loading-patterns)
3. [Configuration Examples](#configuration-examples)
4. [State Management](#state-management)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

Incremental extract and load (E&L) in dlt allows you to efficiently process only new or updated data from REST APIs. This approach reduces API calls, processing time, and resource usage by tracking and loading only changed data since the last run.

## Incremental Loading Patterns

### 1. Timestamp-Based Incremental Loading
Best for APIs that provide update timestamps:

```python
import dlt
from dlt.sources.rest_api import rest_api_source
from datetime import datetime, timedelta

# Configure source with timestamp-based incremental loading
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/v1/",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["api_token"]
        }
    },
    "resources": [
        {
            "name": "updated_records",
            "endpoint": {
                "path": "records",
                "incremental": {
                    "start_param": "updated_since",        # API parameter for filtering
                    "cursor_path": "data.last_updated",    # Path to timestamp in response
                    "initial_value": "2024-01-01T00:00:00Z",
                    "date_format": "%Y-%m-%dT%H:%M:%SZ"   # Format of timestamps
                }
            }
        }
    ]
})
```

### 2. ID-Based Incremental Loading
For APIs that use sequential IDs:

```python
source = rest_api_source({
    "resources": [
        {
            "name": "records_by_id",
            "endpoint": {
                "path": "records",
                "incremental": {
                    "start_param": "min_id",
                    "cursor_path": "data.id",
                    "initial_value": 0,
                    "type": "integer"
                }
            }
        }
    ]
})
```

### 3. Cursor-Based Incremental Loading
For APIs using opaque cursors:

```python
source = rest_api_source({
    "resources": [
        {
            "name": "cursor_based_records",
            "endpoint": {
                "path": "records",
                "incremental": {
                    "cursor_path": "meta.next_cursor",
                    "start_param": "cursor",
                    "initial_value": None,
                    "type": "string"
                }
            }
        }
    ]
})
```

## Configuration Examples

### 1. Complete Example with Multiple Resources

```python
source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/v1/",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["api_token"]
        }
    },
    "resource_defaults": {
        "write_disposition": "merge",
        "primary_key": "id"
    },
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "incremental": {
                    "start_param": "modified_after",
                    "cursor_path": "modified_at",
                    "initial_value": "2024-01-01T00:00:00Z"
                }
            }
        },
        {
            "name": "orders",
            "endpoint": {
                "path": "orders",
                "incremental": {
                    "start_param": "min_order_id",
                    "cursor_path": "data.order_id",
                    "initial_value": 0,
                    "type": "integer"
                }
            }
        }
    ]
})
```

### 2. Incremental Loading with Custom Processing

```python
def process_timestamp(timestamp_str):
    """Convert API timestamp to standard format"""
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

source = rest_api_source({
    "resources": [
        {
            "name": "events",
            "endpoint": {
                "path": "events",
                "incremental": {
                    "start_param": "from_time",
                    "cursor_path": "data.event_time",
                    "initial_value": "2024-01-01T00:00:00Z",
                    "value_transform": process_timestamp
                }
            }
        }
    ]
})
```

## State Management

### 1. Basic State Storage

```python
pipeline = dlt.pipeline(
    pipeline_name="incremental_api",
    destination="duckdb",
    dataset_name="api_data"
)

# Run pipeline with state management
info = pipeline.run(source, write_disposition="merge")

# Access state information
current_state = info.load_state
print(f"Last processed timestamp: {current_state.get('events.last_value')}")
```

### 2. Custom State Management

```python
from datetime import datetime, timedelta

def get_initial_state():
    """Calculate initial state based on business logic"""
    start_date = datetime.now() - timedelta(days=30)
    return start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

source = rest_api_source({
    "resources": [
        {
            "name": "transactions",
            "endpoint": {
                "path": "transactions",
                "incremental": {
                    "start_param": "start_time",
                    "cursor_path": "data.transaction_time",
                    "initial_value": get_initial_state(),
                    "state_management": {
                        "store_state": True,
                        "state_key": "last_transaction_time"
                    }
                }
            }
        }
    ]
})
```

## Best Practices

1. **Choose the Right Incremental Pattern**:
   - Use timestamp-based for most real-time data
   - Use ID-based for sequential records
   - Use cursor-based for APIs that provide cursors

2. **State Management**:
   - Always implement proper state storage
   - Include error handling for state management
   - Consider backup state storage

3. **Performance Optimization**:
   - Use appropriate batch sizes
   - Implement parallel processing where possible
   - Monitor and adjust incremental windows

4. **Error Handling**:
   - Implement retry logic
   - Handle state recovery
   - Log incremental processing details

## Troubleshooting

### Common Issues and Solutions

1. **Missing Data**
   ```python
   # Add overlap to avoid missing data
   last_value = info.load_state.get('last_value')
   adjusted_value = (
       datetime.strptime(last_value, "%Y-%m-%dT%H:%M:%SZ") 
       - timedelta(hours=1)
   ).strftime("%Y-%m-%dT%H:%M:%SZ")
   ```

2. **State Management Issues**
   ```python
   # Implement state verification
   def verify_state(state_value):
       try:
           datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%SZ")
           return True
       except ValueError:
           return False
   ```

3. **Rate Limiting with Incremental Loads**
   ```python
   # Implement backoff strategy
   "endpoint": {
       "incremental": {
           "backoff_strategy": {
               "initial_delay": 1,
               "max_delay": 60,
               "factor": 2
           }
       }
   }
   ```

Remember to:
- Test incremental loading with small data sets first
- Verify state management functionality
- Monitor for data completeness
- Implement proper error handling
- Document state management approach
- Consider data consistency requirements 