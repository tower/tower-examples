# Temporary fix for the issues with not having a fully-activated virual
# environment in the Tower runtime environment at execution time.
source .venv/bin/activate

dlt project clean
dlt pipeline -l
dlt pipeline events_to_lake run
dlt transformation . run
dlt dataset reports_dataset info
