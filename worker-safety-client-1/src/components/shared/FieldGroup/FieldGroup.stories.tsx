import type { ComponentMeta, ComponentStory } from "@storybook/react";

import FieldInput from "../field/fieldInput/FieldInput";
import { FieldGroup } from "./FieldGroup";

export default {
  title: "JSB/FieldGroup",
  component: FieldGroup,
} as ComponentMeta<typeof FieldGroup>;

const Template: ComponentStory<typeof FieldGroup> = args => (
  <FieldGroup {...args}>
    <FieldInput containerClassName="mb-4" label="First Name:" required />
    <FieldInput label="Last Name:" required />
  </FieldGroup>
);

export const Example = Template.bind({});
Example.args = {
  legend: "Profile data",
};
