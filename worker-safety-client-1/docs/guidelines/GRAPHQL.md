# GraphQL

> Query only the data you need, where you need it [^1]

Each component can (and should) query exactly the fields it requires to render,
avoiding querying unnecessary data thus preventing larger payloads to be sent.

We can use `fragments` to distribute the structure of a single query between
several components.

## Fragments

Fragments are reusable units that represent a set of data to query from a
GraphQL type exposed in the schema.

Fragments are building blocks that can describe the data requirements of a given
component and they can be used to compose a query.

Colocating components with their data dependencies.

By using a colocating fragment strategy, the component is decoupled from the
query that renders it. We can change the data dependencies for the component
without having to update the queries that render them or worrying about breaking
other components.

Thus, we make it more scalable and easier to maintain.

Code example

```graphql
fragment LocationCoordinate on ProjectLocation {
  latitude
  longitude
}
```

## External sources

[Colocating fragments](https://www.apollographql.com/docs/react/data/fragments/#colocating-fragments)

[Fragments](https://graphql.org/learn/queries/#fragments)

---

[^1]:
    [Query only the data you need, where you need it](https://www.apollographql.com/docs/react/data/operation-best-practices/#query-only-the-data-you-need-where-you-need-it)
