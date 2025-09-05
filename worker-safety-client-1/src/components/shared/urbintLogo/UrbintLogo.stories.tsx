import type { ComponentMeta, ComponentStory } from "@storybook/react";

import UrbintLogo from "./UrbintLogo";

export default {
  title: "Silica/Logo",
  component: UrbintLogo,
} as ComponentMeta<typeof UrbintLogo>;

const TemplateUrbintLogo: ComponentStory<typeof UrbintLogo> = args => (
  <UrbintLogo {...args} />
);

export const Default = TemplateUrbintLogo.bind({});

Default.args = {
  className: "text-brand-urbint-40 text-3xl",
};
