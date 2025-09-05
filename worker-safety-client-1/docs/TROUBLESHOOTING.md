# Troubleshooting

## Cannot download to @urbint/silica (Hard Hat DS)

When downloading the dependencies, you may run into this.

```sh
➜  worker-safety-client git:(main) yarn
yarn install v1.22.17
[1/4] 🔍  Resolving packages...
[2/4] 🚚  Fetching packages...
error An unexpected error occurred: "https://npm.pkg.github.com/download/@urbint/silica/1.3.1/0aa2b6a8a86035904ca969b91033081e8eb0a3c418519714753775638f3f91be: Request failed \"401 Unauthorized\"".
```

It means you need access to [@urbint/Silica](https://github.com/urbint/silica)
which is a private repo. Follow the installation guide found
[here](https://github.com/urbint/silica#installation).
