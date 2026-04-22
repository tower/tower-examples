"""
Tower Example: Unload Snowflake Table to S3 via COPY INTO

Runs a Snowflake COPY INTO command to export a native Snowflake table
to Parquet files on an external stage, partitioned by year and month.
"""

import os
import snowflake.connector


def main():
    # Snowflake connection parameters from Tower secrets / env vars
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PAT"], # PAT used as password
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
    )

    table_name = os.getenv("TABLE_NAME")
    stage_name = os.getenv("STAGE_NAME")
    warehouse_name = os.getenv("SNOWFLAKE_WAREHOUSE")
    warehouse_size = os.getenv("WAREHOUSE_SIZE", "")
    warehouse_size_after = os.getenv("WAREHOUSE_SIZE_AFTER", "")
    partition_col = os.getenv("PARTITION_COLUMN")

    file_format_sql = """
CREATE OR REPLACE FILE FORMAT my_parquet_format
  TYPE = 'PARQUET'
  COMPRESSION = 'SNAPPY';
"""

    copy_sql = f"""
COPY INTO @{stage_name}/
FROM {table_name}
{f"PARTITION BY ('{partition_col}=' || to_varchar({partition_col}))" if partition_col else ""}
FILE_FORMAT = (FORMAT_NAME = my_parquet_format)
HEADER = TRUE
MAX_FILE_SIZE = 268435456
"""

    try:
        cur = conn.cursor()

        if warehouse_size:
            print(f"Resizing warehouse {warehouse_name} to {warehouse_size}", flush=True)
            cur.execute(f"ALTER WAREHOUSE {warehouse_name} SET WAREHOUSE_SIZE = '{warehouse_size}'")

        print("Creating file format")
        cur.execute(file_format_sql)
        for row in cur.fetchall():
            print(f"  {row}")

        print(f"Running COPY INTO from {table_name} to @{stage_name}/{table_name}")
        cur.execute(copy_sql)
        results = cur.fetchall()

        print(f"COPY INTO completed successfully. {len(results)} file(s) written.")
        for row in results:
            print(f"  {row}")
    finally:
        if warehouse_size_after:
            print(f"Resizing warehouse {warehouse_name} back to {warehouse_size_after}", flush=True)
            cur.execute(f"ALTER WAREHOUSE {warehouse_name} SET WAREHOUSE_SIZE = '{warehouse_size_after}'")
        conn.close()


if __name__ == "__main__":
    main()
