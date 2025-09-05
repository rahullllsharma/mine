import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { TenantMock } from "@/store/tenant/utils/tenantMock";
import { DailyReportPrintTemplate } from "./DailyReportPrintTemplate";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import json from "./__mocks__/data.json";

export default {
  title: "Layout/PrintReportLayout/Template",
  component: DailyReportPrintTemplate,
  parameters: {
    docs: {
      description: {
        component: `
<div className="bg-yellow-100 rounded-lg p-4 mb-4 text-sm text-yellow-700">
This is just an example of the HTML that is sent to the PDF service
(puppeteer)
<br />
<p>
It is possible that some sections do not have the spacing required nor
the header or footer is present. <b>This is by design</b> as same rules
can only be applied when regenerating the actual PDF.
</p>
</div>`,
      },
    },
  },
  decorators: [
    Story => (
      <div className="overflow-y-auto h-screen">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof DailyReportPrintTemplate>;

const jsonObj = {
  ...json,
  user: { ...json.user, entities: TenantMock.entities },
};

const Template: ComponentStory<typeof DailyReportPrintTemplate> = args => (
  <DailyReportPrintTemplate {...args} />
);

export const Playground = Template.bind({});
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
Playground.args = jsonObj;
