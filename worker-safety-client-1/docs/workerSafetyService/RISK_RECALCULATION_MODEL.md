# Risk Recalculation model

In order to run the risk recalculation model, execute the following command in
your `graphql` docker container

```
wss risk-model recalculate --update-incident-data --update-library-data --spawn-worker
```

## How to get the docker container?

### Command line:

- Open a terminal and run `docker ps`
- Copy the **Container ID** corresponding to the `graphql` instance
- Run `docker exec -it <CONTAINER_ID> /bin/bash`
- Run
  `wss risk-model recalculate --update-incident-data --update-library-data --spawn-worker`

### Docker desktop app:

- Go to the list of containers and click in the **CLI** button
- <img width="362" alt="Screenshot 2022-06-06 at 08 50 07" src="https://user-images.githubusercontent.com/88859702/172118751-89f0e604-e60b-44e5-932d-cc08878a6753.png">
- Once the terminal is open, type `exit` and press enter
- Press arrow up and replace `/bin/sh` by `bin/bash` and press enter
- <img width="879" alt="Screenshot 2022-06-06 at 08 51 52" src="https://user-images.githubusercontent.com/88859702/172119011-3d6ebc85-cb4a-40ed-901c-1b02dc59c7c2.png">
- Run
  `wss risk-model recalculate --update-incident-data --update-library-data --spawn-worker`
