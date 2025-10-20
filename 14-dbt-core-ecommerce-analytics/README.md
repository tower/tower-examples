# Tower dbt Core Ecommerce Analytics App

This Tower example app shows how to run a dbt Core project with the Python API instead of shell commands. It executes the `olist_dbt` project included in this repo, but you can point it at any dbt project that is available in the workspace.

## What the app does
- Writes a `profiles.yml` file from the `DBT_PROFILE_YAML` secret.
- Invokes dbt commands (`deps`, `seed`, `build` by default) via `dbtRunner`.
- Streams run statuses to the Tower logs.

## Parameters & Secrets
| Name | Description | Default |
| ---- | ----------- | ------- |
| `DBT_COMMANDS` | Comma-separated list of dbt commands to run (`deps,seed,build`, etc.). Flags can follow each command (e.g. `build --select tag:daily`). | `deps,seed,build` |
| `DBT_PROJECT_PATH` | Relative path to the dbt project directory | `dbt-project/olist_dbt` |
| `DBT_TARGET` | Target name from the profile (empty = profile default) | _empty_ |
| `DBT_SELECT` | Optional `--select` selector | _empty_ |
| `DBT_FULL_REFRESH` | `true` to add `--full-refresh` to `run`/`build`/`seed` (unless already provided in `DBT_COMMANDS`) | `false` |
| `DBT_PROFILE_YAML` | **Secret.** Entire contents of `profiles.yml` | _(required)_ |

> ℹ️ Store `DBT_PROFILE_YAML` as a Tower secret so credentials never hit version control. You can still use `env_var()` inside the YAML to defer sensitive values to other secrets.

Advanced flags such as `DBT_THREADS`, `DBT_STATE_DIR`, or `DBT_VARS_JSON` remain supported—pass them with `tower run -p VAR=value` or extend the Towerfile if your workflow needs them regularly.

## Local setup
1. Ensure Python 3.11+ is available.
2. Install dependencies:
   ```bash
   uv venv
   uv sync
   ```
3. Create a profile secret for local testing:
   ```bash
   export DBT_PROFILE_YAML="$(cat dbt-project/olist_dbt/profiles.example.yml)"
   ```
4. Run the app:
   ```bash
   uv run python task.py
   ```

When run inside Tower, the app will execute the same workflow against your configured profile and dbt project. Adjust `DBT_COMMANDS` or `DBT_SELECT` to tailor the run to your needs (e.g., `DBT_COMMANDS=build` and `DBT_SELECT=tag:mart`).

## Programmatic helper
The `_dbt.py` module wraps `dbtRunner` with a higher-level interface:

```python
from _dbt import DbtRunnerConfig, run_dbt_workflow, load_profile_from_env

config = DbtRunnerConfig(
    project_path="path/to/dbt_project",
    profile_payload=load_profile_from_env(),
    # commands default to: deps -> seed -> build
)
run_dbt_workflow(config)
```

Override the defaults by editing the command plan (`parse_command_plan("deps,build --select tag:daily")`), enabling full refreshes, or passing vars/state directories through the config.
