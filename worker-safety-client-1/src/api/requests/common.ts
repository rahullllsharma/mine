import type { GraphQLClient } from "graphql-request";
import type { TaskEither } from "fp-ts/lib/TaskEither";
import type { ApiError } from "../api";
import type { Sdk } from "../generated/types";
import type { FileUploadPolicy } from "../codecs";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { identity } from "fp-ts/lib/function";
import { makeRequest } from "../api";
import { getSdk } from "../generated/types";
import { fileUploadPolicyCodec } from "../codecs";

export const generateFileUploadPolicies =
  (sdk: Sdk) =>
  (count: number): TaskEither<ApiError, NonEmptyArray<FileUploadPolicy>> =>
    makeRequest(
      sdk.FileUploadPolicies,
      { count },
      res =>
        tt.nonEmptyArray(fileUploadPolicyCodec).decode(res.fileUploadPolicies),
      identity
    );

export const uploadFileToGCS =
  (url: string) =>
  (payload: FormData): TaskEither<ApiError, unknown> =>
    makeRequest(
      () => fetch(url, { method: "POST", body: payload }),
      {},
      res => t.success(res),
      identity
    );

export interface CommonApi {
  generateFileUploadPolicies: (
    count: number
  ) => TaskEither<ApiError, NonEmptyArray<FileUploadPolicy>>;
  uploadFileToGCS: (
    url: string
  ) => (payload: FormData) => TaskEither<ApiError, unknown>;
}
export const commonApi = (c: GraphQLClient) => ({
  generateFileUploadPolicies: generateFileUploadPolicies(getSdk(c)),
  uploadFileToGCS: uploadFileToGCS,
});
