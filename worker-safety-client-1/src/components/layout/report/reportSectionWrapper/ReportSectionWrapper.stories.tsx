import type { ComponentMeta, ComponentStory } from "@storybook/react";
import ReportSectionHeader from "../reportSectionHeader/ReportSectionHeader";
import ReportSectionBlock from "../reportSectionBlock/ReportSectionBlock";
import ReportSectionWrapper from "./ReportSectionWrapper";

export default {
  title: "Layout/Report/ReportSectionWrapper",
  component: ReportSectionWrapper,
} as ComponentMeta<typeof ReportSectionWrapper>;

const Template: ComponentStory<typeof ReportSectionWrapper> = args => (
  <ReportSectionWrapper {...args} />
);

export const OneElement = Template.bind({});
OneElement.args = {
  children: (
    <>
      <ReportSectionHeader title="Section title" />
      <ReportSectionBlock>Section content</ReportSectionBlock>
    </>
  ),
};

export const TwoElements = Template.bind({});
TwoElements.args = {
  children: (
    <>
      <ReportSectionHeader title="Section title" />
      <ReportSectionBlock>Section content</ReportSectionBlock>
      <ReportSectionBlock isInner>Section content inner</ReportSectionBlock>
    </>
  ),
};
