import json
from collections import defaultdict

import boto3
import tower


bucket_name = tower.parameter("BUCKET_NAME", default="snowflake-iceberg-stage-248189900669")
table_name = tower.parameter("TABLE_NAME", default="CATALOG_RETURNS")
n_pods = int(tower.parameter("N_PODS", default="8"))
worker_app = tower.parameter("WORKER_APP", default="s3-to-iceberg")
environment = tower.parameter("ENVIRONMENT", default="")

# 1. Discover partition prefixes in the unload bucket
s3 = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")

partitions = defaultdict(list)
for page in paginator.paginate(Bucket=bucket_name, Prefix="unload/"):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        parts = key.split("/")
        part_val = next((p for p in parts if p.startswith("CR_RETURNED_DATE_SK=")), None)
        if part_val and key.endswith(".parquet"):
            partitions[part_val].append(key)

total_files = sum(len(files) for files in partitions.values())
print(f"Found {len(partitions)} partitions, {total_files} parquet files total", flush=True)

# 2. Split partitions round-robin into N chunks and write manifests to S3
items = list(partitions.items())
actual_pods = min(n_pods, len(partitions))

for i in range(actual_pods):
    chunk = dict(items[i::actual_pods])
    s3.put_object(
        Bucket=bucket_name,
        Key=f"manifests/chunk_{i}.json",
        Body=json.dumps(chunk),
    )
    chunk_files = sum(len(files) for files in chunk.values())
    print(f"  Chunk {i}: {len(chunk)} partitions, {chunk_files} files", flush=True)

# 3. Fan out worker runs
child_runs = []
env_arg = environment if environment else None
for i in range(actual_pods):
    run = tower.run_app(worker_app, environment=env_arg, parameters={
        "TABLE_NAME": table_name,
        "BUCKET_NAME": bucket_name,
        "CHUNK_ID": str(i),
    })
    child_runs.append(run)
    print(f"  Started worker run {run.id} for chunk {i}", flush=True)

print(f"\nWaiting for {actual_pods} workers to complete...", flush=True)

# 4. Wait for all workers
successful, unsuccessful = tower.wait_for_runs(child_runs, raise_on_failure=False)

print(f"\nResults: {len(successful)} succeeded, {len(unsuccessful)} failed", flush=True)
if unsuccessful:
    for run in unsuccessful:
        print(f"  FAILED: run {run.id} (chunk)", flush=True)
    raise RuntimeError(f"{len(unsuccessful)} worker(s) failed")

print("All workers completed successfully!", flush=True)
