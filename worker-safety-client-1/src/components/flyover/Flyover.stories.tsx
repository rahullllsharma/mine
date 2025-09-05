import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { action } from "@storybook/addon-actions";
import { useState } from "react";
import ButtonIcon from "../shared/button/icon/ButtonIcon";

import Flyover from "./Flyover";

export default {
  title: "Components/Flyover",
  component: Flyover,
  parameters: { layout: "fullscreen" },
  decorators: [
    Story => (
      <div className="relative h-[600px] w-full py-4">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Flyover>;

const largeContentChildren = (
  <div>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras facilisis
    risus ac augue varius, ac fringilla quam luctus. Orci varius natoque
    penatibus et magnis dis parturient montes, nascetur ridiculus mus. Fusce
    scelerisque nisl mi, id auctor enim malesuada eget. In metus odio, lobortis
    vitae lacus vel, sagittis ultricies ipsum. Cras in sodales ipsum. Vestibulum
    pellentesque fermentum odio, ut facilisis ligula commodo sed. Duis posuere
    vulputate consectetur. Pellentesque gravida quam at auctor posuere. Mauris
    vitae volutpat nisl, ac laoreet enim. Sed tincidunt enim ante, at dictum
    neque porta et. Pellentesque cursus efficitur odio, vitae consequat nisi
    accumsan ut. Maecenas sollicitudin efficitur nisl sit amet sodales. Cras
    molestie iaculis ligula nec vulputate. Phasellus quam nunc, fermentum sed
    feugiat volutpat, faucibus iaculis mauris. Nunc tristique laoreet orci
    convallis placerat. Aenean ut elementum elit, non tempus orci.
  </div>
);

const Template: ComponentStory<typeof Flyover> = args => <Flyover {...args} />;

const WithToggleTemplate: ComponentStory<typeof Flyover> = args => {
  const [isOpen, setIsOpen] = useState(false);
  const toggleState = () => setIsOpen(prevState => !prevState);
  return (
    <>
      <ButtonIcon iconName="filter" className="pl-4" onClick={toggleState} />
      <Flyover {...args} isOpen={isOpen} onClose={toggleState} />
    </>
  );
};

export const Playground = Template.bind({});
Playground.args = {
  title: "Filters",
  isOpen: true,
  onClose: action("onClose"),
  children: <div>Content Panel</div>,
};

export const WithToggle = WithToggleTemplate.bind({});
WithToggle.args = {
  title: "Filters",
  children: largeContentChildren,
};

export const WithFooter = Template.bind({});
WithFooter.args = {
  title: "Filters",
  isOpen: true,
  onClose: action("onClose"),
  children: largeContentChildren,
  footer: (
    <div className="bg-brand-urbint-20 flex items-center justify-center h-full">
      This is a footer
    </div>
  ),
};
