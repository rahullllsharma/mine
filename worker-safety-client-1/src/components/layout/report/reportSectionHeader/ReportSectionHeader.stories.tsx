import type { ComponentMeta, ComponentStory } from "@storybook/react";

import ReportSectionHeader from "./ReportSectionHeader";

export default {
  title: "Layout/Report/ReportSectionHeader",
  component: ReportSectionHeader,
} as ComponentMeta<typeof ReportSectionHeader>;

const Template: ComponentStory<typeof ReportSectionHeader> = args => (
  <ReportSectionHeader {...args} />
);

export const TitleOnly = Template.bind({});
TitleOnly.args = {
  title: "This is a title",
};

export const TitleAndSubtitle = Template.bind({});
TitleAndSubtitle.args = {
  title: "This is a title",
  subtitle: "This is a subtitle",
};
