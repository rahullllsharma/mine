import Script from "next/script";
import { useEffect, useRef, useState } from "react";

import { config } from "@/config";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { getEnv } from "@/utils/env";

type UserData = {
  keyCloakId: string;
  firstName: string;
  lastName: string;
  email: string;
  role: string;
  tenantId: string;
  opCoId: string;
  accountId: string;
  visitorId: string;
};

// Utility to construct email and visitor ID
const constructIdentifiers = (
  name: string,
  email: string,
  tenantId: string
) => {
  const [firstName = "", lastName = ""] = name.split(" ");
  const fallbackEmail = `${firstName}_${lastName}@noemail.${tenantId || "com"}`;
  const constructedEmail = email || fallbackEmail;

  const visitorId = `${constructedEmail}-WS-${getEnv()}-${tenantId}`;

  return { firstName, lastName, constructedEmail, visitorId };
};
// Populates user data for Pendo
const populateUserData = (user: any, tenantId: string): UserData => {
  const { id, name = "", email = "", role = "", opco = {} } = user || {};
  const { firstName, lastName, constructedEmail, visitorId } =
    constructIdentifiers(name, email, tenantId);

  return {
    keyCloakId: id || "",
    firstName,
    lastName,
    email: constructedEmail,
    role,
    tenantId,
    opCoId: opco?.id || "",
    accountId: `ws-${
      getEnv() === "integ" ? "integration" : getEnv()
    }-${tenantId}`,
    visitorId,
  };
};

function Pendo(): JSX.Element {
  const [canPendoLoad, setCanPendoLoad] = useState(false);

  const {
    tenant: { name: tenantId },
  } = useTenantStore();
  const { me: user } = useAuthStore();

  const userData = useRef<UserData>({
    keyCloakId: "",
    firstName: "",
    lastName: "",
    email: "",
    role: "",
    tenantId: "",
    opCoId: "",
    visitorId: "",
    accountId: "",
  });

  useEffect(() => {
    if (!user) {
      return;
    }

    userData.current = populateUserData(user, tenantId);

    setCanPendoLoad(true);
  }, [user]);

  const {
    keyCloakId,
    firstName,
    lastName,
    email,
    role,
    opCoId,
    accountId,
    visitorId,
  } = userData.current;

  return (
    <>
      {canPendoLoad && (
        <Script
          id="pendo-script"
          dangerouslySetInnerHTML={{
            __html: `(function(apiKey){
  (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
  v=['initialize','identify','updateOptions','pageLoad','track'];for(w=0,x=v.length;w<x;++w)(function(m){
      o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
      y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
      z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');

      
          pendo.initialize({
        visitor: {
           id: "${visitorId}",
          keycloak_id:"${keyCloakId}",
          first_name: "${firstName}", 
          last_name: "${lastName}",
          email_address: "${email}",
          role: "${role}",
          tenant_id: "${tenantId}",
          opco_id: "${opCoId}",
        },

        account: {
          id: "${accountId}", 
          tenant_id: "${tenantId}",
        }});
})("${config.pendoToken}");`,
          }}
        />
      )}
    </>
  );
}

export { Pendo };
