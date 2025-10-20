# Tower dbt Core Ecommerce Analytics App

This Tower example app shows how to run a dbt Core project with the Python API instead of shell commands. It executes the `olist_dbt` project included in this repo, but you can point it at any dbt project that is available in the workspace.

## What the app does
- Writes a `profiles.yml` file from the `DBT_PROFILE_YAML` secret.
- Invokes dbt commands (`deps`, `seed`, `build` by default) via `dbtRunner`.
- Streams run statuses to the Tower logs.

## Parameters & Secrets
| Name | Description | Default |
| ---- | ----------- | ------- |
| `DBT_COMMANDS` | Comma-separated list of dbt commands to run (`deps,seed,build`, etc.) | `deps,seed,build` |
| `DBT_PROJECT_PATH` | Relative path to the dbt project directory | `dbt-project/olist_dbt` |
| `DBT_TARGET` | Target name from the profile (empty = profile default) | _empty_ |
| `DBT_SELECT` | Optional `--select` selector | _empty_ |
| `DBT_THREADS` | Number of threads to pass to dbt | _empty_ |
| `DBT_FULL_REFRESH` | `true` to add `--full-refresh` to `run`/`build`/`seed` | `false` |
| `DBT_STATE_DIR` | Optional `--state` directory path | _empty_ |
| `DBT_VARS_JSON` | JSON/YAML string forwarded to `--vars` | _empty_ |
| `DBT_PROFILE_YAML` | **Secret.** Entire contents of `profiles.yml` | _(required)_ |

> ℹ️ Store `DBT_PROFILE_YAML` as a Tower secret so credentials never hit version control. You can still use `env_var()` inside the YAML to defer sensitive values to other secrets.

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
