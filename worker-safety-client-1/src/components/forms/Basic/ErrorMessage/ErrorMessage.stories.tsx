import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Either } from "fp-ts/Either";
import type { Errors } from "io-ts";

import { NonEmptyString, withMessage } from "io-ts-types";
import { initFormField, updateFormField } from "@/utils/formField";

import { ErrorMessage } from "./ErrorMessage";

const decodeStringInput: (input: string) => Either<Errors, NonEmptyString> =
  withMessage(NonEmptyString, () => "Please select one option").decode;

let field = initFormField(decodeStringInput)("");
field = updateFormField(decodeStringInput)("");

export default {
  title: "JSB/ErrorMessage",
  component: ErrorMessage,
} as ComponentMeta<typeof ErrorMessage>;

export const Playground: ComponentStory<typeof ErrorMessage> = args => (
  <ErrorMessage {...args} />
);
Playground.args = {
  field: field,
};
