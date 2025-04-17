import tower

# We use PyArrow to communicate serialize data that's headed for Tower.
import pyarrow as pa
from pyarrow import json

# We need the os package to get some parameters from the environment
import os

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


###
#
# main: This is the main function of the program! It demonstrates how to load a
#   table in Tower and how to insert data into the underlying table.
#
###
def main():
    ###
    # 
    # Step 0: We need to get the date of the file that we're loading.
    #
    ###
    date = os.getenv("FILE_DATE", "")

    if date == "":
        raise ValueError("FILE_DATE must be set to the date of the file being loaded.")

    ###
    #
    # Step 1: Get a reference to the table in Tower. If it doesn't exist, we'll
    #   create it.
    #
    ###
    table = tower.tables("daily_ticker_data").create_if_not_exists(SCHEMA)
    
    ###
    # 
    # Step 2: We need to download the data that we want to insert into the table.
    #
    ###
    file = f"https://s3.amazonaws.com/tower.dev-sample-data/daily-ticker-data/{date}.json"
    data = download(file)

    ###
    #
    # Step 3: Insert the underlying data into the table! All the maintenance
    # and lookups are managed by Tower.
    #
    ###
    table.insert(data)


if __name__ == "__main__":
    main()
