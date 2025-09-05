import type { GetServerSideProps } from "next";
import type { FC } from "react";
import { useEffect } from "react";
import { ApolloError } from "@apollo/client";
import { authenticatedQuery } from "@/graphql/client";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import Permissions from "../graphql/queries/permissions.gql";

/**
 * @deprecated
 * earlier used as default callback url for keycloak; now replaced by /api/auth/callback/keycloak
 * this page should never require navigating to;
 * if done will redirect to `b` query-param value (dangerous, should refactor!)
 */
export const Login: FC<{ message: string; reload: boolean }> = ({
  message,
  reload,
}): JSX.Element => {
  useEffect(() => {
    // We need a reload in order to send the token from keycloak to the SSR
    // server via a cookie. Note, if the user is already logged in, she is
    // redirected to `/`. This happens by virtue of the `redirect: {...}` field
    // in the `getServerSideProps`.
    if (reload && typeof window !== "undefined") {
      window.location.reload();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <PageLayout className="h-screen flex flex-col mx-4 md:mx-6 lg:mx-8">
      {message}
    </PageLayout>
  );
};

export default Login;

/**
 * @deprecated
 * Importance notice: This function always needs to be unauthenticated. Hence
 * it can not pull from the Graphql API.
 *
 * @param context
 * @returns
 */
export const getServerSideProps: GetServerSideProps = async context => {
  const redirect = context.query?.["b"] ?? "/";
  try {
    // This call is _merely_ to verify that the user is indeed logged in.
    // There might be much better ways
    await authenticatedQuery(
      {
        query: Permissions,
      },
      context
    );

    // The user was logged in. Redirect back
    return {
      redirect: {
        destination: redirect,
        permanent: false,
      },
      props: {},
    };
  } catch (e) {
    // Apollo related errors
    if (e instanceof ApolloError) {
      // Short-circuit function if error is unknown
      if (e.networkError === null) {
        return {
          props: {
            message: "Unknown Apollo error",
            reload: false,
          },
        };
      }

      // Specific scenario related with tenant
      if (
        "result" in e.networkError &&
        e.networkError.result.detail.includes("No such tenant")
      ) {
        return {
          props: {
            message: "Tenant not configured",
            reload: false, // Just let the message be there
          },
        };
      }
    }

    // Generic Errors
    const normalizedMessage = ((e as Error).message || "").toLowerCase();

    if (!normalizedMessage) {
      // Edge case in case message is not defined
      return {
        props: {
          message: "Generic Error",
          reload: false,
        },
      };
    }

    if (normalizedMessage.includes("received status code 400")) {
      // Server responds with a 400
      return {
        props: {
          message:
            "Bad request. Contact admin to make sure proper roles are configured",
          reload: false, // Just let the message be there
        },
      };
    }

    if (normalizedMessage.includes("received status code 403")) {
      // Server responds with a 403
      // This response should always be because of invalid access token as
      // the me query should not be restricted further than requiring login.
      return {
        props: {
          message: "Initializing.",
          reload: true,
        },
      };
    }

    if (normalizedMessage.includes("connect econnrefused")) {
      // Server is not available
      return {
        props: {
          message: "Server unavailable.",
          reload: false, // Just let the message be there
        },
      };
    }

    if (normalizedMessage?.includes("unexpected token")) {
      return {
        props: {
          message: "Bad request. App not properly configured",
          reload: false, // Just let the message be there
        },
      };
    }

    console.log("Did not recognize exception", e);
    // Assume the user was not logged in. Show the login page, which will
    // redirect to the Keycloak login page
    return {
      props: {
        message: "Waiting to login",
        reload: true,
      },
    };
  }
};
