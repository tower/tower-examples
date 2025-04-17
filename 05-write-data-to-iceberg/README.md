# Read csv file from S3 and write an Iceberg table

All of this running in Tower!


# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
application. Once it's ready to go, you just have to deploy the code, create a
secret, and give it a run!

## Creating the app

The app name should match what's in the Towerfile in this directory.

```bash
$ tower apps create --name=write-data-to-iceberg
```

## Deploying the app

Use the following command

```bash
$ tower deploy
```

## Setup our Iceberg Catalog

You need to create a new catalog with name `default` (which the Tower SDK looks
for by default) to run this app successfully. You can do this in the Tower app.


## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
$ tower run --local \
  --parameter=FILE_DATE='2025-03-18'
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
$ tower apps logs write-data-to-iceberg#1
# ...
```
