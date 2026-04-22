import json
import re
from collections import defaultdict

import boto3
import tower


bucket_name = tower.parameter("BUCKET_NAME", default="snowflake-iceberg-stage-248189900669")
table_name = tower.parameter("TABLE_NAME", default="CATALOG_RETURNS")
snowflake_table = tower.parameter("SNOWFLAKE_TABLE", default="SNOWFLAKE_SAMPLE_DATA.TPCDS_SF10TCL.CATALOG_RETURNS")
stage_name = tower.parameter("STAGE_NAME", default="TEST.PUBLIC.ICEBERG_TRANSFER_STAGE")
partition_col = tower.parameter("PARTITION_COLUMN", default="CR_RETURNED_DATE_SK")
n_pods = int(tower.parameter("N_PODS", default="8"))
unload_app = tower.parameter("UNLOAD_APP", default="unload-snowflake-table-to-s3")
worker_app = tower.parameter("WORKER_APP", default="snowflake-to-iceberg-load-worker")
warehouse_size = tower.parameter("WAREHOUSE_SIZE", default="X-LARGE")
warehouse_size_after = tower.parameter("WAREHOUSE_SIZE_AFTER", default="X-SMALL")
environment = tower.parameter("ENVIRONMENT", default="")

# 1. Unload Snowflake table to S3 (partitioned parquet)
print(f"Starting unload: {snowflake_table} -> s3://{bucket_name}/unload/", flush=True)
env_arg = environment if environment else None
unload_run = tower.run_app(unload_app, environment=env_arg, parameters={
    "TABLE_NAME": snowflake_table,
    "STAGE_NAME": stage_name,
    "PARTITION_COLUMN": partition_col,
    "WAREHOUSE_SIZE": warehouse_size,
    "WAREHOUSE_SIZE_AFTER": warehouse_size_after,
})
print(f"  Unload run {unload_run.run_id} started, waiting...", flush=True)
tower.wait_for_run(unload_run, raise_on_failure=True)
print("  Unload complete.", flush=True)

# 2. Discover partition prefixes in the unload bucket
s3 = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")

partition_re = re.compile(rf"{re.escape(partition_col)}=([^/]+)")
partitions = defaultdict(list)

for page in paginator.paginate(Bucket=bucket_name, Prefix="unload/"):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".parquet"):
            continue
        m = partition_re.search(key)
        if m:
            partitions[m.group(1)].append(key)

total_files = sum(len(files) for files in partitions.values())
print(f"Found {len(partitions)} partitions, {total_files} parquet files total", flush=True)

if not partitions:
    raise RuntimeError(
        f"No parquet files found under s3://{bucket_name}/unload/ "
        f"with {partition_col}=<value>/ directory structure"
    )

# 2. Split partitions round-robin into N chunks and write manifests to S3
items = list(partitions.items())
actual_pods = min(n_pods, len(items))

for i in range(actual_pods):
    chunk = dict(items[i::actual_pods])
    s3.put_object(
        Bucket=bucket_name,
        Key=f"manifests/chunk_{i}.json",
        Body=json.dumps(chunk),
    )
    chunk_files = sum(len(f) for f in chunk.values())
    print(f"  Chunk {i}: {len(chunk)} partitions, {chunk_files} files", flush=True)

# 3. Fan out worker runs
child_runs = []
env_arg = environment if environment else None
for i in range(actual_pods):
    run = tower.run_app(worker_app, environment=env_arg, parameters={
        "TABLE_NAME": table_name,
        "BUCKET_NAME": bucket_name,
        "PARTITION_COLUMN": partition_col,
        "CHUNK_ID": str(i),
    })
    child_runs.append(run)
    print(f"  Started worker run {run.run_id} for chunk {i}", flush=True)

print(f"\nWaiting for {actual_pods} workers to complete...", flush=True)

# 4. Wait for all workers
successful, unsuccessful = tower.wait_for_runs(child_runs, raise_on_failure=False)

print(f"\nResults: {len(successful)} succeeded, {len(unsuccessful)} failed", flush=True)
if unsuccessful:
    for run in unsuccessful:
        print(f"  FAILED: run {run.run_id} (chunk)", flush=True)
    raise RuntimeError(f"{len(unsuccessful)} worker(s) failed")

print("All workers completed successfully!", flush=True)
