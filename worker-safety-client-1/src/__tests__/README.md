# API Testing (for server routes only!)

> **warning** This is only to start some documentation on how should we handle
> tests on the few api routes that we currently have.

Given the way Nextjs handles API routes, we cannot add the spec into the `pages`
folder, otherwise, it will be copied to the `.build` folder. So, the common
approach, is to create `__tests__` folder at the `@/src` folder and replicate
the structure on the `pages/api/*` folder and files.

## How to mock requests?

TBC

## Examples
