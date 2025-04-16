# File: 07-dlthub-portable-datalake/dlthub_data_pond/destinations/move_to_iceberg.py
# Description: Source for loading transformed data to Iceberg
# Version: 2024-05-23-001

import dlt
from dlt.sources.helpers import sql_database
from sqlalchemy import create_engine
from pathlib import Path


@dlt.resource(table_format="iceberg")
def iceberg_transformed_resource():
    """
    Source for reading transformed dimension tables from DuckDB.
    Yields resources for dim_issues_actors and dim_issues_repos tables.
    """
    # Connect to DuckDB containing transformed data
    duckdb_path = Path(__file__).parent.parent.parent / "analyze_github_issues.duckdb"
    engine = create_engine(f"duckdb:///{duckdb_path}")

    # Setup SQL database helper
    database = sql_database(engine)

    # Define resources for our dimension tables
    dim_actors = database.with_table(
        "dim_issues_actors", write_disposition="merge", primary_key="actor_id"
    )
    dim_repos = database.with_table(
        "dim_issues_repos", write_disposition="merge", primary_key="repo_id"
    )

    return dim_actors, dim_repos
