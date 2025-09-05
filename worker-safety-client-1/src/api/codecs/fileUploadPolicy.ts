import type { CheckKeys } from "../codecs/utils";
import type { FileUploadPoliciesMutation } from "../generated/types";
import * as t from "io-ts";
import * as tt from "io-ts-types";

// type of the individual file upload policy item from the FileUploadPoliciesMutation
export type FileUploadPolicyDto =
  FileUploadPoliciesMutation["fileUploadPolicies"][number];

export const fileUploadPolicyCodec = t.type({
  id: t.string,
  url: t.string,
  signedUrl: t.string,
  fields: t.string,
});

type _CheckFUP = CheckKeys<keyof FileUploadPolicy, keyof FileUploadPolicyDto>;

export type FileUploadPolicy = t.TypeOf<typeof fileUploadPolicyCodec>;

export const generatedFileUploadPolicies = t.array(fileUploadPolicyCodec);

export const fileUploadPolicyFieldsCodec = t.type({
  key: tt.NonEmptyString,
  policy: tt.NonEmptyString,
  "x-goog-algorithm": tt.NonEmptyString,
  "x-goog-credential": tt.NonEmptyString,
  "x-goog-date": tt.NonEmptyString,
  "x-goog-signature": tt.NonEmptyString,
});

export type FileUploadPolicyFields = t.TypeOf<
  typeof fileUploadPolicyFieldsCodec
>;

export type GeneratedFileUploadPolicies = t.TypeOf<
  typeof generatedFileUploadPolicies
>;

export const filePropertiesCodec = t.type({
  id: t.string,
  name: t.string,
  displayName: t.string,
  size: t.string,
  url: t.string,
  signedUrl: t.string,
  date: tt.optionFromNullable(t.string),
  time: tt.optionFromNullable(t.string),
  category: tt.optionFromNullable(t.string),
});

export type FileProperties = t.TypeOf<typeof filePropertiesCodec>;
