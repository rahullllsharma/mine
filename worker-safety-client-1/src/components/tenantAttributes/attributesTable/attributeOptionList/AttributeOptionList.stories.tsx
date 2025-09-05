import type { Meta, Story } from "@storybook/react";
import type { AttributeOptionListProps } from "./AttributeOptionList";
import { AttributeOptionList } from "./AttributeOptionList";

export default {
  title: "Components/TenantAttributes/AttributeOptionList",
  component: AttributeOptionList,
} as Meta;

const Template: Story<AttributeOptionListProps> = args => (
  <AttributeOptionList {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  isVisible: true,
  isRequired: true,
  isFilterable: true,
};
