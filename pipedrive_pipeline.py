import dlt
from dlt.sources.rest_api import rest_api_source
from datetime import datetime, timedelta

# Default start date for incremental loading (e.g., 30 days ago)
DEFAULT_START_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

# Removed api_token argument. Secret is resolved inside.
def pipedrive_source():
    """
    Creates a verified Pipedrive data source configuration for DLT pipeline.
    Resolves the API token explicitly from dlt secrets.
    """
    # Explicitly resolve the secret *before* creating the config dict
    # Assumes secret key is 'api_token' in secrets.toml under [sources.pipedrive] or [sources]
    actual_api_token = dlt.secrets["api_token"]

    return rest_api_source({
        "client": {
            "base_url": "https://api.pipedrive.com/v1/",
            "auth": {
                "type": "api_key",
                "name": "api_token",
                # Use the explicitly resolved secret value
                "api_key": actual_api_token, 
                "location": "query"
            },
            # Define paginator declaratively - Corrected for cursor type
            "paginator": {
                "type": "cursor",
                "cursor_path": "additional_data.pagination.next_start",
                "cursor_param": "start", # Changed from offset_param
                # Removed limit_param, total_path, maximum_limit
            }
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
            "endpoint": {
                "params": {
                    "limit": 100 # Page size limit is handled here
                },
                # Apply declarative paginator to defaults - Corrected for cursor type
                 "paginator": {
                    "type": "cursor",
                    "cursor_path": "additional_data.pagination.next_start",
                    "cursor_param": "start", # Changed from offset_param
                    # Removed limit_param, total_path, maximum_limit
                }
            }
        },
        "resources": [
            # Resources without explicit incremental (usually config/metadata)
            {
                "name": "currencies",
                "endpoint": {
                    "path": "currencies",
                    "data_selector": "data.*"
                }
            },
            {
                "name": "activity_types",
                "endpoint": {
                    "path": "activityTypes",
                    "data_selector": "data.*"
                }
            },
            {
                "name": "filters",
                "endpoint": {
                    "path": "filters",
                    "data_selector": "data.*"
                }
            },
            {
                "name": "stages",
                "endpoint": {
                    "path": "stages",
                    "data_selector": "data.*"
                }
            },
            {
                "name": "pipelines",
                "endpoint": {
                    "path": "pipelines",
                    "data_selector": "data.*"
                }
            },
            # {
            #     "name": "goals", # Goals might have specific incremental logic depending on type
            #     "endpoint": {
            #         "path": "goals",
            #         "data_selector": "data.*",
            #         # Consider adding specific incremental based on goal type if needed
            #     }
            # },

             # Standard resources with timestamp incremental
            {
                "name": "deals",
                "endpoint": {
                    "path": "deals",
                    "data_selector": "data.*",
                    "incremental": {
                        "cursor_path": "update_time", # Use update_time for incremental
                        # Using 'update_time' as cursor might be sufficient if API sorts by it implicitly
                        # Removing potentially problematic 'start_date' param assumption
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "organizations",
                "endpoint": {
                    "path": "organizations",
                    "data_selector": "data.*",
                     "incremental": {
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "persons",
                "endpoint": {
                    "path": "persons",
                    "data_selector": "data.*",
                    "incremental": {
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
             {
                "name": "products",
                "endpoint": {
                    "path": "products",
                    "data_selector": "data.*",
                     "incremental": {
                        "cursor_path": "update_time",
                         "initial_value": DEFAULT_START_DATE
                    }
                 }
            },

            # Recents resources with specific 'since_timestamp' incremental
            {
                "name": "recent_notes",
                "endpoint": {
                    "path": "recents",
                    "params": {"items": "note"},
                    "data_selector": "data.*",
                    "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_users",
                "endpoint": {
                    "path": "recents",
                    "params": {"items": "user"},
                    "data_selector": "data.*",
                     "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_activities",
                "endpoint": {
                    "path": "recents",
                    "params": {"items": "activity"},
                    "data_selector": "data.*",
                     "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_deals",
                "endpoint": {
                    "path": "recents",
                     "params": {"items": "deal"},
                    "data_selector": "data.*",
                    "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                         "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_files",
                "endpoint": {
                    "path": "recents",
                     "params": {"items": "file"},
                    "data_selector": "data.*",
                    "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_organizations",
                 "endpoint": {
                    "path": "recents",
                     "params": {"items": "organization"},
                    "data_selector": "data.*",
                    "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_persons",
                 "endpoint": {
                    "path": "recents",
                     "params": {"items": "person"},
                    "data_selector": "data.*",
                    "incremental": {
                         "start_param": "since_timestamp",
                         "cursor_path": "update_time",
                        "initial_value": DEFAULT_START_DATE
                    }
                }
            },
            {
                "name": "recent_products",
                 "endpoint": {
                    "path": "recents",
                     "params": {"items": "product"},
                     "data_selector": "data.*",
                    "incremental": {
                        "start_param": "since_timestamp",
                        "cursor_path": "update_time",
                         "initial_value": DEFAULT_START_DATE
                     }
                }
            }
        ]
    })

if __name__ == "__main__":
    # Ensure you have your Pipedrive API token in secrets.toml or environment variables:
    # [sources.pipedrive]
    # api_token="your_api_token"

    # Create the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="pipedrive",
        destination="duckdb",  # Change destination as needed (e.g., bigquery, redshift)
        dataset_name="pipedrive_data"
    )

    # Run the pipeline
    # Load data from the source
    print("Running pipeline...")
    load_info = pipeline.run(pipedrive_source())

    # Print outcomes
    print(load_info)
    print("Pipeline run complete.")

    # Optionally, inspect the data
    # try:
    #     import duckdb
    #     conn = duckdb.connect(f"{pipeline.pipeline_name}.duckdb")
    #     print(f"Available tables in {pipeline.dataset_name}:")
    #     print(conn.sql(f"SHOW TABLES FROM {pipeline.dataset_name}").df())
    #     conn.close()
    # except ImportError:
    #     print("Install duckdb and pandas to inspect the data.")
    # except Exception as e:
    #      print(f"Could not inspect data: {e}") 