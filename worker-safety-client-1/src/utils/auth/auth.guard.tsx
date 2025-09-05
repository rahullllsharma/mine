import type { PropsWithChildren } from "react";
import type { KeycloakProfile } from "next-auth/providers/keycloak";
import { signIn, useSession } from "next-auth/react";
import React, { useEffect, useState, useRef } from "react";
import { InvalidTokenError, jwtDecode } from "jwt-decode";
import { ApolloProvider, useQuery } from "@apollo/client";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { stripTypename } from "@/utils/shared";

import { initializeApollo } from "@/graphql";
import Loader from "@/components/shared/loader/Loader";
import Permissions from "../../graphql/queries/permissions.gql";

const UserProvider = ({
  children,
}: {
  children?: React.ReactNode | undefined;
}) => {
  const parsedToken = useRef<KeycloakProfile | null>(null);

  // Session is being fetched, or no user.
  const { data: session, status } = useSession({
    required: true,
  });

  useEffect(() => {
    if (status === "authenticated") {
      try {
        parsedToken.current = jwtDecode<KeycloakProfile>(
          session.accessToken ?? ""
        );
      } catch (e) {
        if (e instanceof InvalidTokenError) {
          signIn("keycloak", {
            redirect: true,
            callbackUrl: window.location.href,
          });
        } else {
          throw e;
        }
      }
    }
  }, [session, status]);

  const setUser = useAuthStore(state => state.setUser);
  const setTenant = useTenantStore(state => state.setTenant);
  const [isAppReady, setIsAppReady] = useState(false);
  useQuery(Permissions, {
    fetchPolicy: "cache-and-network",
    onCompleted: ({ me }) => {
      setUser({
        initials: nameToInitials(
          parsedToken?.current?.given_name,
          parsedToken?.current?.family_name
        ),
        email: me?.email ?? "",
        permissions: me?.permissions ?? [],
        role: me?.role ?? "",
        id: me?.id ?? "",
        name: me?.name ?? "",
        opco: me?.opco,
        userPreferences: me?.userPreferences ?? [],
      });

      const normalizedTenantEntities = stripTypename(
        me?.tenant.configurations.entities ?? []
      );

      setTenant({
        name: me?.tenant.name ?? "",
        entities: normalizedTenantEntities,
        displayName: me?.tenant.displayName ?? "",
        workos: me?.tenant.workos,
      });

      setIsAppReady(true);
    },
  });

  if (isAppReady) {
    return <>{children}</>;
  }

  return null;
};

export function AuthGuard({
  children,
}: Readonly<PropsWithChildren<unknown>>): JSX.Element {
  const [isLoading, setIsLoading] = useState<boolean>(true);
  // Session is being fetched, or no user.
  const { data: session, status } = useSession({
    required: true,
  });
  const client = initializeApollo();

  useEffect(() => {
    if (status === "authenticated") {
      setIsLoading(false);
    } else {
      setIsLoading(true);
    }
  }, [session, status]);

  return (
    <>
      {isLoading ? (
        <Loader />
      ) : (
        <ApolloProvider client={client}>
          <UserProvider>{children}</UserProvider>
        </ApolloProvider>
      )}
    </>
  );
}

const nameToInitials = (first?: string, last?: string) => {
  if (!first || !last) {
    return "NA";
  }
  return first.charAt(0) + last.charAt(0);
};
