import type { ComponentMeta, ComponentStory } from "@storybook/react";
import PrintReportFooter from "./PrintReportFooter";

export default {
  title: "Layout/PrintReportLayout/Footer",
  component: PrintReportFooter,
} as ComponentMeta<typeof PrintReportFooter>;

const Template: ComponentStory<typeof PrintReportFooter> = args => (
  <PrintReportFooter {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  note: "Generated on 03/25/2022 at 05:00 PM EST by Christina Ou",
};
