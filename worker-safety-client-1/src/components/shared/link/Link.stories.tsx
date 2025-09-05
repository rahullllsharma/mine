import type { ComponentMeta, ComponentStory } from "@storybook/react";
import Link from "./Link";

export default {
  title: "Silica/Link",
  component: Link,
} as ComponentMeta<typeof Link>;

const TemplateLink: ComponentStory<typeof Link> = args => <Link {...args} />;

export const Playground = TemplateLink.bind({});
Playground.args = {
  label: "link label",
};

export const WithIcon = TemplateLink.bind({});
WithIcon.args = {
  label: "link label",
  iconRight: "external_link",
};
