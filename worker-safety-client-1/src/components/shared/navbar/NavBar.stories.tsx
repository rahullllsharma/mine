import type { ComponentMeta, ComponentStory } from "@storybook/react";

import Navbar from "./NavBar";

export default {
  title: "Silica/Navbar",
  component: Navbar,
} as ComponentMeta<typeof Navbar>;

const TemplateNavbar: ComponentStory<typeof Navbar> = args => (
  <Navbar {...args} />
);

export const Default = TemplateNavbar.bind({});

Default.args = { title: "Urbint" };
