import os
import dlt
from dlt.sources.filesystem import readers


# Tower app parameters (with defaults)
BUCKET_URL = os.environ.get("BUCKET_URL", "s3://mango-public-data/")
FILE_GLOB = os.environ.get("FILE_GLOB", "japan-trade-stats/custom_2020.csv")
TARGET_SCHEMA_NAME = os.environ.get("TARGET_SCHEMA_NAME", "raw")
TARGET_TABLE_NAME = os.environ.get("TARGET_TABLE_NAME", "trade_stats")
WRITE_DISPOSITION = os.environ.get("WRITE_DISPOSITION", "replace")
REPLACE_STRATEGY = os.environ.get("REPLACE_STRATEGY", "truncate-and-insert")
MERGE_KEY = os.environ.get("MERGE_KEY", "")


def load_csv_to_snowflake() -> None:
    """Load CSV files from S3 to Snowflake using dlt."""
    pipeline = dlt.pipeline(
        pipeline_name="s3_csv_to_snowflake",
        destination="snowflake",
        dataset_name=TARGET_SCHEMA_NAME,
    )

    # Read CSV files from S3
    raw_files = readers(
        bucket_url=BUCKET_URL, 
        file_glob=FILE_GLOB
    ).read_csv()

    # Apply write disposition hints
    if WRITE_DISPOSITION == "replace":
        raw_files.apply_hints(
            write_disposition={
                "disposition": "replace",
                "strategy": REPLACE_STRATEGY
            }
        )
    elif WRITE_DISPOSITION == "merge":
        if MERGE_KEY:
            raw_files.apply_hints(
                write_disposition="merge", 
                merge_key=MERGE_KEY
            )
        else:
            raise ValueError("MERGE_KEY must be set when WRITE_DISPOSITION is 'merge'")
    else:
        # append or other dispositions
        raw_files.apply_hints(write_disposition=WRITE_DISPOSITION)

    load_info = pipeline.run(raw_files.with_name(TARGET_TABLE_NAME))
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_csv_to_snowflake()
