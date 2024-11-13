import dlt

try:
    from .filesystem import FileItemDict, filesystem, readers, read_csv  # type: ignore
except ImportError:
    from filesystem import (
        FileItemDict,
        filesystem,
        readers,
        read_csv,
    )

BUCKET_URL = dlt.config["sources.filesystem.bucket_url"]
FILE_GLOB = dlt.config["sources.filesystem.file_glob"]

TARGET_SCHEMA_NAME = dlt.config["loader_config.target_schema_name"]
TARGET_TABLE_NAME = dlt.config["loader_config.target_table_name"]
WRITE_DISPOSITION = dlt.config["loader_config.write_disposition"]

def load_and_merge_csv() -> None:
    """Demonstrates how to scan folder with csv files, load them in chunk and merge on date column with the previous load"""
    pipeline = dlt.pipeline(
        pipeline_name="csv_to_snowflake",
        destination="snowflake",
        dataset_name=TARGET_SCHEMA_NAME,
    )

    # load all csv
    raw_files = readers(
        bucket_url=BUCKET_URL, file_glob=FILE_GLOB
    ).read_csv()

    if WRITE_DISPOSITION == "replace":
        replace_strategy = dlt.config["loader_config.replace_strategy"]
        raw_files.apply_hints(write_disposition=WRITE_DISPOSITION)
    elif WRITE_DISPOSITION == "merge":
        merge_key = dlt.config["loader_config.merge_key"]
        raw_files.apply_hints(write_disposition=WRITE_DISPOSITION, merge_key=merge_key)

    load_info = pipeline.run(raw_files.with_name(TARGET_TABLE_NAME))
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_and_merge_csv()
