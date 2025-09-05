/* istanbul ignore file */
import type { NormalizedCacheObject } from "@apollo/client";
import fetch from "cross-fetch";
import { ApolloClient, HttpLink, InMemoryCache, from } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";
import getConfig from "next/config";
import { offsetLimitPagination } from "@apollo/client/utilities";
import { getSession, signIn } from "next-auth/react";
import { config } from "@/config";

console.log(
  `ApolloClient going to be instantiated with: ${config.workerSafetyServiceUrlGraphQL}`
);

const isSSR = typeof window === "undefined";
const configs = getConfig();
const runtimeConfig = isSSR
  ? configs?.serverRuntimeConfig
  : configs?.publicRuntimeConfig;

export const devApolloLinks =
  runtimeConfig?.APOLLO_LOGGER === "1"
    ? // eslint-disable-next-line @typescript-eslint/no-var-requires
      [require("apollo-link-logger").default]
    : [];

export const errorLink = onError(({ networkError }) => {
  if (networkError) {
    if (!isSSR) void signIn("keycloak", { redirect: true });
  }
});

export const httpLink = new HttpLink({
  uri: `${config.workerSafetyServiceUrlGraphQL}/graphql`,
  fetch,
});

const authLink = setContext(async (_, { headers }) => {
  const token = (await getSession())?.accessToken;
  if (!token) console.error("No token attached in authlink!! SSR: %o", isSSR);
  return {
    headers: {
      authorization: token ? `Bearer ${token}` : "",
      ...headers,
    },
  };
});

let apolloClient: ApolloClient<NormalizedCacheObject>;
function createApolloClient() {
  return new ApolloClient({
    defaultOptions: isSSR ? { query: { fetchPolicy: "network-only" } } : {},
    cache: new InMemoryCache({
      typePolicies: {
        Query: {
          fields: {
            projects: offsetLimitPagination(),
          },
        },
      },
    }),
    link: from(devApolloLinks.concat([errorLink, authLink, httpLink])),
    ssrMode: isSSR,
  });
}

/**
 * Always create a new apollo client instance on the server.
 * Creates or return apollo client in the browser.
 */
export function initializeApollo(): ApolloClient<NormalizedCacheObject> {
  // For SSG and SSR always create a new Apollo Client
  if (isSSR) {
    return createApolloClient();
  }

  // For CSR, singleton Apollo Client
  if (!apolloClient) {
    apolloClient = createApolloClient();
  }

  return apolloClient;
}
