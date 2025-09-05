import type { Either } from "fp-ts/Either";
import type { Option } from "fp-ts/Option";
import type { JsbApi } from "./requests/jsb";
import type { EboApi } from "./requests/ebo";
import type { CommonApi } from "./requests/common";
import type * as t from "io-ts";
import * as E from "fp-ts/Either";
import * as O from "fp-ts/Option";
import * as TE from "fp-ts/TaskEither";
import { pipe } from "fp-ts/function";
import { GraphQLClient } from "graphql-request";
import { failure } from "io-ts/PathReporter";
import { useEffect, useMemo, useRef, useState } from "react";
import { signIn, useSession } from "next-auth/react";
import { config } from "@/config";
import { jsbApi } from "./requests/jsb";
import { eboApi } from "./requests/ebo";
import { commonApi } from "./requests/common";

export type ApiError =
  | {
      type: "DecodeError";
      errors: t.Errors;
    }
  | {
      type: "JsonParseError";
      error: unknown;
    }
  | {
      type: "RequestError";
      error: unknown;
    };

export const DecodeError = (errors: t.Errors): ApiError => ({
  type: "DecodeError",
  errors,
});

export const RequestError = (error: unknown): ApiError => ({
  type: "RequestError",
  error,
});

export const JsonParseError = (error: unknown): ApiError => ({
  type: "JsonParseError",
  error,
});

export type ApiResult<T> = Either<ApiError, T>;

export const showApiError = (error: ApiError): string => {
  switch (error.type) {
    case "DecodeError":
      return failure(error.errors).join("\n").replace(/\//g, "\n\t/");
    case "RequestError":
      return JSON.stringify(error.error);
    case "JsonParseError":
      return JSON.stringify(error.error);
  }
};

export const showUserApiError = (error: ApiError): string => {
  switch (error.type) {
    case "DecodeError":
      return "An error occurred while processing the response from the server.";
    case "RequestError":
      return JSON.stringify(error.error).includes("does not exist")
        ? "The form has been deleted"
        : "An error occurred while communicating with the server.";
    case "JsonParseError":
      return "An error occurred while processing the response from the server.";
  }
};

export const makeRequest = <T, D, A, R>(
  fn: (a: A) => Promise<D>,
  args: A,
  decode: t.Decode<D, T>,
  mapResultFn: (_: T) => R
): TE.TaskEither<ApiError, R> => {
  return pipe(
    TE.tryCatch(() => fn(args), RequestError),
    TE.chainEitherK(data => {
      return pipe(decode(data), E.mapLeft(DecodeError));
    }),
    TE.map(mapResultFn)
  );
};

export interface Api {
  jsb: JsbApi;
  ebo: EboApi;
  common: CommonApi;
}

export function useApi(): Option<Api> {
  const signingIn = useRef(false);
  const { data: session } = useSession({ required: true });
  const [token, setToken] = useState<Option<string>>(O.none);

  useEffect(() => {
    if (!session || signingIn.current) {
      signingIn.current = true;
      return;
    }
    if (session.error) {
      signIn("keycloak", { redirect: true });
    } else {
      setToken(O.fromNullable(session?.accessToken));
    }
  }, [session]);

  const client = useMemo(
    () =>
      pipe(
        token,
        O.map(
          tkn =>
            new GraphQLClient(
              `${config.workerSafetyServiceUrlGraphQL}/graphql`,
              {
                headers: {
                  Authorization: `Bearer ${tkn}`,
                },
              }
            )
        )
      ),
    [token]
  );

  return pipe(
    client,
    O.map(c => ({
      jsb: jsbApi(c),
      ebo: eboApi(c),
      common: commonApi(c),
    }))
  );
}
