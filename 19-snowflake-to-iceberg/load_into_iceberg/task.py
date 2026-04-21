import duckdb
import json
import os

import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, LongType, DoubleType
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import IdentityTransform


# tower runtime secrets
client_id, client_secret = os.environ['PYICEBERG_CATALOG__DEFAULT__CREDENTIAL'].split(":")
polaris_uri = os.environ['PYICEBERG_CATALOG__DEFAULT__URI']
warehouse = os.environ['PYICEBERG_CATALOG__DEFAULT__WAREHOUSE']

# AWS credentials - use explicit keys if provided, otherwise fall back to credential chain (e.g. EC2 instance role)
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region = os.environ.get('AWS_REGION', 'eu-central-1')
os.environ.pop('AWS_SESSION_TOKEN', None)
use_credential_chain = not (aws_access_key_id and aws_secret_access_key)

# config parameters
table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME'][5:] if os.environ['BUCKET_NAME'].startswith('s3://') else os.environ['BUCKET_NAME']
namespace = os.environ.get('NAMESPACE', 'default')
chunk_id = os.environ.get('CHUNK_ID') or None

# 1. Setup Connection & Extensions
con = duckdb.connect()
con.install_extension("iceberg")
con.load_extension("iceberg")
con.install_extension("httpfs")
con.load_extension("httpfs")

# 2. Performance Tuning
cpu_count = os.cpu_count() or 8
con.execute(f"SET threads TO {cpu_count};")
con.execute("SET memory_limit = '50GB';")
con.execute("SET temp_directory = '/tmp/duckdb_temp';")
con.execute("SET preserve_insertion_order = false;")
con.execute("SET http_keep_alive = true;")
con.execute("SET http_timeout = 300000;")  # 5 minutes

if use_credential_chain:
    con.sql(f"""
        CREATE SECRET s3_secret (TYPE S3, PROVIDER 'credential_chain', REGION '{region}', SCOPE 's3://{bucket_name}');
    """)
else:
    con.sql(f"""
        CREATE SECRET s3_secret (TYPE S3, PROVIDER 'config', KEY_ID '{aws_access_key_id}', SECRET '{aws_secret_access_key}', REGION '{region}', SCOPE 's3://{bucket_name}');
    """)
con.sql(f"""
    CREATE SECRET polaris_secret (TYPE ICEBERG, CLIENT_ID '{client_id}', CLIENT_SECRET '{client_secret}', ENDPOINT '{polaris_uri}');
""")

con.sql(f"""
    ATTACH '{warehouse}' AS polaris_catalog (
        TYPE ICEBERG,
        ENDPOINT '{polaris_uri}',
        SECRET polaris_secret,
        ACCESS_DELEGATION_MODE 'vended_credentials',
        DEFAULT_REGION '{region}'
    );
""")

schema = Schema(
    NestedField(field_id=1, name="CR_CALL_CENTER_SK", field_type=LongType(), required=False),
    NestedField(field_id=2, name="CR_CATALOG_PAGE_SK", field_type=LongType(), required=False),
    NestedField(field_id=3, name="CR_FEE", field_type=DoubleType(), required=False),
    NestedField(field_id=4, name="CR_ITEM_SK", field_type=LongType(), required=False),
    NestedField(field_id=5, name="CR_NET_LOSS", field_type=DoubleType(), required=False),
    NestedField(field_id=6, name="CR_ORDER_NUMBER", field_type=LongType(), required=False),
    NestedField(field_id=7, name="CR_REASON_SK", field_type=LongType(), required=False),
    NestedField(field_id=8, name="CR_REFUNDED_ADDR_SK", field_type=LongType(), required=False),
    NestedField(field_id=9, name="CR_REFUNDED_CASH", field_type=DoubleType(), required=False),
    NestedField(field_id=10, name="CR_REFUNDED_CDEMO_SK", field_type=LongType(), required=False),
    NestedField(field_id=11, name="CR_REFUNDED_CUSTOMER_SK", field_type=LongType(), required=False),
    NestedField(field_id=12, name="CR_REFUNDED_HDEMO_SK", field_type=LongType(), required=False),
    NestedField(field_id=13, name="CR_RETURNED_DATE_SK", field_type=LongType(), required=False),
    NestedField(field_id=14, name="CR_RETURNED_TIME_SK", field_type=LongType(), required=False),
    NestedField(field_id=15, name="CR_RETURNING_ADDR_SK", field_type=LongType(), required=False),
    NestedField(field_id=16, name="CR_RETURNING_CDEMO_SK", field_type=LongType(), required=False),
    NestedField(field_id=17, name="CR_RETURNING_CUSTOMER_SK", field_type=LongType(), required=False),
    NestedField(field_id=18, name="CR_RETURNING_HDEMO_SK", field_type=LongType(), required=False),
    NestedField(field_id=19, name="CR_RETURN_AMOUNT", field_type=DoubleType(), required=False),
    NestedField(field_id=20, name="CR_RETURN_AMT_INC_TAX", field_type=DoubleType(), required=False),
    NestedField(field_id=21, name="CR_RETURN_QUANTITY", field_type=LongType(), required=False),
    NestedField(field_id=22, name="CR_RETURN_SHIP_COST", field_type=DoubleType(), required=False),
    NestedField(field_id=23, name="CR_RETURN_TAX", field_type=DoubleType(), required=False),
    NestedField(field_id=24, name="CR_REVERSED_CHARGE", field_type=DoubleType(), required=False),
    NestedField(field_id=25, name="CR_SHIP_MODE_SK", field_type=LongType(), required=False),
    NestedField(field_id=26, name="CR_STORE_CREDIT", field_type=DoubleType(), required=False),
    NestedField(field_id=27, name="CR_WAREHOUSE_SK", field_type=LongType(), required=False),
)


partition_spec = PartitionSpec(
    PartitionField(source_id=13, field_id=1000, transform=IdentityTransform(), name="CR_RETURNED_DATE_SK")
)


catalog = load_catalog("default")


try:
    catalog.create_namespace(namespace)
except Exception:
    pass  # namespace already exists

if not catalog.table_exists(f"{namespace}.{table_name}"):
    catalog.create_table(
        identifier=f"{namespace}.{table_name}",
        schema=schema,
        partition_spec=partition_spec
    )
    print(f"Partitioned table {namespace}.{table_name} created in Polaris.")


if chunk_id is not None:
    # Parallel mode: read only this worker's assigned manifest chunk
    s3 = boto3.client("s3", region_name=region)
    manifest = json.loads(
        s3.get_object(Bucket=bucket_name, Key=f"manifests/chunk_{chunk_id}.json")["Body"].read()
    )
    file_list = [f"s3://{bucket_name}/{key}" for keys in manifest.values() for key in keys]
    print(f"Chunk {chunk_id}: {len(file_list)} files across {len(manifest)} partitions", flush=True)

    con.execute("""
        CREATE VIEW s3_data AS
        SELECT * FROM read_parquet($1, hive_partitioning=True)
    """, [file_list])
else:
    # Single-run mode: read all parquet files (original behavior)
    print(f"Registering data from s3://{bucket_name}/unload...", flush=True)
    con.sql(f"""
        CREATE VIEW s3_data AS
        SELECT * FROM read_parquet('s3://{bucket_name}/unload/**/*.parquet', hive_partitioning=True)
    """)

print("Ingesting data...", flush=True)
con.execute(f"""
    INSERT INTO polaris_catalog.{namespace}.{table_name}
    SELECT * FROM s3_data
""")
print("Done!", flush=True)