# Seed data

We have a script to create some sample data. Check the main reference in
[Worker Safety Service](https://github.com/urbint/worker-safety-service#seed-sample-data)

**note**: By using the seed, the current database data will be wiped out, so if
we need to preserve that data, we need to dump the database first.

## How to run it?

- Open a terminal and run `docker ps`
- Copy the **Container ID** corresponding to the `graphql` instance
- Run `docker exec -it <CONTAINER_ID> /bin/bash`
- Run `. /venv/bin/activate` - the virtualenv should be activated first
- Run `pip install poetry` - in `/app` is required to install `poetry`
- Run `poetry install` - will install the missing 'dev' dependencies
- Run `poetry run seed` - run the backend seed Typer app

Or you can run everything in once:

`docker exec -it <CONTAINER_ID OR CONTAINER_NAME> /bin/bash -c ". /venv/bin/activate; pip install poetry; poetry install; poetry run seed"`

> **Warning** It's possible that `poetry run seed` does not work. In that case,
> try running the command `poetry run seed seed` instead.
