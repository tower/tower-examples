from pyiceberg.catalog import load_catalog
import polars as pl
import os

# Review https://www.tabular.io/apache-iceberg-cookbook/getting-started-python-configuration/
# on how to pass catalog configuration parameters
# Either use the .pyiceberg.yaml file or pass 4 environment variables e.g.
# PYICEBERG_CATALOG__DEFAULT__URI=<https://... for REST catalogs>
# PYICEBERG_CATALOG__DEFAULT__CREDENTIAL=<client_id>:<client_secret>
# PYICEBERG_CATALOG__DEFAULT__SCOPE=PRINCIPAL_ROLE:<principal_role_your_configured>
# PYICEBERG_CATALOG__DEFAULT__WAREHOUSE=<catalog_identifier>
# The catalog name "default" must be in the config file or in env variable names
catalog = load_catalog("default")

iceberg_table_name= os.getenv("iceberg_table")

# follows the tutorial https://py.iceberg.apache.org/#connecting-to-a-catalog
# also this tutorial https://www.tabular.io/apache-iceberg-cookbook/pyiceberg-polars/

icetable = catalog.load_table(iceberg_table_name)

# create a Polars dataframe
df = pl.scan_iceberg(icetable)

# see this dataset for code values
# https://www.kaggle.com/datasets/zanjibar/japantradestat
# exp_imp: 1 is export, 2 is import
# hs2 to hs9 are goods classification codes
# Q1, Q2 is quantity. http://www.customs.go.jp/toukei/sankou/howto/yougo_e.htm
# Value is in 1000s of Yen

df2 = (
    df.select([
        pl.col("ym"),
        pl.col("exp_imp"),
        pl.col("Value")
    ])
    .group_by(["ym", "exp_imp"])
    .agg(pl.col("Value").sum().alias("total_value"))
    .collect()
    .pivot(
        values="total_value",
        index="ym",
        columns="exp_imp",
        aggregate_function="first"
    )
    .rename({"1": "exports", "2": "imports"})
    .sort("ym")
)

print("\n=== Japan Trade Statistics by Month ===")
print("Month    | Exports (1000s Yen) | Imports (1000s Yen)")
print("-" * 60)
for row in df2.iter_rows():
    month, exports, imports = row
    print(f"{month}  | {exports:,} | {imports:,}")
print("=" * 60)
