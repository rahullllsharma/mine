import type { ComponentMeta, ComponentStory } from "@storybook/react";
import PrintReportHeader from "./PrintReportHeader";

export default {
  title: "Layout/PrintReportLayout/Header",
  component: PrintReportHeader,
} as ComponentMeta<typeof PrintReportHeader>;

const Template: ComponentStory<typeof PrintReportHeader> = args => (
  <PrintReportHeader {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  subtitle: "North Grand St. Bridge • Location A",
};
