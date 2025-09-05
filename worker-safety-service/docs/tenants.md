# Tenants
Tenants are used for customer separation in worker safety. Tenants are an
application level construct and as such there are a number of things we need
to be aware of.

The core principle of a tenant is, that it should not be possible to retrieve
data from a tenant _other_ than the one the user is authenticated for.

To provide tooling around tenants, the data loaders are made in such a way that
they always respect tenants

__Specifying tenants on requests:__ Tenants are specified in the token provided
from Keycloak. The tenant is resolved based on the external auth provider field
in the tenant model. This implementation is currently strictly bound to the
way Keycloak formats their "iss" (issuer) field in their token.

As a consequence tenants are derived from the used auth token and there should
be no need to specify them otherwise either in the URL or in other ways.

__Creating a new tenant:__

1. Generate a realm input file `wss tenant new-realm [tenant_name] [tenant_display_name] [tenant_url] > [filename].json`.
2. Import that realm into keycloak on the [add realm page](http://localhost:8080/auth/admin/master/console/#/create/realm)
3. In Keycloak, add users, email configuration, etc as required and double check realm settings.
4. create the tenant in the application: `poetry run wss tenant create [tenant_subdomain_name] [tenant_name]`

__Development tenant:__ There is already an olympus realm running for the
purpose of setting up another tenant in development. It can be completely
activated by:

1. add `127.0.0.1       olympus.ws.local` to your `/etc/hosts` file
2. run `poetry run wss tenant create olympus olympus`
3. Navigate to [olympus.ws.local:3000](http://olympus.ws.local:3000/)
4. Login with super / password

**Note:** When running the backend, make sure that the right CORS origins are
added. Eg. by running:

```
CORS_ORIGINS='["http://localhost:3000", "http://olympus.ws.local:3000"]' poetry run uvicorn --reload worker_safety_service.graphql.main:app
```

The frontend is assumed to be run on port 3000 as setup per default.
