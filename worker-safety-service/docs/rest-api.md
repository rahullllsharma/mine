# Worker Safety Rest API Documentation

## Application Layout
```
worker_safety_service/rest    # Location of all Rest API Code
├─ api_models/                # Rest API interface models & Generic model builder
├─ dependency_injection/      # FastAPI DI for data_loaders and data access layer (dal) managers
├─ openapi/                   # Code to support OpenAPI specification tooling
├─ routers/                   # Route definitions for API endpoints
├─ __init__.py
├─ exception_handlers.py      # Endpoint exception handling
├─ main.py                    # Application setup and configuration
```

## Getting an OpenAPI spec.
To generate a specification from a local install either 
- use the cli: `wss rest-spec current -o your_spec.yaml`
- or the app endpoint: `http://localhost:8000/rest/openapi.yaml`

For higher environments the app endpoint is usually best.
- integration : https://ws-api.integ.urbinternal.com/rest/openapi.yaml
- staging     : https://ws-api.staging.urbinternal.com/rest/openapi.yaml
- production  : https://ws-api.urbint.com/rest/openapi.yaml

You can limit the generated specification to any of the API routers defined in `worker_safety_service/rest/routers/__init__.py::OpenapiSpecRouters`.
- cli   : `-l activities -l ...`
- http  : `?limit=activities&limit=...`

### Configuring the Generated Specification.
There are many options to extend the generated specification with extra information. For a full reference see the FastAPI documentation for detailed OpenAPI settings and extensions: https://fastapi.tiangolo.com/advanced/extending-openapi/

We customize the specification to add authentication settings in `worker_safety_service/rest/main.py::custom_openapi` as well as adding the required `Oauth2` auth and scopes to each endpoint. 

## Generating documentation in Stoplight
Paste the generated specification file contents into the stoplight editor to generate the stoplight API reference, etc.

- go to : https://urbint.stoplight.io/studio/worker-safety-api-spec?
- "edit" the current specification
- replace the contents with the generated yaml file

## Generating documentation from FastAPI
FastAPI publishes a documentation page using `redoc` at `/rest/redoc` and an interactive OpenAPI UI at `/rest/docs`. These are available locally and in integration.

## Adding New Endpoints
New endpoints should prefer the `create_models` method to help ensure a [consistent JSONAPI interface](https://jsonapi.org/format/). See existing routers for examples.

Endpoints should use a data_loader provided by the DI module to ensure the REST Api uses the same logic as other parts of Worker Safety.
