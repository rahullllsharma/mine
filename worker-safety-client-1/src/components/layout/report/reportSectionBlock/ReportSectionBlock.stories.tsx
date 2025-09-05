import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ReportSectionBlock from "./ReportSectionBlock";

export default {
  title: "Layout/Report/SectionBlock",
  component: ReportSectionBlock,
} as ComponentMeta<typeof ReportSectionBlock>;

const Template: ComponentStory<typeof ReportSectionBlock> = args => (
  <ReportSectionBlock {...args} />
);

export const Normal = Template.bind({});
Normal.args = {
  children: <p>Report Section Block Content</p>,
};

export const IsInner = Template.bind({});
IsInner.args = {
  isInner: true,
  children: <p>Report Section Block Content</p>,
};
