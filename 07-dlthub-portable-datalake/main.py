from pathlib import Path
import subprocess
import os
import dlt

from dlthub_data_pond.sources.github_events_dispatch import get_repo_events
from dlthub_data_pond.destinations.move_to_iceberg import iceberg_transformed_resource


# Run dbt transformations
def run_dbt_transformations(pipeline):
    """Execute dbt transformations after data loading"""
    # Correct path construction
    dbt_project_dir = (
        Path(__file__).parent
        / "dlthub_data_pond"
        / "transformations"
        / "dbt_aggregate_issues"
    )

    # Install dbt dependencies
    subprocess.run(["dbt", "deps"], cwd=dbt_project_dir, check=True)

    # Create vars dictionary and convert to JSON-like string
    dbt_vars = {
        "source_dataset_name": pipeline.dataset_name,
        "source_database_name": pipeline.pipeline_name,
        "destination_dataset_name": "github_issues_transformed",
    }
    vars_str = str(dbt_vars).replace("'", '"')

    # Set up environment with existing env plus our additions
    env = os.environ.copy()
    env["DBT_DUCKDB_PATH"] = str(Path(__file__).parent / "analyze_github_issues.duckdb")

    # Run dbt
    subprocess.run(
        [
            "dbt",
            "run",
            "--profiles-dir",
            str(Path(__file__).parent.absolute()),
            "--vars",
            vars_str,
        ],
        cwd=dbt_project_dir,
        check=True,
        env=env,
    )


def load_github_events():
    pipeline = dlt.pipeline(
        pipeline_name="analyze_github_issues",
        destination="duckdb",
        dataset_name="github_events_data",
        progress="enlighten",
    )

    # Load raw data
    load_info = pipeline.run(get_repo_events)
    row_counts = pipeline.last_trace.last_normalize_info
    print(load_info)  # noqa: T201
    print(row_counts)  # noqa: T201

    # Execute transformations after loading
    run_dbt_transformations(pipeline)

    # Return both load and transformation results
    return load_info, pipeline


def output_transformed_events():
    # Configure Iceberg pipeline
    pipeline = dlt.pipeline(
        pipeline_name="move_data_to_iceberg",
        destination="iceberg",
        dataset_name="github_issues_transformed",
    )

    # Load transformed data to Iceberg
    load_info = pipeline.run(iceberg_transformed_resource())

    # Get load metrics
    row_counts = pipeline.last_trace.last_normalize_info
    print(load_info)  # noqa: T201
    print(row_counts)  # noqa: T201

    return load_info, row_counts


if __name__ == "__main__":
    load_github_events()
