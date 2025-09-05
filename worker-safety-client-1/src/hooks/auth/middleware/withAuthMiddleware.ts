import { getServerSession } from "next-auth";
import { initializeApollo } from "@/graphql";
import { stripTypename } from "@/utils/shared";
import Permissions from "@/graphql/queries/permissions.gql";
import { getNextConfig } from "@/utils/auth";

/**
 * Authentication Middleware
 *
 * With keycloak, we need to call the identity server to verify that the user is a valid one.
 *
 * TODO: We should move this into a global middleware that protects some routes, using the _middleware approach.
 * It has a few caveats (due to edge functions) but we should be able to bypass its limitations.
 */
const withAuthMiddleware: AuthMiddlewareHandler =
  callback => async (req, res) => {
    // This is just an example of how to filter http verbs not supported
    if (req.method !== "GET" || !req?.url) {
      res.status(405);
      return res.send("");
    }

    const nextConfig = await getNextConfig(req);
    const token = (await getServerSession(req, res, nextConfig))?.accessToken;

    try {
      const { data, errors } = await initializeApollo().query({
        query: Permissions,
        context: {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      });

      if (errors) {
        res.status(403);
        return res.send("User not authenticated");
      }

      // TODO: Move to a custom middleware share the information down to other resources
      const protocol =
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        req.headers["x-forwarded-proto"] || req.connection.encrypted
          ? "https"
          : "http";

      const { origin } = new URL(
        req.url || "",
        `${protocol}://${req.headers.host}`
      );

      req.locals = {
        ...req.locals,
        connection: {
          protocol,
          origin,
          isSecure: protocol === "https",
        },
        user: {
          ...stripTypename(data).me,
          entities: data.me?.tenant.configurations.entities,
        },
      };
    } catch (err) {
      res.status(401);
      return res.send("");
    }

    return callback(req, res);
  };

export { withAuthMiddleware };
