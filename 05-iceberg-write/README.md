# Read csv file from S3 and write an Iceberg table

All of this running in Tower!


# Deploying app to Tower cloud

Tower uses a manifest file called Towerfile to figure out how to deploy your
application. Once it's ready to go, you just have to deploy the code, create a
secret, and give it a run!

## Creating the app

The app name should match what's in the Towerfile in this directory.

```bash
$ tower apps create --name=iceberg-write
```

## Deploying the app

Use the following command

```bash
$ tower deploy
```

## Creating the secrets

We create these secrets in Tower and they are automatically passed to your app.

To access S3, we need to define AWS credentials

```bash
$ tower secrets create --name=AWS_ACCESS_KEY_ID --value='AK...'
$ tower secrets create --name=AWS_SECRET_ACCESS_KEY --value='ABC...'
```

To access the Polaris catalog, we need to define another credential. 
Three additional settings to access the Polaris catalog will be passed to the app
via parameters.

```bash
$ tower secrets create --name=PYICEBERG_CATALOG__DEFAULT__CREDENTIAL --value='o...=:L...='
```


## Running the app

You can run the app using the Tower CLI. You don't need to specify a name, it
will figure out what app to run based on the Towerfile.

To run locally

```bash
$ tower run --local \
 --parameter=PYICEBERG_CATALOG__DEFAULT__SCOPE='PRINCIPAL_ROLE:...' \
 --parameter=PYICEBERG_CATALOG__DEFAULT__URI='https://...snowflakecomputing.com/polaris/api/catalog' \
 --parameter=PYICEBERG_CATALOG__DEFAULT__WAREHOUSE='...'	
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
$ tower apps logs iceberg-write#1
# ...
```
