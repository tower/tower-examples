-- --
-- This is the contents of file snowflake_create_database.sql
-- --

---> set the Role
USE ROLE accountadmin;

---> set the Warehouse
USE WAREHOUSE compute_wh;

DROP DATABASE IF EXISTS mango_data;
DROP USER IF EXISTS loader;
DROP ROLE IF EXISTS dlt_loader_role;

---> create the Mango Database
CREATE OR REPLACE DATABASE mango_data;

---> create the Raw Schema for ingesting data
CREATE OR REPLACE SCHEMA mango_data.raw;

-- create new user - set your password here
CREATE OR REPLACE USER loader WITH PASSWORD='<pwd>';

-- we assign all permission to a role
CREATE OR REPLACE ROLE dlt_loader_role;
GRANT ROLE dlt_loader_role TO USER loader;

-- give database access to new role
GRANT USAGE ON DATABASE mango_data TO dlt_loader_role;

-- allow access to COMPUTE_WH
GRANT USAGE ON WAREHOUSE compute_wh TO dlt_loader_role;

-- grant access to all future schemas and tables in the database
GRANT ALL PRIVILEGES ON SCHEMA mango_data.raw TO dlt_loader_role;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN SCHEMA mango_data.raw TO dlt_loader_role;