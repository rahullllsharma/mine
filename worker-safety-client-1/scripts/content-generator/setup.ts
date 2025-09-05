import * as dotenv from "dotenv";
import configs from "./configs.json";

function setupScriptEnv() {
  // fetch main env vars
  dotenv.config({ path: "./.env.local" });
  // fetch "environment" env vars
  dotenv.config({
    path: `./support/config/.env.${configs.environment}`,
  });
}

export { setupScriptEnv };
