from pyiceberg.catalog import load_catalog
import polars as pl

# Review https://www.tabular.io/apache-iceberg-cookbook/getting-started-python-configuration/
# on how to pass catalog configuration parameters
# Either use the .pyiceberg.yaml file or pass 4 environment variables e.g.
# PYICEBERG_CATALOG__DEFAULT__URI=<https://... for REST catalogs>
# PYICEBERG_CATALOG__DEFAULT__CREDENTIAL=<client_id>:<client_secret>
# PYICEBERG_CATALOG__DEFAULT__SCOPE=PRINCIPAL_ROLE:<principal_role_your_configured>
# PYICEBERG_CATALOG__DEFAULT__WAREHOUSE=<catalog_identifier>
# The catalog name "default" must be in the config file or in env variable names
catalog = load_catalog("default")

# follows the tutorial https://py.iceberg.apache.org/#connecting-to-a-catalog
# also this tutorial https://www.tabular.io/apache-iceberg-cookbook/pyiceberg-polars/

icetable = catalog.load_table("default.japan_trade_stats_2017_2020")

# create a Polars dataframe
df = pl.scan_iceberg(icetable)

# see this dataset for code values
# https://www.kaggle.com/datasets/zanjibar/japantradestat
# exp_imp: 1 is export, 2 is import
# hs2 to hs9 are goods classification codes
# Q1, Q2 is quantity. http://www.customs.go.jp/toukei/sankou/howto/yougo_e.htm
# Value is in 1000s of Yen

df2 = (
    df.filter(
        (pl.col("exp_imp") == '1')
    ).collect().select([
        pl.col("ym"),
        pl.col("Value")
    ]).group_by(['ym']).sum().sort("ym")
)

print(df2)