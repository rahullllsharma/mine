import type { ComponentMeta, ComponentStory } from "@storybook/react";
import Loader from "./Loader";

export default {
  title: "Silica/Loader",
  component: Loader,
  argTypes: {
    isOpen: { control: false },
    children: { control: false },
  },
  decorators: [
    Story => (
      <div className="flex">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Loader>;

const TemplateLoader: ComponentStory<typeof Loader> = () => <Loader />;

export const LoaderAnimation = TemplateLoader.bind({});
