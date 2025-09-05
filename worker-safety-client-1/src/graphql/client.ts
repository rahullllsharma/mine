/* istanbul ignore file */
import type {
  GetServerSideProps,
  GetServerSidePropsContext,
  NextApiRequest,
} from "next";
import {
  ApolloError,
  from,
  type ApolloQueryResult,
  type OperationVariables,
  type QueryOptions,
} from "@apollo/client";
import { StatusCodes } from "http-status-codes";
import { getServerSession } from "next-auth";
import { setContext } from "@apollo/client/link/context";
import { getNextConfig } from "@/utils/auth";
import { devApolloLinks, errorLink, httpLink, initializeApollo } from ".";

export const authGetServerSidePropsProxy = async (
  context: GetServerSidePropsContext,
  f: () => ReturnType<GetServerSideProps>
) => {
  try {
    return await f();
  } catch (e) {
    // has been made specific based on https://github.com/apollographql/apollo-link/issues/300#issuecomment-518445337
    if (
      e instanceof ApolloError &&
      e.networkError &&
      "statusCode" in e.networkError &&
      [StatusCodes.UNAUTHORIZED, StatusCodes.FORBIDDEN].includes(
        e.networkError.statusCode
      )
    ) {
      return {
        redirect: {
          destination: `/auth/signin?callbackUrl=${context.resolvedUrl}`,
          permanent: false,
        },
        props: {},
      };
    }
    throw e;
  }
};

/**
 * Query with authentication
 *
 * Note: everything passed takes higher precedence.
 *
 * @param options
 * @returns
 */
export const authenticatedQuery: <T = any>(
  options: QueryOptions<OperationVariables, T>,
  context: GetServerSidePropsContext
) => Promise<ApolloQueryResult<T>> = async (options, context) => {
  const { req, res } = context;
  const nextConfig = await getNextConfig(req as NextApiRequest);
  const client = initializeApollo();
  const authLink = setContext(async (_, { headers }) => {
    const token = (await getServerSession(req, res, nextConfig))?.accessToken;
    return {
      headers: {
        authorization: token ? `Bearer ${token}` : "",
        ...headers,
      },
    };
  });
  client.setLink(from(devApolloLinks.concat([errorLink, authLink, httpLink])));

  return client.query(options);
};
