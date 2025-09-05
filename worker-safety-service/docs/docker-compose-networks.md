# Docker Compose Networks
---
Adding a custom network like `wss_network` in a Docker Compose file allows containers within the same network to communicate with each other using their service names as hostnames. This is particularly useful when you want to isolate your containers and control how they interact with each other.

Here's a brief documentation on adding and using the `wss_network` network in other Docker Compose files:
## Adding wss_network to Docker Compose
1. Network Definition:
  ```yaml
  networks:
    wss_network:
  ```
  This declares a custom network named wss_network in the Docker Compose file. All services listed under this network will be able to communicate with each other using their service names.

2. Adding Services to `wss_network`: 
For each service you want to add to wss_network, include the following line under the service definition:
```yaml
networks:
  - wss_network
```
For example:
```yaml
services:
  graphql:
    # Other service configuration
    networks:
      - wss_network
```
Repeat this for all services you want to include in the `wss_network`.
> [!NOTE]
>
> To activate this network configuration, `execute docker-compose up`. To verify if the network has been successfully created, use the command `docker network ls`. You should observe an output similar to the following:
>```diff
>$ docker network ls
>NETWORK ID     NAME                                DRIVER    SCOPE
>b6b73e8d6681   bridge                              bridge    local
>f2cdaff8f634   host                                host      local
>020323fe570e   none                                null      local
>d64234c09a5d   ticket-lifecycle-services_dev-net   bridge    local
>091d1af89411   worker-safety-service_default       bridge    local
>897f04485068   worker-safety-service_wss_network   bridge    local
>ee57f44d5312   ws-customizable-workflow_default    bridge    local
>```
>`worker-safety-service_wss_network` is the network that is created.
>This will confirm that the `wss_network` has been created and is active within your Docker environment.

## Usage in Other Docker Compose Files
To use the wss_network in another Docker Compose file, you would need to define the same network with the same name (wss_network). This allows containers in different Docker Compose files but within the same network to communicate with each other.

Here's an example of how you can use wss_network in another Docker Compose file:
```yaml
version: '3'

networks:
  worker-safety-service_wss_network:
    external: true

services:
  another_service:
    image: some_image
    networks:
      - worker-safety-service_wss_network
    # Other configurations for the service
```
In this example:
- We define a new Docker Compose file.
- We declare the `worker-safety-service_wss_network` as an external network using `external: true`.
- The `another_service` is then added to the `worker-safety-service_wss_network`/`wss_network` using networks.

## Communication between Containers in `wss_network`

Once containers are added to the `wss_network`, they can communicate with each other using their service names as hostnames. For example, if `graphql` wants to communicate with `postgres`, it can simply use `postgres` as the hostname since they are on the same network:
```python
# Inside graphql container
POSTGRES_HOST = "postgres"
```
This resolves to the correct container because they are on the same network.

Example to setup networks on other docker compose file:
```yaml
version: '3'

networks:
  worker-safety-service_wss_network:
    external: true

services:
  cwf-rest:
      build:
        context: .
        target: uvicorn
      container_name: rest-api
      command: --reload ws_customizable_workflow.main:app --port 5001
      volumes:
        - ./ws_customizable_workflow:/app/ws_customizable_workflow
        - ./support/uvicorn/mute.logging.conf:/app/uvicorn.logging.conf
      ports:
        - "5001:5001"
      depends_on:
        - mongodb
      environment:
        - CORS_ORIGINS=["http://localhost:3000", "http://localhost:5001", "http://localhost"]
        - MONGO_HOST=mongodb
        - MONGO_USER=root
        - MONGO_PASSWORD=password
        - MONGO_DB=asgard
        - MONGO_PORT=27017
        - WORKER_SAFETY_SERVICE_REST_URL=http://rest:8000
        - WORKER_SAFETY_SERVICE_GQL_URL=http://graphql:8000
      networks:
        - worker-safety-service_wss_network
```
In the above example the `rest` and `graphql` services are called using their respective service name because it is all in the same network even if the docker compose file is different, and note that the port number will be the container port not the host port.

## Benefits of Using a Custom Network

**Isolation**: Services in wss_network can communicate with each other but are isolated from services outside this network.

**Service Discovery**: Docker manages DNS resolution within the network, so you can refer to services by their names.

**Control**: You have more control over which services can communicate with each other by placing them in the same network.

Remember to start your containers using `docker-compose up` with the appropriate compose file to ensure they join the `wss_network`.

This setup helps in organizing and structuring your containers, especially when dealing with multiple services that need to communicate in a controlled and isolated environment.

---


