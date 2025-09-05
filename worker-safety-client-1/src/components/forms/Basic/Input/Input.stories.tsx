import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Either } from "fp-ts/lib/Either";
import type { Errors } from "io-ts";
import * as tt from "io-ts-types";
import { initFormField } from "@/utils/formField";
import { Input } from "./Input";
import { TelephoneInput } from "./TelephoneInput";

export default {
  title: "JSB/Input",
  component: Input,
} as ComponentMeta<typeof Input>;

const decodeFieldInput: (input: string) => Either<Errors, tt.NonEmptyString> =
  tt.withMessage(tt.NonEmptyString, () => "Please provide a value").decode;

const field = initFormField(decodeFieldInput)("");

export const DefaultText: ComponentStory<typeof Input> = args => (
  <Input {...args} />
);

DefaultText.args = {
  type: "text",
  field,
  onChange: () => null,
  label: "First Name: *",
};

export const Telephone: ComponentStory<typeof TelephoneInput> = args => (
  <TelephoneInput {...args} />
);

Telephone.args = {
  field,
  onChange: () => null,
  label: "Telephone: *",
};
