from pyiceberg.catalog import load_catalog
from pyarrow import csv
import fsspec
import os

# Review https://www.tabular.io/apache-iceberg-cookbook/getting-started-python-configuration/
# on how to pass catalog configuration parameters
# Either use the .pyiceberg.yaml file or pass 4 environment variables e.g.
# PYICEBERG_CATALOG__DEFAULT__URI=<https://... for REST catalogs>
# PYICEBERG_CATALOG__DEFAULT__CREDENTIAL=<client_id>:<client_secret>
# PYICEBERG_CATALOG__DEFAULT__SCOPE=PRINCIPAL_ROLE:<principal_role_your_configured>
# PYICEBERG_CATALOG__DEFAULT__WAREHOUSE=<catalog_identifier>
# The catalog name "default" must be in the config file or in env variable names
catalog = load_catalog("default")

# get source and destination paths
csv_file_path = os.getenv("csv_file_path")
iceberg_table_name= os.getenv("iceberg_table")

# follows the tutorial https://py.iceberg.apache.org/#connecting-to-a-catalog
# Download from s3 a large CSV file with Japan Trade Statistics (import and export of goods by month)
# Use fsspec to cache this file locally
# Open the csv file in binary mode so that the read_csv call is happy https://issues.apache.org/jira/browse/ARROW-4883

of = fsspec.open("filecache://{csv_file_path}".format(csv_file_path=csv_file_path), mode='rb',
                 cache_storage='/tmp/cache1',
                 target_protocol='s3', target_options={'anon': True})

# Read the csv file into an PyArrow table so that we can take its schema and pass it to iceberg
with of as f:
    artable = csv.read_csv(f)

# create the "default" namespace in our open lakehouse
catalog.create_namespace_if_not_exists("default")

# create or retrieve the table to hold our Japan trade stats
icetable = catalog.create_table_if_not_exists(iceberg_table_name, schema=artable.schema)

# add the contents of the csv file to our iceberg table
icetable.append(artable)

# The scan will materialize the table on S3
records_read = len(artable)
records_written = len(icetable.scan().to_arrow())

# print a nicely formatted summary
print("\n=== Iceberg Write Summary ===")
print(f"Records read from CSV: {records_read:,}")
print(f"Records written to table: {records_written:,}")
print(f"Table location: {icetable.location()}")
print("==========================\n")
