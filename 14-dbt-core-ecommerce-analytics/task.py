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

    project_path = Path(_get_env_value("DBT_PROJECT_PATH") or "dbt-project/olist_dbt")
    commands = parse_command_plan(_get_env_value("DBT_COMMANDS"))
    selector = _get_env_value("DBT_SELECT")
    target = _get_env_value("DBT_TARGET")
    threads = _parse_threads(_get_env_value("DBT_THREADS"))
    state_dir_raw = _get_env_value("DBT_STATE_DIR")
    vars_payload = _parse_vars(_get_env_value("DBT_VARS_JSON"))

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
        state_dir=Path(state_dir_raw) if state_dir_raw else None,
        full_refresh=full_refresh,
    )

    run_dbt_workflow(config)


if __name__ == "__main__":
    main()
