import { Router } from "next/router";
import { useCallback, useEffect } from "react";

export default function useBeforeUnload(
  onRouteChange: (url: string) => void,
  onBeforeUnload: (e: BeforeUnloadEvent) => void
): void {
  const onBeforeUnloadCallback = useCallback(onBeforeUnload, [onBeforeUnload]);
  const routeChangeStartCallback = useCallback(onRouteChange, [onRouteChange]);

  useEffect(() => {
    Router.events.on("routeChangeStart", routeChangeStartCallback);
    window.addEventListener("beforeunload", onBeforeUnloadCallback);

    return () => {
      Router.events.off("routeChangeStart", routeChangeStartCallback);
      window.removeEventListener("beforeunload", onBeforeUnloadCallback);
    };
  }, [onBeforeUnloadCallback, routeChangeStartCallback]);
}
