import type { ComponentStory, Meta, Story } from "@storybook/react";
import ErrorContainer from "./ErrorContainer";

export default {
  component: ErrorContainer,
  title: "Silica/Error",
  parameters: {
    layout: "none",
  },
  decorators: [
    (StoryComponent: Story) => (
      <div style={{ height: "100vh" }}>
        <StoryComponent />
      </div>
    ),
  ],
} as Meta;

const Template: ComponentStory<typeof ErrorContainer> = args => (
  <ErrorContainer {...args} />
);
export const Playground = Template.bind({});

export const NotFoundError = Template.bind({});
NotFoundError.args = {
  notFoundError: true,
};
