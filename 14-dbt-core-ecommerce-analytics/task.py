from __future__ import annotations

import json
import os
import tower

from pathlib import Path
from seed import populate_seeds_from_archive

DATASET_ARCHIVE_ENV = "DBT_SEED_ARCHIVE_URI"
DEFAULT_SEED_ARCHIVE = "s3://tower-sandbox/olist_ecommerce_dataset/olist-seeds.zip"


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
    # Absolute path to the dbt project directory (contains dbt_project.yml).
    project_path = Path(_get_env_value("DBT_PROJECT_PATH") or "dbt-project/olist_dbt")
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

    workflow = tower.dbt(
        project_path=project_path,
        profile_payload=tower.dbt.load_profile_from_env(),
        commands=tower.dbt.parse_command_plan(_get_env_value("DBT_COMMANDS")),
        selector=_get_env_value("DBT_SELECT"),
        target=_get_env_value("DBT_TARGET"),
        threads=_parse_threads(_get_env_value("DBT_THREADS")),
        vars_payload=_parse_vars(_get_env_value("DBT_VARS_JSON")),
        full_refresh=(_get_env_value("DBT_FULL_REFRESH") or "false").lower() in {"1", "true", "yes"},
    )

    workflow.run()


if __name__ == "__main__":
    main()
