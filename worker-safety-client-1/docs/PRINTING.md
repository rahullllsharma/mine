# Printing

This docs serve as guidance for printing documents and reports from worker
safety. At the moment, the printing service is only available for daily reports
but it can be extended for other areas.

## Pre-requisites

- Chrome or Chromium browser installed

> The main package `puppeteer-core` only includes the bindings to plug puppeteer
> and an instance of chrome available in the machine. That way, we don't force
> to download an separated binary just for puppeteer.

## How to run

You need to boot `worker-safety` and include a new env variable called
`PUPPETEER_EXECUTABLE_PATH`, eg, for macos

```
PUPPETEER_EXECUTABLE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
```

This will identify where the chrome's binary is located in the system.

### Include styles (mostly for development)

After booting the instance, we need to generate the custom stylesheet used for
the printing page. To do that, manually run `yarn dev:print` command and it will
generate the file.

> **Note** Why is this command not baked into the standard `yarn dev` command?
>
> Because the stylesheet is mainly static and we should only built it, whenever
> we need it.

The template is generated at SSR time and parse as a HTML string and then
outputted as a PDF buffer.

#### Why parse the template in the container server?

Mainly because it's easier to just reuse the components built for Worker Safety,
specifically.

## Running with the container

This should be very similar to the instructions needed to run the container.

> **Warning** To have a closer experience to production, prepare the `build`
> folder before booting the container

```sh
# With a previously built image, create a container based of the dockerfile.
# For this example, it includes some restrictions to the container like cpu and memory and it will switch the entry point so WS will NOT start automatically
docker run -p 3000:3000 -v $(pwd)/:/app -it --memory="2g" --cpus="2.0" --name wsc-container --entrypoint /bin/sh wsc

# Then ssh into the container
docker exec -it wsc-container /bin/sh

# (inside the container)
cd /app
yarn start (boots in a production like env)
```

## (NEAR) future

Generating PDFs and other files in the same POD as the instance is (very)
expensive. It will stress the container in memory and, specially, in **cpu**
cycles, thus, this is a start but SHOULD NOT the final destination.

We should be able to migrate this, relatively easy and cheap, to a Google Cloud
Function (GCF) and only export the PDF on demand (and removing puppeteer from
the container)

**PDO/Server/Nodejs**

- **GET** _/api/daily-report/<daily-report-id>/print_
  - Auth Middleware (global)
  - Permissions Middleware (per route)
  - (controller) Generates the HTML template
  - (controller) Calls the `GCF` to generate the PDF and other stuff
  - (controller) Proxies the buffer back from the CF

**Cloud/GCF**

- CF `Generate PDF` (from a string, generate the PDF Buffer)
- CF `Zip Buffers` (we could extend and have a custom CF either to only zip
  buffers (nodebuffers) or create a CF that will replace the code in WS)
