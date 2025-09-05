import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { DropdownProps } from "./Dropdown";
import { action } from "@storybook/addon-actions";
import { Icon } from "@urbint/silica";
import ButtonPrimary from "../button/primary/ButtonPrimary";
import Dropdown from "./Dropdown";

export default {
  title: "Silica/Dropdown",
  component: Dropdown,
  decorators: [
    Story => (
      <div className="absolute">
        {" "}
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Dropdown>;

const TemplateDropdown: ComponentStory<typeof Dropdown> = args => (
  <Dropdown {...args} />
);

const commonArgs: DropdownProps = {
  label: "Button label",
  menuItems: [
    [
      { label: "edit", icon: "edit", onClick: action("edit clicked") },
      {
        label: "open",
        icon: "external_link",
        onClick: action("open clicked"),
      },
    ],
    [
      {
        label: "close",
        icon: "close_small",
        onClick: action("close clicked"),
      },
    ],
    [{ label: "user", icon: "user", onClick: action("user clicked") }],
  ],
};

export const Playground = TemplateDropdown.bind({});

Playground.args = commonArgs;

export const WithIcon = TemplateDropdown.bind({});

WithIcon.args = {
  ...commonArgs,
  icon: "chevron_down",
};

const TemplateDropdownPrimary: ComponentStory<typeof Dropdown> = args => (
  <Dropdown {...args}>
    <ButtonPrimary label="button label" iconStart="chevron_down" />
  </Dropdown>
);

export const withCustomButton = TemplateDropdownPrimary.bind({});

withCustomButton.args = commonArgs;

export const WithMenuItemsRightSlot = TemplateDropdown.bind({});

WithMenuItemsRightSlot.args = {
  ...commonArgs,
  menuItems: [
    commonArgs.menuItems[0].map(item => ({
      ...item,
      rightSlot: <Icon name="uploading" />,
    })),
  ],
};
