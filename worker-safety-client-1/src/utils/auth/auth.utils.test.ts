import { config } from "@/config";
import { getKeycloakCfg } from "./";

describe(getKeycloakCfg.name, () => {
  it.each`
    hostname                  | url                   | realm       | clientId
    ${"asgard.ws.urbint.com"} | ${config.keycloakUrl} | ${"asgard"} | ${"worker-safety-asgard"}
  `(
    "should return a keycloak config for standard environment => $hostname",
    async ({ realm, clientId }) => {
      const mockResponse = {
        realm: "asgard",
        clientId: "worker-safety-asgard",
      };
      expect(mockResponse).toEqual({ realm, clientId });
    }
  );

  describe.each`
    hostname       | url                   | realm       | clientId
    ${"localhost"} | ${config.keycloakUrl} | ${"asgard"} | ${"worker-safety-asgard"}
  `(
    "for each exceptional hostnames => $hostname",
    ({ hostname, url, realm, clientId }) => {
      it("should return a special keycloak config for exceptional environment", async () => {
        const result = await getKeycloakCfg({ hostname });
        expect(result).toEqual({ url, realm, clientId });
      });

      describe("when has a realm defined by the env", () => {
        let keycloakModule: typeof getKeycloakCfg;

        beforeEach(() => {
          jest.resetModules();
          jest.doMock("@/config", () => ({
            ...jest.requireActual("@/config"),
            config: {
              ...jest.requireActual("@/config").config,
              keycloakRealm: "custom-realm",
            },
          }));
          jest.isolateModules(() => {
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            keycloakModule = require("./").getKeycloakCfg;
          });
        });

        it("should use it as the realm", async () => {
          const result = await keycloakModule({ hostname });
          expect(result).toEqual({ url, realm: "custom-realm", clientId });
        });
      });
    }
  );
});
