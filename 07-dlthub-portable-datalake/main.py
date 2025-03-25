from pathlib import Path
import subprocess
import os
import dlt

from dlthub_data_pond.sources.github_events_dispatch import get_repo_events


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

    subprocess.run(["dbt", "deps"], cwd=dbt_project_dir, check=True)

    # Pass schema name from pipeline config
    subprocess.run(
        [
            "dbt",
            "run",
            "--profiles-dir",
            Path(__file__).parent.absolute(),
            "--vars",
            f"{{"
            + f"'source_dataset_name': '{pipeline.dataset_name}',"
            + f"'source_database_name': '{pipeline.pipeline_name}',"
            + "'destination_dataset_name': 'github_issues_transformed',"
            + f"}}",
        ],
        cwd=dbt_project_dir,
        check=True,
        env={
            **os.environ,
            "DBT_DUCKDB_PATH": str(
                Path(__file__).parent / "analyze_github_issues.duckdb"
            ),
        },
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


if __name__ == "__main__":
    load_github_events()
