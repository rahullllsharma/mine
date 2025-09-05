# worker-safety-service

[![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/urbint/Worker%20Safety%2Fworker-safety-service?type=cf-1&key=eyJhbGciOiJIUzI1NiJ9.NWVmMjExNjc2ZDZiMDgyNWY4MWEzYmQ0.VeDbpbnjLO46-8-75GJILduZqg4GtSOImKK8_MkQ9Nk)]( https://g.codefresh.io/pipelines/edit/new/builds?id=6185774620bb9af77d12ff73&pipeline=worker-safety-service&projects=Worker%20Safety&projectId=613ae6a7561677409583dff9)

> Doing the work behind the scenes to keep workers safe

## Requirements
- Python (3.10.4)
- [Poetry](https://python-poetry.org/)
- [Docker](https://docker.com)
- Docker Compose
- Postgres

## Quick Start

### Clone the repo
``` shell
git clone git@github.com:urbint/worker-safety-service.git
cd worker-safety-service
```

### Run the App and backing services
``` shell
docker-compose up

# on M1 macs - you may need to disable buildkit
# https://urbint.atlassian.net/wiki/spaces/PLAT/pages/3405250567/Local+Dev+on+M1+Mac#Docker-Compose-Execution
DOCKER_BUILDKIT=0 docker-compose up

# on M1 macs, you might also need to comment this line
# in the docker-compose.yml file:
platform: linux/amd64
```

By default, the docker-compose will **not** run the risk-model worker which is necessary for the automatic risk recalculations.
In order to enable the automatic recalculations we need to use the `with-risks` profile. 
However, this mode will consume more resources.

`docker-compose --profile "with-risks" up`

Note: In order to be able to run the project, ensure that Docker has permissions to read "Files and Folders". More relevant to fresh install machines.

### Try the API
The graphql application runs at [`localhost:8001`](http://localhost:8001). The app provides an interactive GraphQL interface at [`localhost:8001/graphql`](http://localhost:8001/graphql). You must provide an access token (jwt) from keycloak to authenticate. `ModHeader` is a nice way to inject Authorization headers: [chrome](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en) and [firefox](https://addons.mozilla.org/en-US/firefox/addon/modheader-firefox/). Generate a JWT with the following curl.

``` shell
curl -s --request POST \
  --url localhost:8080/auth/realms/asgard/protocol/openid-connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=worker-safety-asgard \
  --data scope=openid \
  --data username=super \
  --data password=password
```

This command will copy the JWT directly to clipboard.
``` shell
# You can use `jq` to parse the json response from keycloak
# and `pbcopy` to pull the value directly into the mac clipboard
brew install jq
curl -s --request POST \
  --url localhost:8080/auth/realms/asgard/protocol/openid-connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=worker-safety-asgard \
  --data scope=openid \
  --data username=super \
  --data password=password | jq -r .access_token | pbcopy
```

#### Using Apollo studio
[Apollo Studio](https://studio.apollographql.com/) can be used to interact with the GraphQL API directly. You can create account using your github account. With the application running, choose `+ New Graph`, select Development graph type, and set the URL to [`localhost:8001/graphql`](http://localhost:8001/graphql). Click Add header and add `Authorization` and `Bearer <access token>`, and replace `<access token>` with the JWT token from the shell command above.

To enable automatic token generation, while in the Apollo Studio Explorer, click the cog Settings icon, edit the connection setttings and set the Authorization header to exactly `Bearer {{ACCESS_TOKEN}}`. Click Save and then under "Preflight script" click Edit script and paste in JavaScript below. Click save, ensure that preflight script is enabled, and then refresh the browser.

``` javascript
const openidConnectTokenUrl = 'http://localhost:8080/auth/realms/asgard/protocol/openid-connect/token';

const grant_type = "password";
const client_id = "worker-safety-asgard";
const scope = "openid";
const username = "super";
const password = "password";
const data = `grant_type=${grant_type}&client_id=${client_id}&scope=${scope}&username=${username}&password=${password}`

const response = await explorer.fetch(openidConnectTokenUrl, {
    method: 'POST',
    headers: {
        "Content-Type":"application/x-www-form-urlencoded"
    },
    body: data,
})

const token = JSON.parse(response.body);
explorer.environment.set("ACCESS_TOKEN", token.access_token)
```

### Useful commands

A dev utility is implemented in `./support/scripts/dev/main.py` - you can see
all the commands with `poetry run dev --help`. At the time of writing:

``` shell
❯ poetry run dev --help
Usage: dev [OPTIONS] COMMAND [ARGS]...

  Worker Safety dev support commands.

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  deps                        Installs deps from poetry.
  docker                      Starts the usual dev docker containers.
  docker-graphql-log          Follows the logs from the graphql app...
  docker-graphql-rebuild      Rebuilds the graphql app container.
  lint                        Runs our auto-formatters, then runs all the...
  migrate                     Bring your local db up to date.
  migration-downgrade         Downgrade your local database.
  migration-generate          Generate a new migration.
  migration-new               Create a new migration.
  prep                        `deps` + `docker` + `migrate`
  test-all                    `test-unit` + `test-integration`
  test-integration            Runs the integration tests.
  test-integration-fail-fast  Runs the integration tests, but exits on...
  test-match                  Runs tests matching the provided match_str.
  test-unit                   Runs the unit tests.
```

## Development Setup

### Install system dependencies
``` shell
brew install postgres
```

### Install python dependencies and virtualenv
This project requires Python 3.10.x. We recommend using [`pyenv`](https://github.com/pyenv/pyenv) to manage python versions and [`poetry`](https://python-poetry.org/) for virtual environments and dependencies.

<details>
  <summary>Pyenv install</summary>

  ``` shell
  brew install pyenv
  # from pyenv github readme under `zsh` setup
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
  echo 'eval "$(pyenv init -)"' >> ~/.zshrc
  source ~/.zshrc

  # install python 3.10.4
  pyenv install 3.10.4

  # Set local version
  pyenv local 3.10.4
  ```
</details>

<details>
  <summary>Poetry install</summary>

  brew install poetry
</details>

``` shell
poetry install
```

### Setup autohooks
Autohooks is a Python library that assists in automated formatting and linting using Black and Pylint during git commits. This feature aids in identifying and addressing linting and typing issues in code before committing, thereby minimizing build pipeline failures resulting from such issues.

For further details on Autohooks, please refer to this URL: https://pypi.org/project/autohooks/

Autohooks utilizes the setup.cfg file to configure details for various libraries such as isort, flake8, and mypy. The settings for Autohooks are specified in the pyproject.toml file.

Run the following command to activate autohooks after the `poetry install` command:

```shell
poetry run autohooks activate --mode poetry
```

### Start the application

#### Main GraphQL API
``` shell
poetry run uvicorn --reload worker_safety_service.graphql.main:app
```

#### External Rest API
``` shell
poetry run uvicorn --reload worker_safety_service.rest.main:app
```

## Additional Setup

### Seed sample Data
We have a script that will create some sample data in the app. It does require completing the local dev setup.
```shell
poetry run seed
```
Note: when running backend services using docker compose
```shell
POSTGRES_DB="postgres" poetry run seed
```

More on seeding can be found [below](#Seeding).

### Configure Google Cloud Storage
To use features of the app that use Google Cloud Storage you must download the authentication file for Google Cloud Storage from 1Password. It is in the engineering vault - you may need to request access to the engineering vault in freshservice if you do not have that yet.
- Search for "worker-safety-local-dev-storage-account-key" in the Engineering Vault in 1Password
- Copy the "note" into `.google-dev-service-account.json` (root of repo)
- set this env var where you run the application: `export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/.google-dev-service-account.json`
- Start the application

Alternatively you can use the 1Password CLI and `jq` to get the credentials!
```bash
brew install --cask 1password-cli
brew install jq

# Authenticate using `op signin`
# This command requires you follow some setup instructions.
# Make sure to store any keys or tokens in a safe location
# and follow the steps printed in the command output!
op signin urbint.1password.com [your urbint email address]
op get item "worker-safety-local-dev-storage-account-key" | jq -r .details.notesPlain > .google-dev-service-account.json
```

The tests for file storage should now run
```bash
pytest -vv --durations=0 tests/integration/mutations/test_file_storage.py
```
### Configure Firebase
 To use features of the app that use Firebase you must download the authentication file for Firebase from 1Password. It is in the engineering vault - you may need to request access to the engineering vault in freshservice if you do not have that yet.
 - Search for "worker-safety-firebase-credentials" in the Engineering Vault in 1Password
 - Copy the "note" into `.firebase-dev-service-account.json` (root of repo)
 - set this env var where you run the application: `export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/.firebase-dev-service-account.json`
 - Start the application
 
## For FE development
If you are not working on the BE you may just need to run `docker compose up`. That will start all BE services on the ports listed below.

| Service     | URL                   | PORT |
|-------------|-----------------------|------|
| GraphQL API | http://localhost:8001 | 8001 |
| Keycloak    | http://localhost:8080 | 8080 |
| Redis       | http://localhost:6379 | 8000 |
| Postgres    | localhost             | 5432 |

## Migrations
Migrations are implemented with [alembic](https://alembic.sqlalchemy.org/en/latest/). They will be automatically applied to the docker postgres container when running `docker compose up`.

Full conversation on migrations can be found in the [migrations README](migrations/README.md).
### Upgrade database to latest migration revision
The following command will update the database to the latest migration using the default configuration in `config.py`
``` shell
poetry run alembic upgrade head
```
### Create a new revision manually
The following command will create a new empty revision file in the `migrations/versions` directory.
``` shell
# Create an empty revision file
poetry run alembic revision -m "A new empty revision"

```
### Create a new revision automatically
Alembic can attempt to automatically generate a revision file based on changes to the models. It's not perfect, however, and all migrations should be inspected for correctness.
``` shell
# Autogenerate a revision file after updating model definitions
poetry run alembic revision -m "An autogenerated revision" --autogenerate
```

### Using docker compose
You may also run alembic commands through docker compose.
```bash
docker compose run alembic upgrade head
docker compose run alembic revision -m "A new empty revision"
docker compose run alembic revision -m "An autogenerated revision" --autogenerate
```

## Project Layout
Summary of top-level project organization.
```
├── README.md               # You are here!
├── Dockerfile              # Used for deployments and local docker-compose
├── docker-compose.yml      # Used for development only
├── poetry.lock
├── pyproject.toml
├── docs                    # Supplemental info to the README
├── migrations              # Database migrations using alembic
│   ├── archive             # Original set of migrations (before squashing)
│   ├── fixtures            # Data files & raw sql for migrations
│   └── versions            # Current Migrations
├── support                 # Supporting code for local dev and deployments
├── tests                   # Tests tests and more tests!
│   ├── integration         # Tests requiring external services (postgres, redis, etc)
│   └── unit                # Tests using only mocks
└── worker_safety_service   # Main application module
    ├── audit_events
    ├── cli                 # Typer CLI
    ├── dal
    ├── gcloud              # Google Cloud access (GCS)
    ├── graphql
    ├── ingestion
    ├── keycloak            # Authentication
    ├── models
    ├── rest
    ├── risk_model
    ├── routers
    ├── site_conditions
    ├── urbint_logging
    ├── config.py           # Common configuration settings
    ├── exceptions.py
    ├── middleware.py
    ├── permissions.py
    ├── types.py
    └── utils.py
```

## Environment Variables Listing
See class attributes of `Settings` in [`worker_safety_service/config.py`](https://github.com/urbint/worker-safety-service/blob/main/worker_safety_service/config.py).


## CLI Usage
The `worker_safety_service.cli` module compiles the implementation of a series of command-line-activated features. All functions are bound to the `wss` command, and a list of commands can be obtained using `wss --help`.

### Ingestion Commands
Ingestion commands necessitate that the folder/bucket data is registered for a given tenant. IngestionSettings can be added/updated using the command `wss ingest settings <tenant_id> <bucket_name> <folder_name>` - this will define the path the ingestion commands will use to fetch files.
There are two ways to trigger ingestion and recalculation - one specific and one global:
- `wss ingest check-and-process <tenant_id>` will check for new files, ingest them and trigger recalculations for a single tenant
- `wss script update-tenants` will check for new files, ingest them and trigger recalculation for every tenant that has an IngestionSettings entry.

There is also an option to run locally:
`wss ingest check-and-process {tenant_id} --local-path {path}`
Please note: The filename must include the terms `incident` or `observation` to trigger processing of incidents or observations, respectively.

### Risk Calculation
Several CLIs can be used to interact with the Risk Model.
They are under: `wss risk-model {COMMAND}`

These scripts will not spawn any workers by default. They will only add new requests to the Risk Model Reactor, which by default will use the central Redis queue. As a result, you need to make sure that there are workers running that can handle those requests.

Staging and Production have dedicated daemon workers always running. However, this is not the case locally. Therefore, you need to run the docker-compose with the `with-risk` profile (see `Using docker compose` above). Alternatively, you can run a worker manually.

The Risk Model CLI scripts also have a couple of options that enable spawning a worker alongside the script.
`--spawn-worker --mode daemon|local|isolated`

Risk Model Reactor modes:
** Daemon
This mode spawns the Risk Model Reactor workers as a background process that will not stop running until explicitly stopped. This mode only works with the Redis queue.
** Local
In this mode, the Risk Model Reactor worker spawns locally. It will use the Redis queue. However, unlike the daemon workers, local workers will yield execution as soon as possible; most notably, in the first time the queue is empty.
** Isolated
In the isolated mode, the worker will be created with a dedicated queue (in memory). It will work completely separately from other workers. This mode will also impact the Risk Model Reactor API, because the whole reactor will use the in-memory dedicated queue.

Debugging can be tricky.  While breakpoints can be set in the CLI code, setting breakpoints other files, such as DAL files, may crash the worker.


## Development Guide Lines
### Module Boundaries
#### Data Access Layer (`worker_safety_service.dal`)
The `worker_safety_service.dal` module is the principal user of our data models and is where all data accessor methods should live. This functionality is captured within `Manager` classes. `Manager`s are named with grouping of accessor functionality put together but they are not limited to only those models (i.e. `ProjectManager` contains functionality related to tasks and site conditions in addition to projects).

`Manager`s should be completely ignorant of their consumers.

`Manager`s may make external service calls.

#### GraphQL (`worker_safety_service.graphql`)
The `worker_safety_service.graphql` module is the gateway to our data and contains all GraphQL types, queries, and mutations. It is responsible for authorizing that the consumer of the GraphQL API can access the features and data they are requesting and returning is valid.

##### Context
The GraphQL context is built via the `get_context` method. It contains information about the consumer of the GraphQL request (i.e. user information) as well as any functionality that must be shared amongst GraphQL resolvers (i.e. data access via `Loader`s).

##### Loaders
`Loader` classes are used within GraphQL resolvers to request data from the `dal` and other external services (i.e. Google Cloud Storage). They make use of [dataloaders](https://github.com/graphql/dataloader) to consolidate data requests across resolvers when needed.

`Loader`s are tenant aware, meaning that they are responsible for validating that the authenticated user is authorized to access the tenant data being requested.

### Client/Server Contract Design Process
1. Review acceptance criteria to determine required types, queries, and mutations
2. Create initial schema design proposal document
3. Create draft PR with schema document under `docs/contract-proposals`
4. Discuss and adjust design with front end engineer
5. Finalize PR and get required approvals

### SQLModel implementations to keep in mind

- SQLModel table classes (table=True), don't do pydantic validations
- SQLModel model updates don't have pydantic validations
- SQLModel don't validate/parse data fetched from DB using pydantic, just returns what's saved in DB and parsed by sqlachemy. So, we need to keep in mind that sqlalchemy do the DB parse, sqlalchemy configs should be well defined

Check `tests/integration/test_sqlmodel.py` for more details

### GraphQL Naming Conventions
#### Types
- Capitalized `CamelCase`
- Singular

#### Queries
- Prefer nouns over verbs
  - i.e. `projects` over `getProjects`

## Testing
Managed using **Pytest**.
### Execute tests
- `poetry run pytest` to trigger all tests
- `poetry run pytest -m unit` to only trigger tests that are marked as *"unit"*
- `poetry run --cov=worker_safety_service --cov-report html` to generate a coverage report
- `poetry run -n auto --ignore=./tests/integration/risk_model` to run tests in parallel (skip risk_model tests as the tests don't support running in parallel with redis yet.)

### Using the Python Debugger
Placing `breakpoint()` in a test case or in application code will open a python debugger at that point in the code. The debuger opens in the same place you are running tests. Since it pauses test execution the test database will also be available in postgres.
The [python docs](https://docs.python.org/3/library/pdb.html) have a good summary of PDB options.


### Types of test
- Unit: tests that are isolated from the database, external api calls and other mockable internal code.
- Integration (TBD)
- API (TBD)

## Seeding

A backup of the seed script lives in the repo, and can be used to quickly
restore the state of the database:

```shell
poetry run seed restore-from-backup
```

Note that this will clear all your database tables, so be sure that's what you
want first!

`restore-from-backup` only imports the data from the backup, and requires that
the database migrations have already run. Perhaps more useful is
`create-from-backup`:

```shell
poetry run seed create-from-backup
```

This command is more "from scratch":

- Drops and recreates the database
- Runs the migrations
- Restores the data from the backup file

This command is likely useful for CI - we should be able to run this in
codefresh to get a working copy of the database in place.

### Updating the seed (after adding a migration)

Recreating the backup is a good idea whenever a migration is added, tho it isn't
always technically necessary.

After writing the new migration, the backup can be regenerated like this:

```shell
poetry run seed recreate-backup
```

This command will:

- Drop and recreate the `settings.POSTGRES_DB` database
- Run the migrations
- Generate new data via the `seed` command
- Overwrite the backup file with the new `seed` data

### Other commands

There are a few other commands available - `--help` lists them all:

```shell
poetry run seed --help
```

Or see the `support/scripts/seed/main.py` file for more docstrings and implementations.

---

In particular, `seed` or `reseed` can be helpful while working on the seed generation
itself. `reseed` will create a freshly migrated db and then re-run `seed`.

```shell
poetry run seed reseed
```

---

To seed data for an additional second tenant at the same time, the `--additional-tenant` flag can be used.

``` shell
poetry run seed seed --additional-tenant
```

### Docker Networks
[This](docs/docker-compose-networks.md) document outlines the recent changes made to our Docker Compose configuration, specifically the introduction of a custom network named `wss_network`. This network facilitates improved communication and isolation between containers within our application ecosystem. Below, you'll find details on the network setup, its benefits, and how to utilize it in your Docker Compose configurations.
