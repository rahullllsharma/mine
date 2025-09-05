import type { ComponentMeta, ComponentStory } from "@storybook/react";

import NavBarWorkerSafety from "./NavBarWorkerSafety";

export default {
  title: "Components/Navbar/NavBarWorkerSafety",
  component: NavBarWorkerSafety,
  argTypes: {},
} as ComponentMeta<typeof NavBarWorkerSafety>;

const TemplateNavBarWorkerSafety: ComponentStory<typeof NavBarWorkerSafety> =
  () => <NavBarWorkerSafety />;

export const Playground = TemplateNavBarWorkerSafety.bind({});

Playground.args = {};
