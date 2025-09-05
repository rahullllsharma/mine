# Worker Safety client

[![Codefresh build status](https://g.codefresh.io/api/badges/pipeline/urbint/Worker%20Safety%2Fworker-safety-client?type=cf-1&key=eyJhbGciOiJIUzI1NiJ9.NWVmMjExNjc2ZDZiMDgyNWY4MWEzYmQ0.VeDbpbnjLO46-8-75GJILduZqg4GtSOImKK8_MkQ9Nk)](https://g.codefresh.io/pipelines/edit/new/builds?id=618c2203742b8e18c1ffe7ea&pipeline=worker-safety-client&projects=Worker%20Safety&projectId=613ae6a7561677409583dff9)

---

## Getting Started

### Pre-requisites

- `NVM` is super useful because our node version is pinned in `.nvmrc` in the
  latest LTS version.

It could be useful to add their script to your shell to
[automatically pick up the current version](https://github.com/nvm-sh/nvm#deeper-shell-integration).

> **Note**
>
> Worker safety uses Next.js as foundation and node is being used for both
> tooling (yarn, etc) as well as runtime for some `api` calls (see
> [API Routes](https://nextjs.org/docs/api-routes/introduction))

> **Warning**
>
> In the time being, the LTS version will always be updated to the next version
> once it's available. This can be troublesome if some major change is made and
> the project is still not prepared (eg. some hardcode dependency like next.js
> still needs to catch up with some functionality removed or breaking change),
> and, thus, should be verified with the team before that upgrade is done.
>
> Both the `.nvmrc`, `dockerfile` and YAML file for codefresh, are locked with
> the latest LTS version (other places, eg, in codefresh could have references
> to LTS versions as well).
>
> For future work, it would be objective to "lock" the LTS version (18.X, 20.X,
> etc...) so "phantom" issues don't popup out of the blue.

### Setup

Before installing make sure you are logged in npm with a github token.

`npm login --scope=@urbint --registry=https://npm.pkg.github.com`

- user: ${YOUR_USERNAME}
- password: ${YOUR_GITHUB_TOKEN}
- email: ${YOUR_GITHUB_EMAIL}

After that:

`yarn install`

#### VSCode setup

1. Using VSCode open the task runner panel with `cmd+shift+p`
2. Type `Tasks: Run Task` and hit enter
3. Select and run `(Re)install dependencies`

### Running

#### Script

Before starting the project you need to add a `.env.local`. You should use
`.env.example` as a starting point.

To complete our `.env.local` please ask Worker Safety team. You can find help
[here](https://urbint.atlassian.net/wiki/spaces/WSAPP/overview#%F0%9F%94%8D-Where-to-find-us).

\*\*Important: Please ensure `NEXTAUTH_SECRET` env var is set on your
.env.local. You can run `npx auth secret` to autogenerate a valid secret but
change the key name, do NOT use AUTH_SECRET as mentioned
[here](https://next-auth.js.org/configuration/options#nextauth_secret)

After that is sorted you can:

```
yarn dev
```

> **Graphql Logging**
>
> If you want to inspect all the requests dispatched, for both server and
> client, just include the flag `APOLLO_LOGGER=1` before starting the
> development server `APOLLO_LOGGER=1 yarn dev`. The logger only works in
> development environments

```
# on the server
apollo query Proiect (in 162 ms)
  INIT {
    variables: { projectId: '53a7d7a9-b657-4d3d-a575-eeda2f44bb5 },
    extensions: {},
    operationName: 'Project',
    query: {
      kind: Document
      definitions: [Object],
      loc: { start: 0, ends 124, }
  RESULT {
    data
      project: {
        id: 153a7d7a9-b657-4d3d-a575-eeda2f44bb5e'
        startDate: '2022-11-01',
        endDate: '2022-11-17',
        __typename: 'Project'

# on the client
apollo querv Permissions (in 858 ms)
apollo querv Proiect (in 858 ms)
```

##### Notes

By default, `yarn dev` will be using `http://localhost:8001` as worker safety
service endpoint.

Make sure that worker safety services are started. You can use the following
command `docker-compose up -d --build`. [^2]

#### VSCode **Run and Debug** section

> If it has runnable code, it has a debugger attached to it.

1. Open the [debugger](https://code.visualstudio.com/docs/editor/debugging)
2. select one of the `Start Dev` options to start the next.js server and launch
   an instance of the app in a controlled instance of Chrome.

<details><summary>Debugger configs</summary>

- `Start Dev - localhost`[^1] [^2] - start the next.js app with env var
  `WORKER_SAFETY_SERVICE_URL_GRAPH_QL="http://localhost:8001"`
- `Start Dev - stating`[^1] - start the next.js app with env var
  `WORKER_SAFETY_SERVICE_URL_GRAPH_QL="https://ws-api.staging.urbinternal.com/graphql"`
- `Start Dev - production`[^1] - start the next.js app with env var
  `WORKER_SAFETY_SERVICE_URL_GRAPH_QL="replace-me-with-production-url"`
- `Start Storybook` - start storybook with an attached debugger
- `Jest tests` - starts jest in watch mode with an attached debugger
</details>

---

## Storybook

TODO: With the LTS node update, storybook was broken.
`export SET NODE_OPTIONS=--openssl-legacy-provider` was added to "fix" this
issue. This needs to be addressed when the node version on the project is
properly updated ( fixed node version for the whole project ).

To run storybook, just execute the following command

```
yarn storybook
```

<details><summary>Mapbox in storybook (feat. Mapbox GL)</summary>

To check the shareable Map component, we need to provide an API key to render
the maps. Storybook provides a way to inject `process.env` variables and used
them inside `stories`.

```
WORKER_SAFETY_MAPBOX_ACCESS_TOKEN=<Mapbox.Token> yarn run storybook
```

Refer to
[Storybook documentation](https://storybook.js.org/docs/react/configure/environment-variables/)
to extend more environment variables.

> ⚠️ To avoid having API keys in the codebase, please ask the team about any
> development mapbox api key. Ask for a key on the `#front-end-engineering`
> slack channel or WS teams related channels.

</details>

---

## Running Worker-Safety-Service pre-built images through docker-compose [^2]

Pulling pre-built images requires authentication to google cloud GCR (Google
Container Repositories). Install gcloud
([homebrew](https://formulae.brew.sh/cask/google-cloud-sdk) or your method of
choice), authenticate to google cloud, authenticate the docker service with
gcloud, and verify you can pull an image.

```bash
brew install --cask google-cloud-sdk
gcloud auth login
gcloud auth configure-docker gcr.io
docker pull gcr.io/urbint-1259/worker-safety-service:latest
```

To start backend services.

```bash
DOCKER_BUILDKIT=0 docker compose build
docker compose up
```

To tear down backend services use

```bash
docker compose down --volumes
```

To fully update bring services down, run both a `pull` and `build`, then bring
services up.

```bash
docker compose down --volumes
docker compose pull  # pulls latest pre-built images
DOCKER_BUILDKIT=0 docker compose build --pull alembic
docker compose up
```

### Google Cloud Platform (GCP) upload/download CORS

By default, Google Cloud Platform (GCP) will reject any request from localhost,
due to CORS.

<details><summary>Upload/Download CORS issues on localhost</summary>

To bypass that limitation locally, we need to hijack the **Response** headers of
any request to `storage.googleapis.com`, and add the header
`Access-Control-Allow-Origin: *`.

#### Steps:

1. Install an extension that handles request/response manipulation like
   [ModHeader](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?src=modheader-com) -
   this extension also exists for Firefox but not for Safari.
2. Include the `Response headers` and add a new header to allow cors
   `Access-Control-Allow-Origin: *`
3. If possible, filter by url `storage.googleapis.com/worker-safety-local-dev`
   to avoid having collisions with the graphql service.

##### Optional, ModHeader Profile

If you already use `ModHeader`, you can simply import this profile

```json
[
  {
    "title": "WSC - localhost",
    "headers": [],
    "respHeaders": [
      {
        "enabled": true,
        "name": "Access-Control-Allow-Origin",
        "value": "*"
      }
    ],
    "shortTitle": "1",
    "alwaysOn": false,
    "version": 2,
    "urlFilters": [
      {
        "enabled": true,
        "urlRegex": ".*://storage.googleapis.com/worker-safety-local-dev/.*"
      }
    ],
    "resourceFilters": [
      {
        "enabled": false,
        "resourceType": ["xmlhttprequest"]
      }
    ]
  }
]
```

</details>

---

## Datadog RUM enablement

In order to enable Datadog RUM while running the FE app locally, the following
ENV VAR are required

`DD_CLIENT_APPLICATION_ID=<DATADOG_CLIENT_ID_VALUE> DD_CLIENT_TOKEN=<DATADOG_CLIENT_TOKEN_VALUE> DD_SAMPLE_RATE=100 DD_PREMIUM_SAMPLE_RATE=100 DD_SERVICE=tm-ws-client DD_ENV=development DD_RUM_ENABLED=true yarn dev`

The ENV VAR `DD_RUM_ENABLED=true` allow us to control when to enable/disable
Datadog on the client.

Then you can access to the RUM dashboard
[here](https://app.datadoghq.com/rum/application/f52d590c-9703-4100-8389-a41e77e00f94/overview/browser?from_ts=1654552872467&to_ts=1654556472467&live=true).

> ⚠️ To avoid having API keys in the codebase, please ask the team about any
> development mapbox api key. Ask for a key on the `#squad-ws-app-devs` slack
> channel or WS teams related channels.

---

## PDF printing (nodejs)

If you need to test the PDF output, it should work out-of-the-box for staging
and production envs. Since it needs a **new external css** file exclusive for
printing, the `build` task will take care of that.

### For development

By default, the external stylesheet is not built for development task. If you
need to test it, just run the task `yarn run dev:print` so it generates the
necessary file.

Check the full docs [here](./docs/PRINTING.md)

> **Warning**
>
> This is the first step to generate PDFs in a server env but not the preferable
> approach. Running puppeteer on the container is painful, in terms of
> resources, specially CPU.
>
> The module should be reused and exposed as an HTTP call to a Google Cloud
> Function (GCF) that is shared cross-application. (preferable approach).

---

## Testing

#### [Testing guidelines E2E](./docs/TESTING.md)

### Playwright

### Install dependencies

- yarn install
- yarn add playwright@1.27.1 --with-deps

#### How to execute tests locally

- First start the next.js server and launch an instance of the app as mentioned
  in the `Running` section above.
- Using the VS Code extension:
  - https://playwright.dev/docs/getting-started-vscode
- Using the CLI:
  - Run smoke tests headless for chromium:
    `yarn play --grep @smoke --project=chromium`
  - Run headed mode: `yarn play:headed --grep @smoke --project=chromium`
  - Run auth.spec.ts for chromium: `yarn play auth.spec.ts --project=chromium`
  - Playwright tests are located at `WORKER-SAFETY-CLIENT/playwright/tests/`
  - Usage e.g.
    - Run pw authentication test for the multiple (desktop and mobile) projects
      in parallel
      - `yarn play auth/auth.spec.ts`
      - ⚠️ not fully tested and with a few failures for parallel runs
    - Run all the playwright (pw) tests for desktop projects
      - `yarn play --project=chromium`
      - `yarn play --project=webkit`
      - `yarn play --project=firefox`
    - Run all the tests for all the projects
      - `yarn play`
      - ⚠️ not fully tested and with a few failures for parallel runs

#### How to execute tests in integ, staging or other environments

- Update config file for the environment to run with the correct password:
  - The config files can be found under support/config folder
  - In order to get the password for the admin role, you should search under
    Engineering 1Password for "Admin User Lens Staging" vault
  - In order to run the admin role, you should pass
    TARGET_ENV=<environment>.admin on the yarn command
- Run headless:
  - `TARGET_ENV=integ.admin yarn play --grep @smoke --project=chromium` ->
    Integrations + Administrator role
  - `TARGET_ENV=staging.admin yarn play --grep @smoke --project=chromium` ->
    NatGrid Staging + Administrator role
  - `TARGET_ENV=staging.viewer yarn play --grep @smoke --project=chromium` ->
    NatGrid Staging + Viewer role
- Run headed mode:
  - `TARGET_ENV=staging.admin yarn play:headed --grep @smoke --project=chromium`

#### [Testing guidelines E2E](./docs/TESTING.md)

---

## Notes

### [How to start the WS container locally?](./docs/LOCAL_DOCKER.md)

### [How to test the printing module locally?](./docs/PRINTING.md)

### [How to start contribuiting?](./docs/CONTRIBUTING.md)

### [Troubleshooting](./docs/TROUBLESHOOTING.md)

### [Frontend Guidelines](./docs/guidelines/GUIDELINES.md)

### [Try the API with Apollo Studio](https://github.com/urbint/worker-safety-service#using-apollo-studio)

### [Trigger risk score recalculation model](./docs/workerSafetyService/RISK_RECALCULATION_MODEL.md)

### [Seed with sample data](./docs/workerSafetyService/SEED.md)

### [Add auto-populated site condition](./docs/workerSafetyService/AUTO_SITECONDITION.md)

---

[^1]:
    will start the next.js server and launch an instance of Chrome with a
    debugger attached to both

[^2]:
    [How to run worker-safety-service in localhost](https://github.com/urbint/worker-safety-service#for-fe-development)
