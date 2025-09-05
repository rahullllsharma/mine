import "@apollo/client";
import type { ServerError as OriginalServerError } from "@apollo/client/link/utils/throwServerError";

/**
 * It's needed to extend the ApolloError type in the application
 * in order to account for custom errors that are thrown in the backend
 */
declare module "@apollo/client/link/utils" {
  export declare interface ServerError
    extends Omit<OriginalServerError, "result"> {
    result: OriginalServerError["result"] & {
      /**
       *
       * @package worker-safety-service - worker_safety_service/keycloak/exceptions.py
       * @description WSS returns a detailed reason when the tenant does not exist
       */
      detail: string;
    };
  }
}
