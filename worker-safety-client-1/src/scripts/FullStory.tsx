import { useEffect } from "react";
import { init } from "@fullstory/browser";

import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

function FullStory(): JSX.Element {
  const { me: user } = useAuthStore();
  const { name: tenantName } = useTenantStore(state => state.tenant);

  useEffect(() => {
    if (!window.FS || !user || !user?.id) {
      return;
    }

    window.FS.identify(user.id ?? "", {
      displayName: user?.name,
      role: user?.role,
      tenant: tenantName,
    });

    return () => {
      if (!!window.FS) {
        window.FS.shutdown();
      }
    };
  }, [user, tenantName]);

  init({
    orgId: "o-1A9RR9-na1",
    namespace: "FS",
    debug: false,
    host: "fullstory.com",
    script: "edge.fullstory.com/s/fs.js",
  });

  return <></>;
}

export { FullStory };
