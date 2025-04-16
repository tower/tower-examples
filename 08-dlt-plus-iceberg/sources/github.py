import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source
def github_events():
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.github.com/repos/dlt-hub/dlt/",
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
            "endpoint": {
                "params": {
                    "per_page": 100,
                },
            },
        },
        "resources": [
            {
                "name": "issues",
                "endpoint": {
                    "path": "issues",
                    "params": {
                        "sort": "updated",
                        "direction": "desc",
                        "state": "open",
                        "since": {
                            "type": "incremental",
                            "cursor_path": "updated_at",
                            "initial_value": "2024-01-01T00:00:00Z",
                        },
                    },
                },
            },
            {
                "name": "events",
            },
        ],
    }

    yield from rest_api_resources(config)
