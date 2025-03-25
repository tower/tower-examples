import time
import dlt
from dlt.sources.helpers import requests


@dlt.resource(
    primary_key="id",
    table_name=lambda i: i["type"],
    write_disposition="append",
    columns={
        "created_at": {"data_type": "timestamp"},
        "issue": {"data_type": "complex"},
        "actor": {"data_type": "complex"},
    }
)
def get_repo_events(last_created_at=dlt.sources.incremental("created_at")):
    url = "https://api.github.com/repos/dlt-hub/dlt/events?per_page=100"

    while True:
        response = requests.get(url)
        response.raise_for_status()
        yield response.json()

        # Stop requesting pages if the last element was already older than
        # the initial value.
        # Note: incremental will skip those items anyway, we just do not
        # want to use the API limits.
        if last_created_at.start_out_of_range:
            break

        # Get the next page.
        if "next" not in response.links:
            break
        url = response.links["next"]["url"]
        # be nice to github
        time.sleep(2)
