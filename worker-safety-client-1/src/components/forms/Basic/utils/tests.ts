import type { Either } from "fp-ts/lib/Either";
import type { Errors } from "io-ts";
import * as t from "io-ts-types";
import { initFormField } from "@/utils/formField";

type DecodeFunction = (input: string) => Either<Errors, t.NonEmptyString>;

const createStringInputDecoder = (errorMessage: string) => {
  const decodeStringInput: DecodeFunction = t.withMessage(
    t.NonEmptyString,
    () => errorMessage
  ).decode;

  return decodeStringInput;
};

const createFormField = (raw: string, decodeFunction: DecodeFunction) => {
  return initFormField(decodeFunction)(raw);
};

export { createStringInputDecoder, createFormField };
