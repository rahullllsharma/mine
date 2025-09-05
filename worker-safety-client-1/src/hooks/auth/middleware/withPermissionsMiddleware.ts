/**
 * Permissions Middleware
 *
 * Protects a route if the user doesn't have permissions to access the route. This is based on its role.
 *
 * TODO: We should move this into a per-route basis middleware that protects some routes, using the _middleware approach.
 * It has a few caveats (due to edge functions) but we should be able to bypass its limitations.
 */
const withPermissionsMiddleware: AuthMiddlewareHandler =
  callback => async (req, res) => {
    if (!req?.locals || !req.locals?.user) {
      res.status(401);
      return res.send("");
    }

    // REVIEW: include a middleware to filter by role
    // // include the old way of handling permissions...
    // if (req.locals.user.role === "viewer") {
    //   res.status(403);
    //   return res.send("");
    // }

    return callback(req, res);
  };

export { withPermissionsMiddleware };
