import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";

import Checkbox from "./Checkbox";

export default {
  title: "Silica/Checkbox",
  component: Checkbox,
  argTypes: {
    onClick: () => action("clicked"),
  },
} as ComponentMeta<typeof Checkbox>;

const Template: ComponentStory<typeof Checkbox> = args => (
  <>
    <label htmlFor="id">
      <Checkbox {...args} id="id" /> This is a checkbox (`label` is not part of
      the component!)
    </label>
    <br />
    <br />
    <blockquote>
      This is the barebone checkbox component
      <br />
      If you need to extend, consider creating a <code>FieldCheckbox</code>
    </blockquote>
  </>
);

export const Playground = Template.bind({});
Playground.args = {};

export const Checked = Template.bind({});
Checked.args = {
  defaultChecked: true,
};

export const Disabled = Template.bind({});
Disabled.args = {
  disabled: true,
  defaultChecked: true,
};
