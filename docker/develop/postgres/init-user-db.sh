#!/usr/bin/env bash

set -e

# Create the necessary user and databases
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d template1 <<-EOSQL
    CREATE USER dbuser WITH PASSWORD 'dbpassword';

    CREATE DATABASE rss_reader_db;

    GRANT ALL PRIVILEGES ON DATABASE rss_reader_db TO dbuser;
    ALTER USER dbuser CREATEDB;
EOSQL
