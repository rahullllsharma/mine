declare module "*.gql" {
  import type { DocumentNode } from "graphql";

  const Schema: DocumentNode;

  export = Schema;
}

declare module "*.graphql" {
  const Schema: DocumentNode;

  export = Schema;
}
