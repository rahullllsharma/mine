# Running Superset
We run an instance of superset for internal urbint use. To test or debug locally or to try out superset with worker safety you can enable the docker compose profile and configure the docker compose `postgres` database which has the worker safety DB.

_*NOTE:*_ if you delete the supersetdb volume you _will lose_ all configured databases, datasets, dashboards, charts, etc. Save these with `pg_dump` if you need to remove the `supersetdb` volume.

### Run superset
Superset configuration is mostly automatic thanks to the existing work and configuration done for lens. Since we don't use superset as a part of the application it is not enabled by default in docker compose. To enable it add `--profile superset` to docker compose commands.

```
docker compose --profile superset up
```

### Login
An admin user is created for you to login with once superset is up and running.

[superset](http://localhost:8090)
admin username: superset
admin password: superset

### Add the worker-safety database
You need to manually add the worker-safety DB to superset as well as any datasources and charts that are helpful. Right now, as this isn't part of the app, we do not have any dashboards or charts.

##### In Top left nav
Data > Databases

##### In Top Right
`+ Database`

Select Postgresql and add the compose DB (for macs).
These values should match the docker-compose settings for the `postgres` db.
host: `host.docker.internal`
port: `5432`
database name: `postgres`
username: `postgres`
password: `password`
display name: `worker-safety`

### etc
Superset should now have a connection to your local DB (or swap the connection details for another DB you want to try) and you can import datasources and begin looking around!
