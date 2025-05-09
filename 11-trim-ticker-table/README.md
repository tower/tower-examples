# Trimming an Iceberg table and removing old data
This app will inspect the "daily_ticker_data" table and remove all records from it 
that are older than the specified Time Window parameter. 


# Schedule and Dependencies

This app is supposed to be run on a schedule daily. It complements the "write-ticker-data-to-iceberg" app that acquires new daily ticker stats and populates 
the "daily_ticker_data" table. This app is idempotent and can be re-run multiple times with the same parameters.


# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
app. Review the Towerfile, deploy the code, create secrets or catalogs, and run the app!

## Creating and deploying the app

Use the following command from the folder where your Towerfile is

```bash
tower deploy
```

If the app does not yet exist, Tower will suggest creating it.

## Defining an Iceberg catalog

You will need to tell us about your Iceberg catalog in the [Tower UI](https://app.tower.dev). Use the catalog slug `default` as that's what this sample app expects it to be called.

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
tower run --local \
 --parameter=TIME_WINDOW_DAYS="31"
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. 

```bash
tower apps show trim-ticker-table
```

