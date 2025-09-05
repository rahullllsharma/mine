# Testing guidelines E2E

## How to add tests

- UI tests: Add integration tests for specific features rather than an
  end-to-end approach.
- Playwright tests are located at `WORKER-SAFETY-CLIENT/playwright/tests/`
- A solid test generally covers 3 phases:
  - Set up the application state
  - Take an action
  - Make an assertion about the resulting application state

For more details, see
[how to write a Playwright test](https://playwright.dev/docs/intro#first-test)

## Best Practices

- Use data-\* attributes to provide context to your selectors and isolate them
  from CSS or JS changes. E.g The **data-test-id** attribute to select an
  element rather than targeting the text content.
- If you repeat some steps for all the tests in a single file, you can move them
  inside the "**beforeEach**” function. It will execute those commands before
  each test starts.
- Sometimes you have to wait until the API call ends. You can use the Route
  method for this. It eliminates the unnecessary PLaywright waiting times.
  - [Playwright on response interception](https://playwright.dev/docs/release-notes#response-interception)
- More best practices:
  [Playwright doc best practices on selectors](https://playwright.dev/docs/selectors#best-practices)

## How to structure tests to be resilient

- Utilize Fixtures and POM to set up the application in a particular state.
  - This allows us to save a few headaches by skipping UI interaction and
    jumping straight to a desired state that we want to test.
  - For example: if we're testing adding a task, we need to have a project
    created first. Rather than creating a project through the UI as part of the
    add task test, we can use app actions instead.
  - Detailed explanation:
    [Playwright fixtures](https://playwright.dev/docs/test-fixtures)
    [Playwright POM](https://playwright.dev/docs/test-pom)
- Make tests deterministic.
  - Understand the goal of the test and add valuable assertions
  - If a test has too many steps and assertions, it will be harder to debug, and
    probably warrants it being broken up.
  - It is not necessary to add an assertion after each step
- Ensure tests are independent.
  - A test should not depend on the resulting state of a previous test.
  - Tests should be able to be run in isolation and in parallel.
- Don't repeat assertions across tests. If one test verifies the home page is
  displayed after login, no need to re-verify that in another test.
- It is recommended to keep test runtime under 30 seconds, optimal if it takes
  under 10 seconds.
- Avoid use of implicit waits
- Don't just check that the test passes before committing. Also check that the
  test fails when it should.

## How to debug

- Utilize one of the following package.json scripts to start live debugging
  - `yarn play:debug` -> `"play:debug": "PWDEBUG=1 playwright test"`
  - `yarn play:debug-console` ->
    `"play:debug-console": "PWDEBUG=console playwright test"`
- Utilize one of the following package.json scripts to increase verbosity on
  logging
  - `yarn play:debug-log-api` ->
    `"play:debug-log-api": "DEBUG=pw:api playwright test"`
  - `yarn play:debug-log-browser` ->
    `"play:debug-log-browser": "DEBUG=pw:browser playwright test"`
  - `yarn play:debug-log-all` ->
    `"play:debug-log-all": "DEBUG=pw:browser,pw:api,pw:protocol,pw:proxy,pw:error playwright test"`
  - [Playwright docs on logger tags](https://github.com/microsoft/playwright/blob/e76edef3e226e95ecc6f2071b8c4f9bce478bedf/packages/playwright-core/src/utils/debugLogger.ts#L20-L31)
- For more details consult
  [Playwright docs on debugging](https://playwright.dev/docs/debug)
- Utilize Playwright Trace Viewer that helps exploring recorded Playwright
  traces after the script ran
  - `yarn play:trace <path for trace file>`
- Documentation:
  - https://playwright.dev/docs/trace-viewer

## How to play with codegen and generate test file

- Playwright comes with the ability to generate tests out of the box. To run it
  over http://localhost:3000, you can execute the following script:
  - `yarn play:codegen`
- Documentation:
  - https://playwright.dev/docs/codegen

## How to run locally with docker

- `docker pull mcr.microsoft.com/playwright:latest-focal`
- `docker run -v $PWD:/tests -w /tests --rm -it mcr.microsoft.com/playwright:latest-focal /bin/bash`
- Copy ~/.npmrc file to the container root folder, using the container ID as
  follows:
  - `docker cp ~/.npmrc 3cb941578a56:/root`
  - [Why?](https://github.com/urbint/worker-safety-client/blob/main/docs/TROUBLESHOOTING.md#troubleshooting)
- `npm install --location=global yarn`
- `yarn install`
- `yarn add playwright --with-deps`
- locally ->
  `BASEURL=http://host.docker.internal:3000 yarn play auth/auth.spec.ts --project=chromium`
- staging ->
  `TARGET_ENV=staging.admin yarn play auth/auth.spec.ts --project=chromium`
- To access the report files the user can copy them from container to local,
  using the container ID as follows
  - `docker cp 3cb941578a56:/tests/playwright/report/ .`
- Documentation:
  - [Playwright docs for docker](https://playwright.dev/docs/docker)
  - [E2E testing with Playwright and Docker](https://medium.com/geekculture/e2e-testing-with-playwright-and-docker-91dd7eb11793)

## Notes

storageState.json is generated automatically by playwright from the cookies set
in the application.

To test, open an incognito tab and check the localhost:8080 cookies.
