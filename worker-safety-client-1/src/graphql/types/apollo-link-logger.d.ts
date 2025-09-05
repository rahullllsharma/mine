declare module "apollo-link-logger" {
  import type { ApolloLink } from "@apollo/client";

  const linkLogger: ApolloLink;
  export default linkLogger;
}
