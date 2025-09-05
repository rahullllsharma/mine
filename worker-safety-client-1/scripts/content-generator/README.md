# Content creation scripts

This folder has a couple of scripts to create content in Worker-Safety.

## Configs file

The configs file controls the environment you can point to. Below is an example
of some configs.

```
{
  "environment": "localhost",
  "projects": {
    "newEntries": 3000,
    "chunks": 10,
    "chunkDelay": 1500,
    "chunkFormationDelay": 100,
    "projectNamePrefix": "Script dummy project"
  }
}
```

The values about will point to `localhost`. It will create 3000 projects ( aka
work packages ) and will chunk these in groups of 10. This is to minimized the
load on the BE size and do all the requests in one go.

`projectNamePrefix` will be used to create new project names and will be used as
the search param to delete projects.

You can tweak the `chunkDelay` and `chunkFormationDelay`, however for localhost
the minimum values that more than 500 project creation required were 1500 and
100 respectively.

- `chunkDelay` - is the delay feature chunk fetching. The chunk is requested all
  together in a `Promise.all`. This delay is applied per chunk, so in the
  example above it will run 300 times ( 3000 / 10 ).
- `chunkFormationDelay` - is the delay when forming the groups. This delay is
  applied for every project entry, so you in the case above it will run 3000
  times.

You might need to tweak this values while pointing at different environments.
The possible environments are accessible in the folder `playwright/config/` and
for the file name you should add the part after `.env`. So in the example above
`"environment": "localhost",` will target the file `.env.localhost`.

## Run the script

To run the scripts it was created 2 new scripts in the package.json file

- generate:create-project
- generate:delete-project

Just configures the configs file, run `yarn generate:create-project` and you can
go get a coffee.

With the example above some duration reference where:

- 500 projects - Done in 128.85s.
- 1000 projects - Done in 255.69s.
- 2000 projects - Done in 508.30s.
- 3000 projects - Done in 761.63s.
