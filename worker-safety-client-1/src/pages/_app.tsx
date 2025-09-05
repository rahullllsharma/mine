import type { AppContext, AppInitialProps, AppProps } from "next/app";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider } from "next-auth/react";
import App from "next/app";
import Head from "next/head";
import { useRouter } from "next/router";
import { isMobile, isTablet } from "react-device-detect";
import NavBarWorkerSafety from "@/components/navbarWorkerSafety/NavBarWorkerSafety";
import { RoleGuard } from "@/components/roles/RoleGuard";
import ToastProvider from "@/components/shared/toast/context/ToastProvider";
import { config } from "@/config";
import DatadogRUM from "@/scripts/Datadog";
import { FullStory } from "@/scripts/FullStory";
import { Pendo } from "@/scripts/Pendo";
import { AuthGuard } from "@/utils/auth";
import "../styles/globals.css";

const UNGUARDED_ROUTES: string[] = ["/auth/signin"];

/**
 * TODO: should these next lines be part of the feature flag plan?
 */
const shouldLoadScriptDataDog = config.datadogRUMEnabled === "true";
const shouldLoadFullStory = config.fullStoryEnabled === "true";

const queryClient = new QueryClient();

function WsApp({
  Component,
  pageProps: { session, ...pageProps },
}: AppProps): JSX.Element {
  const router = useRouter();
  const currentPath = router.pathname;

  // TODO This was added to remove the NavBar when on the print page. This is a temporary solution
  const isPrintPage = router.pathname.includes("/print");
  const withAuth = !UNGUARDED_ROUTES.includes(currentPath);
  const isMobileView = isMobile || isTablet;
  const shouldLoadPendo = config.pendoEnabled === "true";
  const pathsToHideNavBar = [
    "/ebo",
    "/jsb",
    "/reports",
    "/templates/",
    "/template-forms/",
  ].some(path => router.pathname.includes(path));
  const hideNaveBar = isMobileView && pathsToHideNavBar;
  return (
    <>
      {withAuth ? (
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <SessionProvider
              session={session}
              refetchInterval={60}
              refetchWhenOffline={false}
            >
              <AuthGuard>
                {shouldLoadScriptDataDog && <DatadogRUM />}
                {shouldLoadFullStory && <FullStory />}
                {shouldLoadPendo && <Pendo />}

                <Head>
                  <title>Worker Safety | Urbint</title>
                  <link
                    href="https://rsms.me/inter/inter.css"
                    rel="stylesheet"
                  />
                </Head>
                {!isPrintPage && !hideNaveBar && <NavBarWorkerSafety />}
                <RoleGuard>
                  <Component {...pageProps} />
                </RoleGuard>
              </AuthGuard>
            </SessionProvider>
          </ToastProvider>
        </QueryClientProvider>
      ) : (
        <ToastProvider>
          <Head>
            <title>Worker Safety | Urbint</title>
            <link href="https://rsms.me/inter/inter.css" rel="stylesheet" />
          </Head>
          <Component {...pageProps} />
        </ToastProvider>
      )}
    </>
  );
}

export default WsApp;

WsApp.getInitialProps = async (
  context: AppContext
): Promise<AppInitialProps> => {
  const ctx = await App.getInitialProps(context);

  return ctx;
};
