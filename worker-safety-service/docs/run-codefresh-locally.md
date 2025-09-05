# How to run a codefresh build Locally
A short guide on how to [run a codefresh pipeline using your local machine](https://codefresh.io/docs/docs/configure-ci-cd-pipeline/running-pipelines-locally/) as the runner. The end result is the same as triggering a build in codefresh manually or through a push to the git repo but instead the build is executed using your local machine as the codefresh runner.

## Install Docker
Use the [official guide](https://docs.docker.com/get-docker/) if not already installed.

## Install cli tool
Install the [Codefresh CLI tool](https://codefresh-io.github.io/cli/installation/) using [homebrew](https://codefresh-io.github.io/cli/installation/homebrew/) if on a mac.

## Create token
Authenticate to codefresh and navigate to the [user settings page](https://g.codefresh.io/user/settings). Create an API token and grant at least the following scopes
- Build:read
- Build:status
- Pipeline:read
- Pipeline:run
- Pipeline:write

Click `OK` to create the token and then `Copy token to clipboard`. 

## Authenticate cli
Using the key name and api key you just generated run

```bash
codefresh auth create-context [key name] --api-key [api key]
```

## Find project id
For some reason the `codefresh run` command does not seem to like spaces in the pipeline name. If you need to run a pipeline with a space in the name first get the `id` for the pipeline using:
```bash
codefresh get pipelines -o wide
```

## Execute local build
Ensure your changes are pushed to github and execute the pipeline locally.

```bash
# push any changes to github
git commit -m "..."
git push origin [branch]

# execute the build
# -b              : specify the branch to pull from github
# --local         : use the local machine as the runner
# --local-volume  : use the local machine for the shared volume
# --yaml=[file]   : use a custom yaml pipeline file
# -v              : Set a pipeline variable (can be set multiple times)
codefresh run 6185774620bb9af77d12ff73 -b=$(git branch --show-current) --local --local-volume --yaml=codefresh.yml -v CF_BRANCH=$(git branch --show-current)
```

## Execute the build on the server

Sometimes, it's important to test the pipeline on the server.
In this case, it is important that we get the trigger right. 
Otherwise, most of the environment variables will not be set.

```
codefresh run 6185774620bb9af77d12ff73 -b=$(git branch --show-current) -t urbint/worker-safety-service --yaml=codefresh.yaml
```
