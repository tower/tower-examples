# DLTHUB pipeline reading files into Snowflake

All of this running in Tower :tokio_tower:! 

# Setup for DLT development

This is how you get DLT up and running on your laptop during development,
including setting up dependencies.

## Create a Snowflake trial account

## Set up a new Snowflake database and users

Run script snowflake_create_database.sql
- modify the script and replace the password of the user LOADER
- After the script is done you will have the MANGO_DATA database, the RAW schema in this database, 
the LOADER user in Snowflake to be used by DLT

## Configure the secrets and config of DLT
```bash
cp .dlt/secrets.toml.template .dlt/secrets.toml 
```
In the .dlt/secrets.toml file, replace the placeholders in the credentials config
destination.snowflake.credentials="snowflake://..."

## Install Snowflake DLT dependencies
```bash
pip3 install "dlt[snowflake]"
pip3 install -r requirements.txt
```

## Run the DLT pipeline
python3 pipeline.py

This pipeline will create the CAP_UTILIZATION table in the RAW schema and 
load it with the data from the ./data/fedres/FRG_G17.csv file

# Setting up Tower

Tower uses the associated Towerfile to figure out how to deploy your
application. Once it's ready to go, you just have to deploy the code, create a
secret, and give it a run!

## Creating the app

The app name matches whats in the Towerfile in this directory.

```bash
$ tower apps create --name=dlthub-pipeline
```

## Deploying the app

Use the following command

```bash
$ tower apps deploy
```

## Creating the secrets

We create this secret in Tower and it's automatically passed in to your DLT
program. Tower automatically integrates with DLT!

The value should match what's in your `secrets.toml` file.

```bash
$ tower secrets create --name=dlt.destination.snowflake.credentials --value='snowflake://...'
```

## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

```bash
$ tower apps run
```

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
$ tower apps logs dlthub-pipeline#1
# ...
```
