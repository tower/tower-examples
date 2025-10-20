from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Iterable

from dbt.cli.main import dbtRunner


logger = logging.getLogger("tower.dbt")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def getenv(name: str, *, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def parse_commands(raw: str | None) -> list[str]:
    if not raw:
        return ["deps", "seed", "build"]
    commands = [cmd.strip() for cmd in raw.split(",")]
    commands = [cmd for cmd in commands if cmd]
    return commands or ["deps", "seed", "build"]


def build_cli_args(
    command: str,
    *,
    selector: str | None,
    full_refresh: bool,
    state_dir: str | None,
    vars_json: str | None,
) -> list[str]:
    args: list[str] = [command]
    if selector:
        args.extend(["--select", selector])
    if full_refresh and command in {"run", "build", "seed"}:
        args.append("--full-refresh")
    if state_dir:
        args.extend(["--state", state_dir])
    if vars_json:
        # pass-through string, dbt will parse as YAML/JSON
        args.extend(["--vars", vars_json])
    return args


def log_run_results(results: Iterable[object]) -> None:
    for entry in results:
        node = getattr(entry, "node", None)
        status = getattr(entry, "status", None)
        if node and hasattr(node, "name"):
            logger.info("dbt result | %s -> %s", node.name, status)


def write_profiles_yaml(destination: Path, payload: str) -> None:
    destination.write_text(payload.rstrip() + "\n", encoding="utf-8")
    logger.info("Wrote dbt profile to %s", destination)


def main() -> None:
    project_relative = getenv("DBT_PROJECT_PATH", default="dbt-project/olist_dbt")
    project_dir = Path(project_relative).resolve()
    if not project_dir.exists():
        raise FileNotFoundError(f"dbt project path does not exist: {project_dir}")

    profile_payload = getenv("DBT_PROFILE_YAML")
    if not profile_payload:
        raise RuntimeError(
            "DBT_PROFILE_YAML is required. Provide the full profiles.yml contents via a Tower secret."
        )

    commands = parse_commands(getenv("DBT_COMMANDS"))
    selector = getenv("DBT_SELECT")
    state_dir = getenv("DBT_STATE_DIR")
    vars_json = getenv("DBT_VARS_JSON")
    full_refresh = getenv("DBT_FULL_REFRESH", default="false").lower() in {"1", "true", "yes"}

    target = getenv("DBT_TARGET")
    threads_raw = getenv("DBT_THREADS")
    threads = int(threads_raw) if threads_raw else None

    runner = dbtRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        profiles_dir = Path(tmpdir)
        profile_path = profiles_dir / "profiles.yml"
        write_profiles_yaml(profile_path, profile_payload)
        # Some dbt adapters expect DBT_PROFILES_DIR to exist. Point it at the temp dir.
        os.environ["DBT_PROFILES_DIR"] = str(profiles_dir)

        runner_kwargs: dict[str, object] = {
            "project_dir": str(project_dir),
            "profiles_dir": str(profiles_dir),
        }
        if target:
            runner_kwargs["target"] = target
        if threads:
            runner_kwargs["threads"] = threads

        logger.info(
            "Starting dbt workflow | project=%s commands=%s target=%s selector=%s full_refresh=%s",
            project_dir,
            commands,
            target or "<default>",
            selector or "<none>",
            full_refresh,
        )

        for command in commands:
            args = build_cli_args(
                command,
                selector=selector,
                full_refresh=full_refresh,
                state_dir=state_dir,
                vars_json=vars_json,
            )

            logger.info("Running dbt %s ...", " ".join(args))
            result = runner.invoke(args, **runner_kwargs)

            result_list = getattr(result, "result", None)
            if result_list:
                log_run_results(result_list)

            if not result.success:
                error_detail = getattr(result, "message", "") or str(
                    getattr(result, "exception", "")
                )
                logger.error("dbt command failed: %s | detail=%s", " ".join(args), error_detail)
                raise RuntimeError(f"dbt command failed: {' '.join(args)}")

        logger.info("dbt workflow finished successfully.")


if __name__ == "__main__":
    main()
