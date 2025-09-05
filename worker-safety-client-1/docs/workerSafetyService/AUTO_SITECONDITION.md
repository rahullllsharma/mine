# Add auto populate site condition

We have a script that can be called to trigger an auto populated site condition.

## How to create an auto populated site condition?

- Add a location with coordinates: `Latitude: 37.926661` and
  `Longitude: -122.356419`
- Add the task `Locates / Mark-outs` (no need to change hazards and controls)
- Go to the docker container where graphql is running
  - Open a terminal and run `docker ps`
  - Copy the **Container ID** corresponding to the `graphql` instance
  - Run `docker exec -it <CONTAINER_ID> /bin/bash`
- Execute the risk model calculation trigger by executing the following command
  - `wss risk-model recalculate --update-incident-data --update-library-data --spawn-worker`
- Go to WS web application and refresh the page
- Crime site conditions should have been added (this is the auto populated site
  condition)
- Click to open it and check that it is disabled
