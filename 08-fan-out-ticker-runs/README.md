# Fan out the downloads of ticker data

This app will download data for multiple tickers by running parallel runs of the "write-ticker-data-to-iceberg" app. It demonstrates Tower's `run` and `wait` orchestration capabilities.

# Schedule 

This app is supposed to be run on a schedule daily. The app is idempotent and can be re-run multiple times with the same parameters.

# App Dependencies

This app will run multiple instances of the "write-ticker-data-to-iceberg" app in parallel, and with different parameters. 

# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
app. Review the Towerfile, deploy the code, create secrets or catalogs, and run the app!

## Creating and deploying the app

Use the following command from the folder where your Towerfile is

```bash
tower deploy
```

If the app does not yet exist, Tower will suggest creating it.

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
tower run --local \
  --parameter=PULL_DATE="2025-05-01" \
  --parameter=TICKERS="MSFT,AAPL,AMZN,GOOGL,NVDA"
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. 

```bash
tower apps show fan-out-ticker-runs
```

