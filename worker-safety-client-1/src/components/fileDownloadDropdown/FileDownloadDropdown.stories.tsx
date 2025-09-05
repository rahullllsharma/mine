import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { WorkbookData } from "./providers/spreadsheet";
import { nanoid } from "nanoid";
import { sampleRiskCountData } from "./__mocks__/mockData";
import FileDownloadDropdown from "./FileDownloadDropdown";

export default {
  title: "Components/FileDownloadDropdown",
  component: FileDownloadDropdown,
  decorators: [
    Story => (
      <div className="flex justify-end p-4">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof FileDownloadDropdown>;

const singleWorkbookData = [
  [`worksheet-${nanoid()}`, sampleRiskCountData],
] as WorkbookData;

const multiWorkbookData = [
  [`worksheet-${nanoid()}`, sampleRiskCountData],
  [`worksheet-${nanoid()}`, sampleRiskCountData],
  [`worksheet-${nanoid()}`, sampleRiskCountData],
  [`worksheet-${nanoid()}`, sampleRiskCountData],
] as WorkbookData;

const Template: ComponentStory<typeof FileDownloadDropdown> = args => (
  <FileDownloadDropdown {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  data: singleWorkbookData,
};

export const WithSingleDownload = Template.bind({});
WithSingleDownload.args = {
  data: singleWorkbookData,
};

export const WithMultipleDownload = Template.bind({});
WithMultipleDownload.args = {
  data: multiWorkbookData,
};
