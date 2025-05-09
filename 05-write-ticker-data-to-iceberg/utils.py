import os
from pyarrow import json
import pyarrow as pa


###
#
# SCHEMA describes the schema of the underlying data that we expect to get out
#   of our raw data.
#
###
SCHEMA = pa.schema([
    ("ticker", pa.string()),
    ("date", pa.string()),
    ("open", pa.float64()),
    ("close", pa.float64()),
    ("volume", pa.int64()),
])

###
#   Sample usage
#   file = f"https://s3.amazonaws.com/tower.dev-sample-data/daily-ticker-data/{date}.json"
#   data = download(file)
###
def download(url: str) -> pa.Table:
    """
    `download` downloads the data from the given URL and returns it as a
    PyArrow Table.  

    Args:
        url (str): The URL of the file to download.
    
    Returns:
        pa.Table: The data as a PyArrow Table.
    """
    import requests

    resp = requests.get(url)
    tmp_file_path = "/tmp/daily_ticker_data.json"

    # We have to write it to a file to allow PyArrow to read it.
    with open(tmp_file_path, 'w') as f:
        f.write(resp.text)
    
    # Parse it into a PyArrow table, matching our schema.
    data = json.read_json(
        input_file=tmp_file_path,
        parse_options=json.ParseOptions(explicit_schema=SCHEMA)
    )

    # Remove the file after reading it.
    os.remove("/tmp/daily_ticker_data.json")
    return data



