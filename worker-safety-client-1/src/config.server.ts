import fs from "fs";
import path from "path";
import getConfig from "next/config";

/** This config should be used for exposing paths and configs for SERVER ONLY. */
const config = {
  workerSafetyPrintStylesheet: fs
    .readFileSync(
      path.join(
        getConfig().serverRuntimeConfig.WORKER_SAFETY_PUBLIC_FOLDER,
        "css/print.css"
      )
    )
    .toString("utf-8"),
};

export { config };
