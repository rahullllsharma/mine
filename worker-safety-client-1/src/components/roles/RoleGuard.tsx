import type { PropsWithChildren } from "react";
import { useRouter } from "next/router";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import ErrorContainer from "@/components/shared/error/ErrorContainer";

/**
 * This key value map is used to store the routes that are only accessible with a specific role.
 * If a route is not visible here, then it means that any user can see them.
 */
const guardedRoutes: Record<string, string[]> = {
  "/admin/config": ["administrator"],
};

function RoleGuard({ children }: PropsWithChildren<unknown>) {
  const { me: user } = useAuthStore();
  const router = useRouter();
  const currentPath = router.pathname;
  if(!user.permissions.includes('CONFIGURE_CUSTOM_TEMPLATES')) {
    guardedRoutes["/templates"] = ["administrator"];
    guardedRoutes["/templates/create"] = ["administrator"];
    guardedRoutes["/templates/view"] = ["administrator"];
  }

  if (
    !Object.keys(guardedRoutes).includes(currentPath) ||
    guardedRoutes[currentPath].includes(user.role)
  ) {
    return <>{children}</>;
  }

  const navigateToHomeScreen = () => router.push("/");
  return <ErrorContainer notFoundError onClick={navigateToHomeScreen} />;
}

export { RoleGuard };
