from __future__ import annotations

import json
import os
import tower

from pathlib import Path
from seed import populate_seeds_from_archive

DATASET_ARCHIVE_ENV = "DBT_SEED_ARCHIVE_URI"
DEFAULT_SEED_ARCHIVE = "https://tower-examples-seed.s3.eu-central-1.amazonaws.com/olist_ecommerce_dataset/olist-seeds.zip"


def _get_env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _parse_threads(value: str | None) -> int | None:
    if not value:
        return None
    return int(value)


def _parse_vars(value: str | None):
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # Fallback: pass raw YAML/JSON string through to dbt
        return value


def main() -> None:
    """
    Main entry point for the dbt workflow.

    This example demonstrates how to run dbt commands via Tower. All configuration
    can be controlled via environment variables (set in the Towerfile) or overridden
    via Towerfile parameters when deploying/running the app.
    """
    # Path to the dbt project directory within the current code repository (contains dbt_project.yml).
    # Note that you MUST include the dbt project files in the Towerfile source section.
    # Override with DBT_PROJECT_PATH env var or Towerfile parameter.
    project_path = Path(_get_env_value("DBT_PROJECT_PATH") or "dbt-project/olist_dbt")

    # Download seed data from archive if needed
    seeds_dir = project_path / "seeds"
    existing_seeds = list(seeds_dir.glob("*.csv")) if seeds_dir.exists() else []
    seed_archive_uri = _get_env_value(DATASET_ARCHIVE_ENV)
    if seed_archive_uri:
        print("Using seed archive at {}".format(seed_archive_uri))
        populate_seeds_from_archive(seed_archive_uri, seeds_dir)
    elif not existing_seeds:
        print("Using default seed archive at {}".format(DEFAULT_SEED_ARCHIVE))
        populate_seeds_from_archive(DEFAULT_SEED_ARCHIVE, seeds_dir)
    else:
        print("Seed CSVs already present in {} – skipping download.".format(seeds_dir.resolve()))

    # Parse dbt configuration from environment variables.
    # These can be overridden via Towerfile parameters.

    # DBT_COMMANDS: Comma-separated list of dbt commands to run (e.g., "seed,run,test")
    commands = tower.dbt.parse_command_plan(_get_env_value("DBT_COMMANDS"))

    # DBT_SELECT: dbt selector for filtering models/tests (e.g., "tag:daily" or "model_name+")
    selector = _get_env_value("DBT_SELECT")

    # DBT_TARGET: Target profile to use from profiles.yml (e.g., "dev", "prod")
    target = _get_env_value("DBT_TARGET")

    # DBT_THREADS: Number of threads for parallel execution
    threads = _parse_threads(_get_env_value("DBT_THREADS"))

    # DBT_VARS_JSON: JSON string of variables to pass to dbt (e.g., '{"key": "value"}')
    vars_payload = _parse_vars(_get_env_value("DBT_VARS_JSON"))

    # DBT_FULL_REFRESH: Whether to do a full refresh of incremental models (true/false)
    full_refresh = (_get_env_value("DBT_FULL_REFRESH") or "false").lower() in {"1", "true", "yes"}

    # Create and run the dbt workflow
    workflow = tower.dbt(
        project_path=project_path,
        profile_payload=tower.dbt.load_profile_from_env(),
        commands=commands,
        selector=selector,
        target=target,
        threads=threads,
        vars_payload=vars_payload,
        full_refresh=full_refresh,
    )

    workflow.run()


if __name__ == "__main__":
    main()
