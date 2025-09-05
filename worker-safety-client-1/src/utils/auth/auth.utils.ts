import type { NextApiRequest } from "next";
import type { IncomingMessage } from "http";
import type { NextAuthOptions } from "next-auth";
import type { ApolloError } from "@apollo/client";
import type { ServerError } from "@apollo/client/link/utils";
import { signOut } from "next-auth/react";
import axios from "axios";
import KeycloakProvider from "next-auth/providers/keycloak";
import { StatusCodes } from "http-status-codes";
import { config } from "@/config";

type GetKeycloakCfgArgs = {
  hostname: string;
};

type KeycloakConfig = {
  url: string;
  realm: string;
  clientId: string;
};

type TokenResponse = {
  access_token: string;
  expires_in: number;
  refresh_token: string;
};

/** Exception subdomains */
const subDomainExceptions = {
  localhost: {
    realm: config?.keycloakRealm || "asgard",
    clientId: "worker-safety-asgard",
  },
} as const;

/**
 * Returns the keycloak realm and client id for the tenant
 * Fallback for local dev.
 */
const getTenantConfigByHostname = async (hostname: string) => {
  try {
    const domains = hostname.split(".");
    const realm = domains[0];
    if (realm in subDomainExceptions) {
      return subDomainExceptions[realm as keyof typeof subDomainExceptions];
    }
    const { data: response } = await axios({
      url: `${config.workerSafetyServiceUrlRest}/rest/realm-details?name=${realm}`,
      method: "get",
    });
    const { attributes: tenantDetails } = response.data;

    return {
      realm: tenantDetails.realm_name || "asgard",
      clientId: tenantDetails.client_id || "worker-safety-asgard",
    };
  } catch (err) {
    console.log(err, "error fetching tenant details");
    throw err;
  }
};

/** Parse the keycloak config for the given environment. */
export const getKeycloakCfg = async ({
  hostname,
}: GetKeycloakCfgArgs): Promise<KeycloakConfig> => {
  const { realm, clientId } = await getTenantConfigByHostname(hostname);

  return {
    url: config.keycloakUrl,
    realm,
    clientId,
  };
};

export async function getNextConfig(
  req: NextApiRequest
): Promise<NextAuthOptions> {
  const { host } = (req as IncomingMessage).headers;
  const url = new URL(
    `${config.appEnv === "development" ? "http" : "https"}://${host}`
  );
  // workaround to fix the dynamic hostname initialization issue
  process.env.NEXTAUTH_URL = url.toString();
  const keycloakCfg = await getKeycloakCfg({ hostname: url.hostname });
  return {
    providers: [
      KeycloakProvider({
        clientId: keycloakCfg.clientId,
        // required Option; passing "" for public client
        clientSecret: "",
        authorization: `${config.keycloakUrl}/realms/${keycloakCfg.realm}/protocol/openid-connect/auth`,
        issuer: `${config.keycloakUrl}/realms/${keycloakCfg.realm}`,
        wellKnown: `${config.keycloakUrl}/realms/${keycloakCfg.realm}/.well-known/openid-configuration`,
      }),
    ],
    pages: {
      signIn: "/auth/signin/",
      error: "/auth/error/",
    },
    callbacks: {
      /* This is to allow for accessToken retrieval inside of GetServerProps
       Reference: https://stackoverflow.com/questions/69068495/how-to-get-the-provider-access-token-in-next-auth/72492588#72492588
       */
      async jwt({ token, user, account }) {
        if (user) {
          token.id = user.id;
        }
        if (account) {
          // First-time login, save the `access_token`, its expiry and the `refresh_token`
          return {
            ...token,
            accessToken: account.access_token,
            refreshToken: account.refresh_token,
            idToken: account.id_token,
            expiresAt: account.expires_at,
          };
          // taken a buffer of 5 sec
        } else if (Date.now() < token.expiresAt! * 1000 - 5 * 1000) {
          // Subsequent logins, but the `access_token` is still valid
          return token;
        } else {
          // Subsequent logins, but the `access_token` has expired, try to refresh it
          if (!token.refreshToken) throw new TypeError("Missing refresh_token");

          try {
            const newTokens = await refreshToken(
              keycloakCfg.realm,
              keycloakCfg.clientId,
              token.refreshToken
            );
            token = {
              ...token,
              accessToken: newTokens.access_token,
              expiresAt: Math.floor(Date.now() / 1000 + newTokens.expires_in),
              refreshToken: newTokens.refresh_token,
            };
            console.debug(
              "Refreshed token: access %s refresh %s",
              token.accessToken?.slice(-6),
              token.refreshToken?.slice(-6)
            );
            return token;
          } catch (error) {
            console.error("Error refreshing access_token", error);
            // If we fail to refresh the token, return an error so we can handle it on the page
            token.error = error;
            return token;
          }
        }
      },
      async session({ session, token }) {
        // @ts-expect-error user can be null
        if (session.user) session.user.id = token.id;
        session.accessToken = token.accessToken;
        session.refreshToken = token.refreshToken;
        session.idToken = token.idToken;
        session.expiresAt = token.expiresAt;
        session.error = token.error;
        return session;
      },
    },
  };
}

export const sessionExpiryHandlerForApolloClient = (error: ApolloError) => {
  const networkError = error.networkError as ServerError;
  const statusCode = networkError?.statusCode || networkError?.response?.status;
  if ([StatusCodes.UNAUTHORIZED, StatusCodes.FORBIDDEN].includes(statusCode)) {
    signOut({ redirect: true });
    return true;
  }
  return false;
};

/*
 * Uses the keycloak's oidc token endpoint to issue a fresh TokenResponse
 * using existing valid refresh_token
 */
const refreshToken = async (
  realm: string,
  client_id: string,
  refresh_token: string
) => {
  const response = await fetch(
    `${config.keycloakUrl}/realms/${realm}/protocol/openid-connect/token`,
    {
      method: "POST",
      body: new URLSearchParams({
        client_id,
        grant_type: "refresh_token",
        refresh_token,
      }),
    }
  );

  const tokensOrError = await response.json();

  if (!response.ok) throw tokensOrError;

  return tokensOrError as TokenResponse;
};
