# Authentication
Authentication happens through Keycloak that is running as a service.

## Updating Realm
Realms are exported from the current Keycloak instance to be imported for new
developer. In order to make updates to the Keycloak development realms:

1. make the changes in the web interface
2. export the realm by using following command (the the `asgard` realm):
   ```
   docker-compose exec keycloak \
     /opt/jboss/keycloak/bin/standalone.sh \
       -Dkeycloak.migration.provider=singleFile \
       -Dkeycloak.migration.realmName=asgard \
       -Dkeycloak.migration.usersExportStrategy=REALM_FILE \
       -Dkeycloak.migration.file=/realms/asgard.json \
       -Djboss.socket.binding.port-offset=100 \
       -Dkeycloak.migration.action=export
   ```
3. Stop the image when there is not more progress, which usually is when the
   container has logged:
   ```
   INFO  [org.jboss.as] (Controller Boot Thread) WFLYSRV0060: Http management interface listening on http://127.0.0.1:10090/management
   INFO  [org.jboss.as] (Controller Boot Thread) WFLYSRV0051: Admin console listening on http://127.0.0.1:10090
   ```
4. Commit and PR the changes

__Note:__ Before new imports are active, the previous realm needs to be
recreated.

## Standard Users
There are a number of users already present in the database. As convention the
passwords for the development users is `password`.

## Keycloak Setup
Keycloak admin console will be available on http://localhost:8080/auth/admin/master/console/ using `user: admin, password: admin` as creadentials.

### Realm
We provide a preconfigured realm called `asgard` with all clients, roles and users created and ready to use.

### Clients
We provide a preconfigured client to facilitate the local development requests:
  - client_id: local-dev
  - client_secret: XErS42uXDD2uJIcDrvjhchw2daeO5XdT

### Users
(TODO: add roles to users export)

We provide 4 users, representing the 4 roles:
  - Admin
    - name: super
    - password: password
  - Manager
    - name: bill
    - password: password
  - Supervisor
    - name: bobby
    - password: password
  - Viewer
    - name: hank
    - password: password

## Exceptions
### Authentication
Authentication is considered to be outside the scope of graphql so we will use HTTP status codes to represent errors:
- Missing token: `status: 400, body:{"detail": "No access token provided"}`
- Token expired: `status: 403, body:{"detail": "Token expired}`
- Token decoded error: `status: 403, body:{"detail": "Token could not be decoded`

### Authorization
(TODO: implement authorization)
Authorization errors are handled inside the graphql scope thus will return 200 HTTP status code and have a type associated with the details

## How to get and use the token
To get this token we can call the Keycloak token endpoint. for this you can use the local-dev client configuration

```shell
curl --request POST \
  --url http://localhost:8080/auth/realms/asgard/protocol/openid-connect/token \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data client_id=local-dev \
  --data client_secret=XErS42uXDD2uJIcDrvjhchw2daeO5XdT \
  --data scope=openid \
  --data username=super \
  --data password=password
```

Then we take the `access_token` from the response and send as an header: `"Authorization": "Bearer <token>`

```shell
curl --request POST \
  --url http://localhost:8001/graphql/ \
  --header 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3elBrZjBtMWNFWmFkUTE5S0NkaC1GcHVsYTB3Z25iRDh0S2ltM1RlUm9jIn0.eyJleHAiOjE2NDMzMDYwOTQsImlhdCI6MTY0MzMwNTc5NCwianRpIjoiZjkwNTU2NTItODJjYy00NjNjLWEyYjctMGE0MTIzN2FkMDNkIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL2F1dGgvcmVhbG1zL2FzZ2FyZCIsImF1ZCI6WyJ3b3JrZXItc2FmZXR5LXdlYiIsImFjY291bnQiXSwic3ViIjoiMTM1YzQzNWQtYjBhNS00MTJmLWE3NjUtZWVhMmNlM2NiNGI5IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiaW5zb21uaWEiLCJzZXNzaW9uX3N0YXRlIjoiNDUzN2Q5MGMtMWNhNy00ZWQyLTllZGQtZWQzMThkOTE0ZjE1IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLWFzZ2FyZCIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ3b3JrZXItc2FmZXR5LXdlYiI6eyJyb2xlcyI6WyJBZG1pbmlzdHJhdG9yIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwic2lkIjoiNDUzN2Q5MGMtMWNhNy00ZWQyLTllZGQtZWQzMThkOTE0ZjE1IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiU3VwZXIgVXNlciIsInByZWZlcnJlZF91c2VybmFtZSI6InN1cGVyIiwiZ2l2ZW5fbmFtZSI6IlN1cGVyIiwiZmFtaWx5X25hbWUiOiJVc2VyIiwiZW1haWwiOiJzdXBlckBlbWFpbC5sb2NhbC51cmJpbnRlcm5hbC5jb20ifQ.bu5mQE8wBdZGEYy8SE5KX37Oc-bNWYyRp4LXkf13PLBOEzP_SsFBbbAyjNrLTw8QtxRm2U0MM3UlSTFpjkBSkaL_iGSH9kGPSM39ot56VNUu30M9DlffdA74vxwK84lVat0YR32K2gnP4aspv_RLPUUI5KJrsv7bvMI_FovGcbEM77UakcU4Fzns-aDesD6qWbs9UNgu42GGjLWtxiiz9O9zFgk96DrC81ExmByVVLixpgOWc-F4HefGJlnJkmS-JxRa9oORqI655IPjTk_vTLepzrsGBJlvVKNKP8Pjzn7ip1rUjPdMRSxgO2KUcclxWt4ZiIj8u9feirz-fVtXnw' \
  --header 'Content-Type: application/json' \
  --data '{"query":"query me{\n\tme {\n\t\tid\n\t\tfirstName\n\t\tlastName\n\t\tname\n\t}\n}","operationName":"me"}'
```

## Insomnia (Optional)
We recomend using [Insomnia](https://docs.insomnia.rest/) as HTTP client and provide a shared [collection](.support/insomnia/ws-collection.json) to abstract away most of the authorization logic on dev environment.

### Setup
Install and import the provided collection file

### Generating Authorization token for reports API

Reports APIs (`/reports`) which are used by our customers to ingest forms data into their PowerBI systems has a separate authorization mechanism-
1. Use /rest/reports_token to generate token for accessing reports API.
2. This API takes single form type param ie. `user_name` a.k.a email_id of user. 
3. The authentication for this reports token generation API uses default keycloak user token.
4. The tenant id will be extracted from this token's user to fetch tenant in order to filter out the reports based on tenant id
5. Token lifespan is configurable and is set to 180 days in config.

API documentation can be found at - https://urbint.atlassian.net/wiki/spaces/WSDD/pages/4223172667/BI+reports+API+for+EBO+JSB+daily+reports

