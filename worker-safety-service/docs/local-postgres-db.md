# Running a local postgres instance with worker safety

The postgres docker container is convenient for running the application and getting started with the project but is orders of magnitude slower than a local postgres instance. This guide will help you setup a local postgres instance to take advantage of the performance increase.

# Install Postgres

Installing postgres can be done through brew with: `brew install postgresql@14`. Additional information on brew install configuration can be found using `brew info postgres`. The default configuration seems fine for what we use.

# Starting the service

Stop the existing docker container or map the port `5432` to something different on the host and restart it. You can ensure the service is not running or is running on a different port use with `docker ps`. Check if the local postgres install is running with `brew services info postgresql` and start it if it is not running `brew services run postgresql`. To enable persistent restart after reboot run `brew services start postgresql`.

# Running tests

First connect to the service with `psql postgres` and create a `postgres` role using `create role postgres with superuser createdb createrole login;`. This matches our default test connection configs. Assuming you are able to run the application locally you should be able to run the tests locally as well using `POSTGRES_DB=p_test poetry run pytest -v -n 8`
