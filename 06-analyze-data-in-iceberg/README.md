# Analyze an Iceberg table and create an aggregation report, all by using Polars and no DucksDB

All of this running in Tower!

# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
application. Once it's ready to go, you just have to deploy the code, create a
secret, and give it a run!

## Creating the app

The app name should match what's in the Towerfile in this directory.

```bash
$ tower apps create --name=analyze-data-in-iceberg
```

## Deploying the app

Use the following command

```bash
$ tower deploy
```

## Adding an Iceberg catalog

You need to add a reference to your Iceberg catalog in the Tower app. Name the
catalog `default` as that's what we expect it to be here.

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
$ tower run --local \
 --parameter=ANALYZE_DATE='2025-04-11'
```

To run on Tower cloud, remove --local

## Check the run status

You can use the following command to see how the app is progressing. Again, no
need to supply an app name as long as you're in a directory with a Towerfile.

```bash
$ tower apps show
```

## Get the run logs

You can use the following command to see what happened with your run. You need
to supply an app name as well as a run number. Use the `show` command to get
both of those values.

```bash
$ tower apps logs analyze-data-in-iceberg#1
```
