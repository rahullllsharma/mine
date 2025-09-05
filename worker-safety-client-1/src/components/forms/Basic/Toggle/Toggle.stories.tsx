import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Either } from "fp-ts/Either";
import type { Errors } from "io-ts";
import { NonEmptyString, withMessage } from "io-ts-types";
import { initFormField } from "@/utils/formField";

import { Toggle } from "./Toggle";

export default {
  title: "JSB/Toggle",
  component: Toggle,
} as ComponentMeta<typeof Toggle>;

const decodeToggleInput: (input: string) => Either<Errors, NonEmptyString> =
  withMessage(NonEmptyString, () => "Please select one option").decode;

const _field = initFormField(decodeToggleInput)("");

export const Playground: ComponentStory<typeof Toggle> = args => (
  <Toggle {...args} />
);

// Playground.args = {
//   htmlFor: "example",
//   value: "example",
//   name: "example",
//   disabled: false,
//   field,
// };
