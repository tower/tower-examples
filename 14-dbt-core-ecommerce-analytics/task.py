from __future__ import annotations

import json
import os
from pathlib import Path

from _dbt import (
    DbtRunnerConfig,
    load_profile_from_env,
    parse_command_plan,
    run_dbt_workflow,
)
from seed import populate_seeds_from_archive

DATASET_ARCHIVE_ENV = "DBT_SEED_ARCHIVE_URI"


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
    profile_payload = load_profile_from_env()

    # Absolute path to the dbt project directory (contains dbt_project.yml).
    project_path = Path(_get_env_value("DBT_PROJECT_PATH") or "dbt-project/olist_dbt")
    seed_archive_uri = _get_env_value(DATASET_ARCHIVE_ENV)
    if seed_archive_uri:
        # Pull zipped seeds (e.g., from S3) so dbt seed can run without committing CSVs.
        populate_seeds_from_archive(seed_archive_uri, project_path / "seeds")
    # Command plan, e.g. "deps, seed --full-refresh, build --select state:modified+".
    commands = parse_command_plan(_get_env_value("DBT_COMMANDS"))
    # Optional selector applied to commands that don't already pass --select.
    selector = _get_env_value("DBT_SELECT")
    # Override target name from the profile; blank uses the profile default.
    target = _get_env_value("DBT_TARGET")
    # Optional thread count; falls back to profile value when unset.
    threads = _parse_threads(_get_env_value("DBT_THREADS"))
    # Optional vars payload (JSON/YAML) passed to dbt.
    vars_payload = _parse_vars(_get_env_value("DBT_VARS_JSON"))

    # Toggle --full-refresh for run/build/seed if not already requested.
    full_refresh = (_get_env_value("DBT_FULL_REFRESH") or "false").lower() in {
        "1",
        "true",
        "yes",
    }

    config = DbtRunnerConfig(
        project_path=project_path,
        profile_payload=profile_payload,
        commands=commands,
        selector=selector,
        target=target,
        threads=threads,
        vars_payload=vars_payload,
        full_refresh=full_refresh,
    )

    run_dbt_workflow(config)


if __name__ == "__main__":
    main()
