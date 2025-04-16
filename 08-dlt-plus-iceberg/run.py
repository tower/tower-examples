# Description: GitHub data pipeline with raw and aggregated datasets
# Version: 2023-11-15-001

import dlt
import dlt_plus

from sources.github import github_events


def load_raw_github_events():
    pipeline = dlt.pipeline(
        pipeline_name="github_events",
        destination="duckdb",
        dataset_name="github_events_raw",
        dev_mode=True,
    )
    load_info = pipeline.run(github_events())
    row_counts = pipeline.last_trace.last_normalize_info
    print(load_info)  # noqa: T201
    print(row_counts)  # noqa: T201
    return pipeline


@dlt.resource(table_name="top_issue_creators", write_disposition="replace")
def transform_issues(pipeline):
    # Get issues data from raw dataset
    issues_df = pipeline.dataset().issues.select("user__login", "state").df()

    # Aggregate issue creators with counts and states
    top_creators = (
        issues_df.groupby("user__login")
        .agg(
            total_issues=("state", "count"),
            open_issues=("state", lambda s: (s == "open").sum()),
            closed_issues=("state", lambda s: (s == "closed").sum()),
        )
        .reset_index()
        .rename(columns={"user__login": "user_login"})
    )

    yield top_creators.to_dict(orient="records")


@dlt.resource(table_name="most_active_users", write_disposition="replace")
def transform_events(pipeline):
    # Get events data from raw dataset
    events_df = pipeline.dataset().events.select("actor__login").df()

    # Count events per user
    active_users = (
        events_df.groupby("actor__login")
        .size()
        .reset_index(name="event_count")
        .rename(columns={"actor__login": "user_login"})
    )

    yield active_users.to_dict(orient="records")


def create_aggregated_dataset(pipeline):
    aggregated_pipeline = dlt.pipeline(
        pipeline_name="github_events",
        destination="duckdb",
        dataset_name="github_analytics",
    )

    load_info = aggregated_pipeline.run(
        [transform_issues(pipeline), transform_events(pipeline)]
    )
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    entities = dlt_plus.current.entities()

    dataset = entities.create_dataset("github_events_raw", "duckdb")

    pipeline_config = dict(
        source="github.github_events",
        destination="duckdb",
        dataset_name="github_events_raw",
        progress="enlighten",
    )

    pipeline = entities.create_pipeline("github_events", **pipeline_config)
    pipeline.run()
    # pipeline = load_raw_github_events()
    # create_aggregated_dataset(pipeline)
